"""
    Class to give access to the config file
"""

import os
import json

# Path to config file
DEFAULT_CONFIG_FILE = os.path.join('/root','.config','gis_packer.json')

# Config keys
AWS_ACCESS_ID_KEY = 'AWS_ACCESS_ID'
AWS_ACCESS_SECRET_KEY = 'AWS_ACCESS_SECRET'
AWS_REGION_KEY = 'AWS_REGION'
DB_USERNAME_KEY = 'DB_USERNAME'
DB_PASSWORD_KEY = 'DB_PASSWORD'
DB_HOSTNAME_KEY = 'DB_HOSTNAME'
DB_PORT_KEY = 'DB_PORT'
DB_NAME_KEY = 'DB_NAME'

ALLOWED_KEYS = set([
    AWS_ACCESS_ID_KEY,
    AWS_ACCESS_SECRET_KEY,
    AWS_REGION_KEY,
    DB_USERNAME_KEY,
    DB_PASSWORD_KEY,
    DB_HOSTNAME_KEY,
    DB_PORT_KEY,
    DB_NAME_KEY
])


__config = None
def load_config(config_file_path=None):
    global __config

    if __config is not None:
        raise Exception(f'config has already been loaded from {__config.config_file_path}')

    if config_file_path is None:
        # write to default location
        __config = gisPackerConfig(DEFAULT_CONFIG_FILE)

    else:
        # write to user provided location
        __config = gisPackerConfig(config_file_path)

    return __config


def get_config():
    global __config

    if __config is None:
        __config = load_config()

    return __config


def create_template_config_file(config_file_path=None):
    """
        Init config template and save to disk at user provided path
    """
    d = {k:'' for k in ALLOWED_KEYS}
    d = json.dumps(d)

    if config_file_path is None:
        open(DEFAULT_CONFIG_FILE,'w').write(d)
    else:
        open(config_file_path,'w').write(d)



class gisPackerConfig:

    def __init__(self, config_file_path):

        self.config_file_path = config_file_path

        with open(config_file_path,'r') as fh:
            self._config = json.load(fh)


    def __getitem__(self, key):
        if key not in self._config:
            raise Exception(f'{key} not in config file')
        return self._config[key]


    def __setitem__(self, key, value):
        if key not in self._config:
            raise Exception(f'{key} not in config file')

        if value is None:
            raise Exception(f'value is none')

        self._config[key] = value


    def list_keys(self):
        return list(ALLOWED_KEYS)


    def is_on_disk(self):
        return os.path.exists(self.config_file_path)


    def save(self):
        d = json.dumps(self._config)
        open(self.config_file_path,'w').write(d)


    def delete(self):
        if self.is_on_disk():
            os.remove(self.config_file_path)
        else:
            raise Exception('Could not delete config file')


    def is_valid(self):
        """
            Makes sure all the allowed keys are in the config file
        """
        for k in ALLOWED_KEYS:
            try:
                _ = self._config[k]
            except:
                return False

        return True

    def is_configured(self):
        """
            Makes sure all the allowed keys are in the config file and checks that the values are set
        """

        for k in ALLOWED_KEYS:
            try:
                val = self._config[k]
                if val is None or val == '':
                    return False
            except:
                return False

        return True
