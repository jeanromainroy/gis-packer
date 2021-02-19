import unittest

import os
import shutil
import json
from glob import glob

# import gis packer
from gis_packer.database import get_database
from gis_packer.utils.basic import get_iso_timestamp

# get an instance of the database
database = get_database()

class TestFuncs(unittest.TestCase):

    def test_execute_query(self):
        database.execute_query('SELECT * FROM raster LIMIT 2')

    def test_insert_select_delete(self):

        # delete
        database.delete('bucket_name', 'file_key')

        # generate an iso timestamp
        now = get_iso_timestamp()

        # insert a raster
        database.insert(now, 'bucket_name', 'file_key', 10, 'POLYGON((45 45, 45.2 45, 45.2 45.2, 45 45.2, 45 45))', {}, {})

        # select
        res = database.select(TAKEN_AT_MIN=now)
        assert len(res.index) == 1

        # delete
        database.delete('bucket_name', 'file_key')

if __name__ == '__main__':
    unittest.main()
