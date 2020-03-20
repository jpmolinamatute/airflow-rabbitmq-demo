#!/usr/bin/env bash

build="$1"
: "${build:=all}"

if [[ $build == 'all' || $build == 'init' ]]; then
    echo
    echo
    echo "Building init image"
    if ! docker build --rm -f ./init/Dockerfile -t 344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelog-init:v1 .; then
        echo "Error: Building init image failed" >&2
        exit 2
    fi
    echo
    echo
fi

if [[ $build == 'all' || $build == 'decrypt' ]]; then
    echo
    echo
    echo "Building decrypt image"

    if ! docker build --rm -f ./decrypt/Dockerfile -t 344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelog-init:v1 .; then
        echo "Error: Building init image failed" >&2
        exit 2
    fi
    echo
    echo
    # docker run --rm --name deleteme -it --entrypoint sh --env-file ./Environments 344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelog-init:v1
fi
exit 0
