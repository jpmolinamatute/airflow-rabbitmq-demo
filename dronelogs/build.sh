#!/usr/bin/env bash

image="$1"
: "${image:=all}"
push="$2"
script_path=$(dirname "$(readlink -f "$0")")

list=("init" "decrypt")

build() {
    local localimage="$1"
    local tag="344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelogs:$localimage"

    echo "Building $localimage image"
    if ! docker build --rm -f ./"$localimage"/Dockerfile -t "$tag" .; then
        echo "Error: Building $localimage image failed" >&2
        exit 2
    fi
}

push() {
    local localimage="$1"
    local tag="344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelogs:$localimage"
    echo "Pushing $localimage image"
    if ! docker push "$tag"; then
        echo "Error: Pushing $localimage image failed" >&2
        exit 2
    fi
}

cd "$script_path" || exit 2

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
fi

exit 0
