#!/usr/bin/env bash

THISSCRIPT="$(basename "$0")"
BASE_PATH="$(dirname "$(readlink -f "$0")")"
BASE_DIR="$(basename "$BASE_PATH")"
ERROR_MESSAGE=""
USERLIST=()
SYSTEMLIST=()
WORDLEN=2
REGISTRY=""
RESULT=""
PUSH=""
PIPELELINE_NAME=""
SUCCESS="\e[32m\xE2\x9C\x94\e[0m"
FAILED="\e[31m\u2717\e[0m"

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
    local returnValue=0
    echo "Building $localimage image"
    if ! docker build --rm -f "${BASE_PATH}/$localimage/Dockerfile" -t "$tag" --build-arg "SRC_DIR=${BASE_DIR}" --build-arg "IMAGE_NAME=${localimage}" --build-arg "USER=airflow" .; then
        ERROR_MESSAGE="${ERROR_MESSAGE}Error: Building $localimage image failed\n"
        returnValue=2
    fi
    return $returnValue
}

push() {
    local localimage="$1"
    local tag="${REGISTRY}:${localimage}"
    local returnValue=0
    echo "Pushing $localimage image"

    if ! docker push "$tag"; then
        if aws ecr get-login-password | docker login --username AWS --password-stdin "${AWS_ACCOUNT_NO}.dkr.ecr.us-east-2.amazonaws.com"; then
            if ! docker push "$tag"; then
                ERROR_MESSAGE="${ERROR_MESSAGE}Error: Pushing $localimage image failed\n"
                returnValue=2
            fi
        else
            ERROR_MESSAGE="${ERROR_MESSAGE}Error: We couldn't log you into AWS ECR\n"
            returnValue=2
        fi
    fi
    return $returnValue
}

processimage() {
    local localimage="$1"
    local firstcolumn
    local build_icon
    local push_icon
    firstcolumn="$(getcolumn "$WORDLEN" "$localimage")"

    if build "$localimage"; then
        build_icon=$SUCCESS
    else
        build_icon=$FAILED
    fi
    RESULT="${RESULT}${firstcolumn}  ${build_icon}"
    if [[ -n $PUSH ]]; then
        if push "$localimage"; then
            push_icon=$SUCCESS
        else
            push_icon=$FAILED
        fi
        RESULT="${RESULT}          ${push_icon}\n"
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

checkpipeline() {
    if [[ -n $PIPELELINE_NAME ]]; then
        if [[ ! -d ${BASE_PATH}/${PIPELELINE_NAME} ]]; then
            echo "Error: ${BASE_PATH}/${PIPELELINE_NAME} is a invalid directory" >&2
            exit 2
        fi
    else
        echo "Error: PIPELELINE_NAME is undefined" >&2
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
    echo
    if [[ -n $ERROR_MESSAGE ]]; then
        echo -e "\e[31m$ERROR_MESSAGE\e[0m" >&2
        exit 2
    fi
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
            PIPELELINE_NAME="$1"
            shift
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
