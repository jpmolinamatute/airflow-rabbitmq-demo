#!/usr/bin/env bash

base_path=$(dirname "$(readlink -f "$0")")
BASE_DIR=$(basename "$base_path")
REGISTRY="344286188962.dkr.ecr.us-east-2.amazonaws.com/pipeline/${BASE_DIR}"

image="$1"
: "${image:=all}"
push="$2"

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
    if ! docker build --rm -f "${base_path}/$localimage/Dockerfile" -t "$tag" --build-arg "SRC_DIR=${BASE_DIR}" .; then
        echo "Error: Building $localimage image failed" >&2
        exit 2
    fi
}

push() {
    local localimage="$1"
    local tag="${REGISTRY}:${localimage}"
    echo "Pushing $localimage image"
    if ! docker push "$tag"; then
        echo "Error: Pushing $localimage image failed" >&2
        exit 2
    fi
}

cd "$base_path" || exit 2

list=()
wordlen=2
# @INFO: loop through all directories looking for Dockerfile file and then append it to list array
for singleimage in */; do
    # @INFO: at this point $singleimage contains a trailing / so we don't need to add an extra one for next line
    if [[ -f ${singleimage}Dockerfile ]]; then
        singleimage="${singleimage%/}"
        if [[ ${#singleimage} -gt $wordlen ]]; then
            wordlen="${#singleimage}"
        fi
        list=("$singleimage" "${list[@]}")
    fi
done

result=""

if [[ $image == "all" ]]; then
    for singleimage in "${list[@]}"; do
        build "$singleimage"
        firstcolumn="$(getcolumn "$wordlen" "$singleimage")"
        result="${result}${firstcolumn}  X"
        if [[ -n $push ]]; then
            push "$singleimage"
            result="${result}          X"
        fi
        result="${result}\n"
    done
elif [[ ${list[*]} =~ $image ]]; then
    build "$image"
    firstcolumn="$(getcolumn "$wordlen" "$image")"
    result="${result}${firstcolumn}  X"
    if [[ -n $push ]]; then
        push "$image"
        result="${result}          X"
    fi
else
    echo "Error: image name '${image}' doesn't exist" >&2
    exit 2
fi

echo "Image        built     pushed"
echo "============================="
echo -e "${result}"
echo "============================="
echo
exit 0
