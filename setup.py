import os
import sys
import re
import setuptools
from setuptools import find_packages

def get_version():
    """
        Returns the package version declared in the __init__.py file
    """
    VERSIONFILE = os.path.join('gis_packer', '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt').readlines()
    VSRE = r'^__version__ = [\"\']*([\d\w.]+)[\"\']'
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError(f'Unable to find version string in {VERSIONFILE}')


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gis_packer",
    description="ETL tool for raster",
    version=get_version(),
    author="Jean-Romain Roy",
    author_email="jroy@gisaerobot.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gis-Aerobot/gis-packer",
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: proprietary and confidential",
        "Operating System :: UNIX",
    ],
    install_requires=[
        'click',
        'humanize',
        'tqdm',
        'psycopg2',
        'sqlalchemy',
        'numpy',
        'matplotlib',
        'pandas',
        'shapely',
        'boto3',
        'geopandas',
        'rasterio',
        'toolz',
        'dask',
        'xarray'
    ],
    python_requires='>=3.6',
)