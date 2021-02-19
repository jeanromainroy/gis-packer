# gis Packer

gis Packer is an ETL CLI tool for geospatial raster.

To mention some of its features :

- Raster search tool where attributes such as cloud coverage, taken_at, bands, resolution, nadir, sun angle can be filtered

- Raster visualization tool

- Raster compression, reprojection, unstack band, ...

- Tiling large-format raster and vector labels


## Requirements

 - Linux Host Machine with Docker installed

 - PostgreSQL (>=11) database with the [PostGIS extension](https://postgis.net/) configured*

 - AWS Account with a S3 bucket to store raster

 - At least 4 GB of disk space

 - At least 4 GB of RAM

*To setup the PostGIS extension on AWS RDS, here is an [article](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.html#Appendix.PostgreSQL.CommonDBATasks.PostGIS)*


## Installation

gis Packer runs inside a Docker Container. Here is the installation procedure,

1. Make sure to have the following information at your disposal

        - AWS_ACCESS_ID
        - AWS_ACCESS_SECRET
        - AWS_REGION
        - DB_USERNAME
        - DB_PASSWORD
        - DB_HOSTNAME
        - DB_PORT
        - DB_NAME

2. cd into the *docker/* folder

3. Make the build.sh script executable

        chmod +x build.sh

4. Execute the build.sh script

        ./build.sh

5. You can then use the command line,

        gis_packer {your-command}


*The config file is stored in $HOME/.config/gis_packer.json*


## Upgrading

Here is how to upgrade your gis Packer tool.

1. Pull the most recent version of gis-packer

        git pull

2. cd into the *docker/* folder

        cd docker

3. Rebuild the docker image

        ./build.sh

4. Optional : You can run the following command to run all the unit tests

        gis_packer autotest


## Documentation

The documentation is available as a locally hosted web app.

1. In your command line run,

        gis_packer documentation

2. Open your browser and type,

        localhost:8888

3. You can then navigate the documentation


## Tutorials

A tutorial in the form of a jupyter notebook is available to see how to use gis packer.

1. In your command line run,

        gis_packer tutorials

2. Copy the secret token from the command line

3. Open your browser and type,

        localhost:8888

4. Paste the token

5. You can then open any of the tutorial notebooks.

**IMPORTANT: None of your work will be saved in this environment**


## API

{"intersects":{"type":"Polygon","coordinates":[[[13.19079905833712,52.25136228575683],[13.581509291272255,52.25136228575683],[13.581154422092254,52.73110575596653],[13.19115392751712,52.73110575596653],[13.19079905833712,52.25136228575683]]]},"limit":50,"query":{"cloudCoverage":{"lte":65},"dataBlock":{"in":["oneatlas-pleiades-fullscene","oneatlas-pleiades-aoiclipped"]}},"datetime":"2012-05-09T00:00:00.000Z/2020-12-02T00:00:00.000Z"}

{"intersects":{"type":"Polygon","coordinates":[[[13.19079905833712,52.25136228575683],[13.581509291272255,52.25136228575683],[13.581154422092254,52.73110575596653],[13.19115392751712,52.73110575596653],[13.19079905833712,52.25136228575683]]]},"limit":50,"query":{"cloudCoverage":{"lte":65},"dataBlock":{"in":["oneatlas-pleiades-fullscene","oneatlas-pleiades-aoiclipped","sobloo-s2-l1c-fullscene","sobloo-s2-l1c-aoiclipped"]}},"datetime":"2012-05-09T00:00:00.000Z/2020-12-02T00:00:00.000Z"}


## PySpark

0. Install the basics

        sudo apt-get update
        sudo apt-get upgrade

        sudo apt-get python3-pip


1. Install java >=8

2. Download the latest version of [Apache Spark](https://spark.apache.org/downloads.html) (e.g. Pre-built for Apache Hadoop 3.2 and later)

3. Unzip & Move it

        tar -xzf spark-3.1.0-bin-hadoop3.2

        mv spark-3.1.0-bin-hadoop3.2 /opt/spark-3.1.0

4. Symbolic

        ln -s /opt/spark-3.1.0 /opt/spark

5. Edit your bash

        nano ~/.bashrc

        # Spark path
        export SPARK_HOME=/opt/spark
        export PATH=$SPARK_HOME/bin:$PATH
        export PYSPARK_PYTHON=python3
        export PYSPARK_DRIVER_PYTHON="jupyter"
        export PYSPARK_DRIVER_PYTHON_OPTS="lab"


6. source

        source ~/.bashrc


7. Generate config for jupyter lab

        jupyter lab --generate-config


8. edit the config

        nano ~/.jupyter/jupyter_notebook_config.py

        c.NotebookApp.ip = '0.0.0.0'
        c.LabApp.allow_origin = '*'

9.
