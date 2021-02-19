import sys
import os
import boto3

import numpy as np
import pandas as pd
import geopandas as gpd

# config file interface
from ..config import get_config, AWS_ACCESS_ID_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_KEY


__cloudstorage = None
def get_cloudstorage():
    global __cloudstorage

    if __cloudstorage is None:
        __cloudstorage = CloudStorage()

    return __cloudstorage


class CloudStorage:
    """
        Class to interact with our AWS S3 cloud storage
    """

    def __init__(self):

        # grab config
        config = get_config()
        AWS_ACCESS_ID = config[AWS_ACCESS_ID_KEY]
        AWS_ACCESS_SECRET = config[AWS_ACCESS_SECRET_KEY]
        AWS_REGION = config[AWS_REGION_KEY]

        # runtime var
        self._downloaded = 0
        self._uploaded = 0

        # init s3 bucket
        self._cloudstorage = boto3.client(
            's3',
            aws_access_key_id = AWS_ACCESS_ID,
            aws_secret_access_key = AWS_ACCESS_SECRET,
            region_name = AWS_REGION,
        )


    def validate_input(self, bucket_name, file_key):
        """ Checks the bucket name and file key input """
        if bucket_name is None or file_key is None or not isinstance(bucket_name, str) or not isinstance(file_key, str) or bucket_name == '' or file_key == '':
            raise Exception('invalid input')


    def does_file_exists_in_cloudstorage(self, bucket_name, file_key):
        """ Checks if file exists in the cloudstorage

        Arguments
        ---------
        bucket_name : str
            Name of the AWS S3 bucket
        file_key : str
            Key of the file

        Returns
        -------
        success : bool
            Returns true if the file exists
        """

        # validate input
        self.validate_input(bucket_name, file_key)

        # init
        filesize = None

        # check if file already exists in the bucket
        try:
            filesize = self._cloudstorage.head_object(
                Bucket=bucket_name,
                Key=file_key
            ).get('ContentLength', 0)

        except:
            return False

        return isinstance(filesize, int)


    def get(self, bucket_name, file_key, out_path):
        """Downloads a file on the host machine

        Arguments
        ---------
        bucket_name : str
            Name of the AWS S3 bucket
        file_key : str
            Key of the file
        out_path : str
            Path where to save the file
        """

        # validate input
        self.validate_input(bucket_name, file_key)

        # reset
        self._downloaded = 0

        # check if we already have this file
        if os.path.exists(out_path):
            raise Exception('File already in local storage')

        # check if the file exists in the cloudstorage
        if not self.does_file_exists_in_cloudstorage(bucket_name, file_key):
            raise Exception('File does not exists in the cloudstorage')

        # grab file size
        filesize = self._cloudstorage.head_object(
            Bucket=bucket_name,
            Key=file_key
        ).get('ContentLength', 0)

        # init progress func
        def progress(chunk):
            self._downloaded += chunk
            done = int(50 * self._downloaded / filesize)
            bytes_done = f'{round((self._downloaded)/(1024.0*1024.0), 2)}/{round((filesize)/(1024.0*1024.0), 2)} mb'
            sys.stdout.write("\r[%s%s] %s" % ('=' * done, ' ' * (50-done), bytes_done))
            sys.stdout.flush()

        # save file to root dir
        with open(out_path, 'wb') as fh:
            self._cloudstorage.download_fileobj(
                bucket_name,
                file_key,
                fh,
                Callback=progress
            )

        # skip line
        print('\n')


    def post(self, bucket_name, file_key, src_path):
        """Uploads a file from the host machine to the cloudstorage

        Arguments
        ---------
        bucket_name : str
            Name of the AWS S3 bucket we want to upload to
        file_key : str
            Key we want to give to the file
        src_path : str
            Path to the file we want to upload
        """

        # validate input
        self.validate_input(bucket_name, file_key)

        # validate input
        if src_path is None or src_path == '':
            raise Exception('Invalid file path')

        # check if on disk
        if not os.path.exists(src_path):
            raise Exception(f'File not found at {src_path}')

        # reset
        self._uploaded = 0

        # grab file size in bytes
        filesize = os.path.getsize(src_path)

        # check if the file exists in the cloudstorage
        if self.does_file_exists_in_cloudstorage(bucket_name, file_key):
            raise Exception('File already exists in the cloudstorage')

        # init progress func
        def progress(chunk):
            self._uploaded += chunk
            done = int(50 * self._uploaded / filesize)
            bytes_done = f'{round((self._uploaded)/(1024.0*1024.0), 2)}/{round((filesize)/(1024.0*1024.0), 2)} mb'
            sys.stdout.write("\r[%s%s] %s" % ('=' * done, ' ' * (50-done), bytes_done))
            sys.stdout.flush()

        # save file to root dir
        self._cloudstorage.upload_file(
            src_path,
            bucket_name,
            file_key,
            Callback=progress
        )

        # skip line
        print('\n')


    def delete(self, bucket_name, file_key):
        """Deletes a file from the S3 bucket

        Arguments
        ---------
        bucket_name : str
            Name of the AWS S3 bucket
        file_key : str
            Key of the file
        """

        # validate input
        self.validate_input(bucket_name, file_key)

        # check if the file exists in the cloudstorage
        if not self.does_file_exists_in_cloudstorage(bucket_name, file_key):
            raise Exception('File does not exists in the cloudstorage')

        # save file to root dir
        self._cloudstorage.delete_object(
            Bucket=bucket_name,
            Key=file_key
        )
