"""
    Class for interfacing with packages
"""

import os.path
import logging
logger = logging.getLogger(os.path.basename(__name__))

# utils
#from gis_packer.utils import get_timestamp

# constants
PUBLISHED_FLAG_FILE = '.published'

class Package:

    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __repr__(self):
        return f'{self.name}-{self.version}'


class LocalPackage(Package):

    def __init__(self, name, version, root_dir):
        Package.__init__(self, name, version)

        self.root_dir = root_dir


    def is_published(self):
        return os.path.exists(os.path.join(self.root_dir,PUBLISHED_FLAG_FILE))


    def publish(self, server):
        if self.is_published():
            raise Exception(f'cannot publish package {self} - already published')

        if server.inner_publish(self):
            # create the published flag if it was done successfully
            open(os.path.join(self.root_dir,PUBLISHED_FLAG_FILE),'w')

        # DONE


    def exists(self):
        return os.path.exists(self.root_dir)
