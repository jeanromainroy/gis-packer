import unittest

import os
import shutil
import json
from glob import glob

# import gis packer
from gis_packer.utils.raster import info, show, create_tiles, unstack_bands, compress, to_uint8, reproject

# PATHS
single_band_path = '/gis-packer/tests/assets/single_band.tif'
three_band_path = '/gis-packer/tests/assets/three_band.tif'
temp_dir = '/gis-packer/tests/assets/temp/'

# create temp folder if not already there
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)

class TestFuncs(unittest.TestCase):

    def test_info(self):
        info(single_band_path)
        print('\n\n')
        info(three_band_path)

    def test_unstack_bands(self):
        out_paths = unstack_bands(three_band_path, temp_dir)
        assert len(out_paths) == 3

    def test_compress(self):
        compress(three_band_path, os.path.join(temp_dir, 'compressed.tif'))

    def test_to_uint8(self):
        to_uint8(three_band_path, os.path.join(temp_dir, 'uint8.tif'))

    def test_reproject(self):
        reproject(single_band_path, os.path.join(temp_dir, 'reprojected.tif'), target_crs='4326')

    def test_tile(self):
        create_tiles(three_band_path, temp_dir, tile_overlap=0.6, tile_size_in_pixels=(100,400))


if __name__ == '__main__':
    unittest.main()
