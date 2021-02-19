#!/bin/bash

# PARAMETERS
docker_image_tag="gispacker"
docker_image_version="v1.0"

# Copy gis_packer to a temp folder inside of this context
mkdir temp
cp -r ../gis_packer ./temp/
cp ../setup.py ./temp/
cp ../README.md ./temp/
cp ../LICENSE ./temp/
cp -r ../tutorials ./temp/
cp -r ../tests ./temp/
cp -r ../docs ./temp/
cd ./temp
find . -type d -name "__pycache__" -exec rm -rf {} +
cd $OLDPWD

# Build Docker Image
sudo docker build . -t "${docker_image_tag}:${docker_image_version}"

# Remove temp
rm -rf ./temp/

# Create the directory gis_packer will use on the host
mkdir -p $HOME/gis_packer/

# Make the gis_packer package inside the docker container accessible
# through the 'gis_packer' cli shortcut on the host
chmod +x run.sh
sudo cp run.sh /usr/local/bin/gis_packer
