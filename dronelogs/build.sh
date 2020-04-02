#!/usr/bin/env bash

image="$1"
: "${image:=all}"
push="$2"
script_path=$(dirname "$(readlink -f "$0")")
registry="344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelogs"

build() {
    local localimage="$1"
    local tag="${registry}:${localimage}"

    echo "Building $localimage image"
    if ! docker build --rm -f ./"$localimage"/Dockerfile -t "$tag" .; then
        echo "Error: Building $localimage image failed" >&2
        exit 2
    fi
}

push() {
    local localimage="$1"
    local tag="${registry}:${localimage}"
    echo "Pushing $localimage image"
    if ! docker push "$tag"; then
        echo "Error: Pushing $localimage image failed" >&2
        exit 2
    fi
}

cd "$script_path" || exit 2

list=()
# @INFO: loop through all directories looking for Dockerfile file and then append it to list array
for singleimage in */; do
    # @INFO: at this point $singleimage contains a trailing / so we don't need to add an extra one for next line
    if [[ -f ${singleimage}Dockerfile ]]; then
        singleimage="${singleimage%/}"
        list=("$singleimage" "${list[@]}")
    fi
done

if [[ $image == "all" ]]; then
    for singleimage in "${list[@]}"; do
        build "$singleimage"
        if [[ -n $push ]]; then
            push "$singleimage"
        fi
    done
elif [[ ${list[*]} =~ $image ]]; then
    build "$image"
    if [[ -n $push ]]; then
        push "$image"
    fi
else
    echo "Error: image name '${image}' doesn't exist" >&2
    exit 2
fi

exit 0
