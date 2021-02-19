import unittest

import os
import shutil
import json
from glob import glob

# import gis packer
from gis_packer.cloudstorage import get_cloudstorage

# PATHS
three_band_path = '/gis-packer/tests/assets/three_band.tif'
temp_dir = '/gis-packer/tests/assets/temp/'
temp_out_path = '/gis-packer/tests/assets/temp/downloaded_image.tif'

# Test Bucket Params
bucket_name = 'tests-gis'

# create temp folder if not already there
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)

# get an instance of the cloudstorage
cloudstorage = get_cloudstorage()

class TestFuncs(unittest.TestCase):

    def test_post_get(self):

        # define a file_key
        file_key = 'test_post.tif'

        # check if test file already exists in bucket
        if cloudstorage.does_file_exists_in_cloudstorage(bucket_name, file_key):
            cloudstorage.delete(bucket_name, file_key)

        # upload image
        cloudstorage.post(bucket_name, file_key, three_band_path)

        # check existance
        res = cloudstorage.does_file_exists_in_cloudstorage(bucket_name, file_key)
        assert res == True

        # download
        cloudstorage.get(bucket_name, file_key, temp_out_path)

        # check existance
        assert os.path.exists(temp_out_path)

        # delete
        cloudstorage.delete(bucket_name, file_key)
        assert not cloudstorage.does_file_exists_in_cloudstorage(bucket_name, file_key)


if __name__ == '__main__':
    unittest.main()
