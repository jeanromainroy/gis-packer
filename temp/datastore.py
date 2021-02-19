"""
    Class for providing access to the local datastore
"""
import os, os.path

# config file interface
from gis_packer.config import get_config, LOCAL_STORE_DIR_PATH_KEY

# package interface
from gis_packer.package import LocalPackage

# utils
#from gis_packer.utils import get_timestamp


__datastore = None
def get_datastore():
    global __datastore

    if __datastore is None:
        __datastore = DataStore()

    return __datastore


class DataStore:

    def __init__(self, root_dir=None):

        # set the root dir of the data store
        if root_dir is None:

            # if it's missing, then load from the config
            self.root_dir = get_config()[LOCAL_STORE_DIR_PATH_KEY]

        else:
            self.root_dir = root_dir

        # check if the root exists
        if not os.path.isdir(self.root_dir):
            raise Exception(f'Data store path is invalid at {self.root_dir}')


    def get_package_dir(self, name, version):
        return os.path.join(self.root_dir,name,version)


    def create_package(self,name):
        """
            Create a new package
        """
        version = str(get_timestamp())

        pkg_dir = self.get_package_dir(name,version)
        if os.path.exists(pkg_dir):
            raise Exception(f'package name={name}, version={version} already exists locally')

        # create the empty directory
        os.makedirs(pkg_dir)

        return LocalPackage(name, version, pkg_dir)


    def package_list(self):
        """
            Return a list of LocalPackage objects that represent all the
            packages in the local store.
        """
        packages = []
        package_names = filter(lambda x: not x.startswith('.'), os.listdir(self.root_dir))

        for pn in package_names:
            name_path = os.path.join(self.root_dir,pn)

            # list out the versions
            versions = filter(lambda x: not x.startswith('.'), os.listdir(name_path))
            for v in versions:
                pack_path = os.path.join(name_path,v)
                packages.append(LocalPackage(pn,v,pack_path))

        return packages


    def get_package(self,name,version):
        for pkg in self.package_list():
            if pkg.name == name and pkg.version == version:
                return pkg

        return None
