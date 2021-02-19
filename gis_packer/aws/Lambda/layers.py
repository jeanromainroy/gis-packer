import sys
import os
import shutil
import boto3

from ...cloudstorage import get_cloudstorage


def create(req_path, out_path, bucket_name=None, file_key=None, TAG='gis-lambda-layer', VERSION='latest'):
    """Creates a lambda layer and uploads it to AWS S3

    Arguments
    ---------
        req_path : str
            Path to the requirements.txt file containing all the desired python libraries
        out_path : str
            Path on the host machine where to save the lambda layer
        bucket_name : str
            Name of the AWS S3 bucket
        file_key : str
            File key in the S3 bucket
    """

    # check if can write to output path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Output path is invalid')

    os.system(f"""
        cd /gis-packer/gis_packer/aws/Lambda/docker/ &&
        cp {req_path} ./requirements.txt &&
        docker build --tag={TAG}:{VERSION} . &&
        docker run --rm -it \
            -v /home:/home \
            {TAG}:{VERSION} cp /packages/lambda-layer.zip {out_path}
    """)

    # check if the zip file was created
    if not os.path.exists(out_path):
        raise Exception('Could not build lambda layer')

    # check if it's not too large (AWS Lambda limits layers to a maximum of 50mb)
    filesize_b = os.path.getsize(out_path)
    filesize_mb = int(filesize_b/float(1024*1024))
    if filesize_mb > 53:
        raise Exception(f'The file size of the Lambda layer is too big ({filesize_mb} mb), remove some libs')

    # upload to aws
    if bucket_name is not None and file_key is not None:
        cloudstorage = get_cloudstorage()
        cloudstorage.post(bucket_name, file_key, out_path)
