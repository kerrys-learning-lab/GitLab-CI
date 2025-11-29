#! /usr/bin/env bash

docker run  --rm \
            --interactive \
            --tty \
            --privileged \
            --env-file test/gitlab-test/data/.env \
            --volume $(pwd):/workspace \
            --volume $(pwd)/src:/opt/gitlab-ci \
            --volume /var/run/docker.sock:/var/run/docker.sock \
            --workdir /workspace \
            localhost/gitlab-ci:main --verbose build image --engine  docker \
                                                          --save    /workspace/images \
                                                          --save-manifest

