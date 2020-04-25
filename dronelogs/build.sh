#!/usr/bin/env bash

THISSCRIPT="$(basename "$0")"
BASE_PATH="$(dirname "$(readlink -f "$0")")"
USERLIST=()
SYSTEMLIST=()
WORDLEN=2
BASE_DIR="$(basename "$BASE_PATH")"
REGISTRY=""
RESULT=""
PUSH=""

getcolumn() {
    local len="$1"
    local word="$2"
    len=$((len + 5))
    printf -v y %-${len}.${len}s "$word"
    echo "$y"
}

build() {
    local localimage="$1"
    local tag="${REGISTRY}:${localimage}"

    echo "Building $localimage image"
    if ! docker build --rm -f "${BASE_PATH}/$localimage/Dockerfile" -t "$tag" --build-arg "SRC_DIR=${BASE_DIR}" --build-arg "IMAGE_NAME=${localimage}" .; then
        echo
        echo
        echo "Error: Building $localimage image failed" >&2
        exit 2
    fi
}

push() {
    local localimage="$1"
    local tag="${REGISTRY}:${localimage}"
    echo "Pushing $localimage image"
    if ! docker push "$tag"; then
        echo
        echo
        echo "Error: Pushing $localimage image failed" >&2
        exit 2
    fi
}

processimage() {
    local localimage="$1"
    local firstcolumn
    firstcolumn="$(getcolumn "$WORDLEN" "$localimage")"

    build "$localimage"
    RESULT="${RESULT}${firstcolumn}  X"
    if [[ -n $PUSH ]]; then
        push "$localimage"
        RESULT="${RESULT}          X\n"
    else
        RESULT="${RESULT}\n"
    fi
}

setregistry() {
    if [[ -f ${BASE_PATH}/ACCOUNTNO && -z $AWS_ACCOUNT_NO ]]; then
        . "${BASE_PATH}/ACCOUNTNO"
    fi
    if [[ -n $AWS_ACCOUNT_NO ]]; then
        export REGISTRY="${AWS_ACCOUNT_NO}.dkr.ecr.us-east-2.amazonaws.com/pipeline/${BASE_DIR}"
    else
        echo "Error: AWS Account Number not provided" >&2
        exit 2
    fi
}

getsystemlist() {
    # @INFO: loop through all directories looking for Dockerfile file and then append it to list array
    for singleimage in */; do
        # @INFO: at this point $singleimage contains a trailing / so we don't need to add an extra one for next line
        if [[ -f ${singleimage}Dockerfile ]]; then
            singleimage="${singleimage%/}"
            if [[ ${#singleimage} -gt $WORDLEN ]]; then
                WORDLEN="${#singleimage}"
            fi
            SYSTEMLIST=("$singleimage" "${SYSTEMLIST[@]}")
        fi
    done
}

displayhelp() {
    cat <<-EOF
    Usage: $THISSCRIPT [options] image1 image2 image3..

    Options:
    --help                  : This output.
    --pipeline              : Name of the pipeline or project (Required)
    --account               : AWS Account number to build and push docker images
                              (Required if ${BASE_PATH}/ACCOUNTNO file doesn't exist)
    --push                  : Push image to registry after build (optional)
EOF
    exit 0
}

displayresult() {
    RESULT="${RESULT::-2}"
    echo
    echo
    echo "Image        built     pushed"
    echo "============================="
    echo -e "${RESULT}"
    echo "============================="
    echo
}

main() {
    local systemimage
    local userimage

    if [[ ${#USERLIST[@]} -eq 0 ]]; then
        for systemimage in "${SYSTEMLIST[@]}"; do
            processimage "$systemimage"
        done
    else
        for userimage in "${USERLIST[@]}"; do
            if [[ ${SYSTEMLIST[*]} =~ $userimage ]]; then
                processimage "$userimage"
            fi
        done
    fi
}
getUserInput() {
    # if [[ $# -eq 0 ]]; then
    #     echo "Error: please provide required arguments" >&2
    #     exit 2
    # fi

    while [[ $# -gt 0 ]]; do
        case "$1" in
        "--help")
            displayhelp
            ;;
        "--account")
            shift
            AWS_ACCOUNT_NO="$1"
            shift
            ;;
        "--pipeline")
            shift
            DOWNLOAD=1
            ;;
        "--push")
            shift
            PUSH="push"
            ;;
        *)
            USERLIST=("$1" "${USERLIST[@]}")
            shift
            ;;
        esac
    done
}

cd "$BASE_PATH" || exit 2

getUserInput "$@"
getsystemlist
setregistry
main
displayresult

exit 0
