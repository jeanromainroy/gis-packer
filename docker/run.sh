#!/bin/bash

# PARAMETERS
docker_image_tag="gispacker"
docker_image_version="v1.0"

# Run a command
sudo docker run --rm -it --name=gis_packer \
        -p 8888:8888 \
        -v /var/run/docker.sock:/var/run/docker.sock \
        --mount type=bind,source="$HOME/.config",destination="/root/.config" \
        --mount type=bind,source="$HOME",destination="$HOME" \
        "${docker_image_tag}:${docker_image_version}" \
        python3 -m gis_packer.cli $@
