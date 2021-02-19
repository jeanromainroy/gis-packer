FROM osgeo/gdal:ubuntu-small-latest

# update env
RUN apt-get update -y

# Install basic packages
RUN apt-get install -y \
            software-properties-common build-essential ca-certificates apt-utils \
            make cmake wget unzip tar gzip curl git nano pkg-config \
            libpq-dev libspatialindex-dev

# Install python tools
RUN apt-get install python3-dev python3-pip python3-wheel python3-sphinx -y
RUN apt-get upgrade python3-setuptools -y
RUN pip3 install --upgrade pip

# Install pip dependencies
RUN pip3 install click \
                 tqdm  \
                 humanize  \
                 psycopg2  \
                 sqlalchemy  \
                 numpy  \
                 opencv-python \
                 matplotlib  \
                 pandas  \
                 shapely  \
                 boto3  \
                 geopandas  \
                 rasterio  \
                 toolz  \
                 dask  \
                 xarray \
                 notebook \
                 jupyterlab \
                 rtree

# Install the documentation styling
RUN pip3 install sphinx_rtd_theme

# Install docker's command line
COPY --from=docker:stable-dind-rootless /usr/local/bin/docker /usr/local/bin/

# Copy gis_packer into image
WORKDIR /gis-packer/
COPY ./temp/ ./

# Install gis_packer
WORKDIR /gis-packer/
RUN python3 setup.py install

# Build the documentation
WORKDIR /gis-packer/docs/
RUN make clean
RUN make html

# Reset workdir
WORKDIR /

# open ports for jupyter
EXPOSE 8888

RUN ["/bin/bash"]
