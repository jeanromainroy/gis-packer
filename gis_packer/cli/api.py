import os

# Pretty print
import pprint
pp = pprint.PrettyPrinter(depth=4)

# config file interface
from ..config import get_config

# aws interface
from ..cloudstorage import get_cloudstorage

# database interface
from ..database import get_database

# raster helper
from ..utils.raster import to_uint8 as img_to_uint8
from ..utils.raster import compress as img_compress
from ..utils.raster import unstack_bands as img_unstack_bands
from ..utils.raster import stack_bands as img_stack_bands
from ..utils.raster import info as img_info
from ..utils.raster import create_tiles as img_create_tiles
from ..utils.raster import get_attributes
from ..utils.raster import reproject as img_reproject
from ..utils.raster import select_bands as img_select_bands
from ..utils.raster import bands_info

# basic funcs
from ..utils.basic import is_int

# http server
from ..httpserver import launch

# lambda helper
from ..aws.Lambda.layers import create as create_lambda_layer


def configure():
    """
        Sets the variables in the config file
    """

    # get config
    config = get_config()
    if config is None:
        raise Exception('Could not load config')

    # go through keys
    for k in config.list_keys():
        val = input(f'{k} [{config[k]}] : ')
        config[k] = val

    # save to disk
    config.save()


def notebook():
    """
        Launches a jupyter notebook runtime environment on port 8888
    """

    # launch jupyter through system
    os.system('jupyter notebook --allow-root --no-browser --ip=0.0.0.0 --port=8888')


def lab():
    """
        Launches a jupyter lab runtime environment on port 8888
    """

    # launch jupyter through system
    os.system('jupyter-lab --allow-root --no-browser --ip=0.0.0.0 --port=8888')


def tutorials():
    """
        Launches an ephemerous jupyter notebook runtime environment on port 8888 in the tutorials folder
    """

    # launch jupyter through system
    os.system('jupyter notebook --allow-root --no-browser --ip=0.0.0.0 --port=8888 --notebook-dir=/gis-packer/tutorials/')


def documentation():
    """
        Launches a web server exposing the documentation on port
    """

    launch('/gis-packer/docs/_build/html/')


def get_file(bucket_name, file_key, out_path):
    """Downloads a file from the an AWS S3 Bucket

    Arguments
    ----------
        bucket_name : str
            Name of the AWS S3 bucket
        file_key : str
            File key in the S3 bucket
        out_path : str
            Path where to save the downloaded file
    """

    # check input
    if out_path is None or out_path == '':
        raise Exception('Must provide a valid output path')

    # check if absolute
    if not os.path.isabs(out_path):
        raise Exception('Must be an absolute path')

    # grab cloud storage
    cloudstorage = get_cloudstorage()

    # get file
    cloudstorage.get(bucket_name, file_key, out_path)

    # inform user
    print(f'File downloaded successfully at {out_path}')


def post_file(bucket_name, file_key, file_path):
    """Uploads a file to the AWS S3 Bucket

    Arguments
    ----------
        bucket_name : str
            Name of the AWS S3 bucket
        file_key : str
            File key in the S3 bucket
        file_path : str
            Path of the file to upload
    """

    # check input
    if file_path is None or file_path == '':
        raise Exception('Must provide a valid file path')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')

    # grab cloud storage
    cloudstorage = get_cloudstorage()

    # grab database
    database = get_database()

    # get raster attributes dict
    attributes = get_attributes(file_path)

    # insert into db
    db_success = False
    try:
        database.insert(
            attributes['taken_at'],
            bucket_name,
            file_key,
            attributes['pixel_size_m'],
            attributes['geometry'],
            attributes['bands'],
            attributes['profile']
        )
        db_success = True
    except:
        pass

    if not db_success:
        raise Exception('Could not insert meta data into the database')

    # upload to aws
    upload_success = False
    try:
        cloudstorage.post(bucket_name, file_key, file_path)
        upload_success = True
    except:
        pass

    if not upload_success:

        db_success = False
        try:
            database.delete(bucket_name, file_key)
            db_success = True
        except:
            pass

        if db_success:
            raise Exception('Could not upload file, but was able to delete meta data from DB')
        else:
            raise Exception('Could not upload file and could not delete meta data from DB')

    # inform
    print('File uploaded successfully and meta data added to DB')


def info(file_path):
    """Prints the GIS info about the .tif file

    Arguments
    ----------
        file_path : str
            Path to .tif file
    """

    # validate input
    if file_path is None or file_path == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')

    # preview
    img_info(file_path)


def unstack_bands(file_path, out_dir):
    """Unstacks an image into its individual bands

    Arguments
    ----------
        file_path : str
            Path to the .tif file
        out_dir : str
            Path the the output directory where to save the individual bands
    """

    # validate input
    if file_path is None or file_path == '' or out_dir is None or out_dir == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_dir):
        raise Exception('Must be an absolute path')

    # convert
    _ = img_unstack_bands(file_path, out_dir)


def stack_bands(src_dir, out_path):
    """Stacks bands into a single raster

    Arguments
    ---------
        src_dir : str
            Path to source directory containing the single bands .tif files
        out_path : str
            Path to output .tif file
    """

    # validate input
    if src_dir is None or src_dir == '' or out_path is None or out_path == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(src_dir):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_path):
        raise Exception('Must be an absolute path')

    # run
    stack_bands(src_dir, out_path)


def to_uint8(file_path, out_path):
    """Converts the pixels of an image to the uint8 format

    Arguments
    ----------
        file_path : str
            Path to the .tif file
        out_path : str
            Path to output the .tif file
    """

    # validate input
    if file_path is None or file_path == '' or out_path is None or out_path == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_path):
        raise Exception('Must be an absolute path')

    # convert
    img_to_uint8(file_path, out_path)


def compress(file_path, out_path):
    """Compresses an image to a lossy format

    Arguments
    ----------
        file_path : str
            Path to the .tif file
        out_path : str
            Path to output the .tif file
    """

    # validate input
    if file_path is None or file_path == '' or out_path is None or out_path == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_path):
        raise Exception('Must be an absolute path')

    # convert
    img_compress(file_path, out_path)


def create_tiles(file_path, out_dir, tile_size_in_m=None, tile_size_in_pixels=None, tile_overlap=0.0):
    """Tiles an image into smaller square chunks

    Arguments
    ----------
        file_path : str
            Path to source .tif file
        out_dir : str
            Path to output the .tif tiles
        tile_size_in_m : tuple
            Tile (height,width) in ground meters
        tile_size_in_pixels : tuple
            Tile (height,width) in pixels
        tile_overlap : float
            Amount of overlap of each tile in float format. Should range between [0.0,0.9]
    """

    # validate input
    if file_path is None or file_path == '' or out_dir is None or out_dir == '':
        raise Exception('Invalid inputs')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_dir):
        raise Exception('Must be an absolute path')

    # convert
    if tile_size_in_m is not None:
        img_create_tiles(file_path, out_dir, tile_overlap=tile_overlap, tile_size_in_m=tile_size_in_m)
    else:
        img_create_tiles(file_path, out_dir, tile_overlap=tile_overlap, tile_size_in_pixels=tile_size_in_pixels)


def search(limit=100, taken_at_min=None, taken_at_max=None, pixel_size_m_max=None, point_contained=None):
    """Searches for raster on the database

    Arguments
    ---------
    limit : int
        Limit to the number of rows returned by the SQL query
    taken_at_min : str
        Min timestamp for when the raster was taken (ISO format)
    taken_at_max : str
        Max timestamp for when the raster was taken (ISO format)
    pixel_size_m_max : int
        Max pixel size in ground meters
    point_contained : tuple
        Point in the (lat,lng) format that must be contained by the geometry
    """

    # get database
    database = get_database()

    # run query
    results = database.select(
            LIMIT=limit,
            TAKEN_AT_MIN=taken_at_min,
            TAKEN_AT_MAX=taken_at_max,
            PIXEL_SIZE_M_MAX=pixel_size_m_max,
            POINT_CONTAINED=point_contained
        )

    # convert to list of dicts
    records = results.to_dict(orient='records')

    # print results
    for record in records:
        pp.pprint(record)
    print(f'{len(records)} records found')


def autotest(module_name=None):
    """Runs the unit tests on the modules

    Arguments
    ---------
    module_name : str
        If you want to run the unit tests of a single module, specify the name here (cloudstorage, utils, database)
    """

    # validate input
    valid_module_names = ['cloudstorage', 'utils', 'database', 'config']
    if module_name is not None:
        if not isinstance(module_name, str):
            raise Exception('Module Name must be a string')
        elif module_name not in valid_module_names:
            raise Exception(f'Module Name must be one of : {valid_module_names}')


    def test_cloudstorage():
        # test the cloudstorage modules

        os.system('python3 -m gis-packer.tests.cloudstorage')


    def test_utils():
        # test the utils modules

        os.system('python3 -m gis-packer.tests.utils.raster')


    def test_database():
        # test the database modules

        os.system('python3 -m gis-packer.tests.database')


    if module_name is None:
        test_cloudstorage()
        test_utils()
        test_database()

    elif module_name == 'cloudstorage':
        test_cloudstorage()

    elif module_name == 'utils':
        test_utils()

    elif module_name == 'database':
        test_database()

    else:
        raise Exception('Invalid module name')


def reproject(file_path, out_path, target_crs=4326):
    """Reproject an image to a different coordinates reference system

    Arguments
    ----------
        file_path : str
            Path to the .tif file
        out_path : str
            Path to output the .tif file
        new_crs : int
            ESPG code of the target coordinates reference system
    """

    # validate input
    if file_path is None or file_path == '' or out_path is None or out_path == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_path):
        raise Exception('Must be an absolute path')

    img_reproject(file_path, out_path, target_crs=target_crs)


def select_bands(file_path, out_path):
    """Takes a multi-band .tif file and creates a new image with only selected bands

    Arguments
    ---------
        src_path : str
            Path to source .tif file
        out_path : str
            Path to output .tif tiles
        bands : list
            List of the band indexes to keep (band indexes start from 1, not 0)
    """

    # validate input
    if file_path is None or file_path == '' or out_path is None or out_path == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(file_path):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_path):
        raise Exception('Must be an absolute path')

    # grab bands info
    bands_dict = bands_info(file_path)

    # print band info
    for key in bands_dict.keys():
        band_dict = bands_dict[key]
        ind = band_dict['index']
        description = band_dict['description']
        print(f'Index : {ind}')
        print(f'Description : {description}\n')

    # grab the bands to keep
    bands_kept = input('Provide indexes of bands to keep (provide as comma-separated, 1 or 3 bands) : ')
    bands_kept = bands_kept.split(',')
    bands_kept = [b for b in bands_kept if is_int(b)]
    bands_kept = [int(b) for b in bands_kept]

    if len(bands_kept) == 0:
        raise Exception('Invalid band indexes')

    # select the bands
    img_select_bands(file_path, out_path, bands_kept)


def create_aws_lambda_layer(req_path, out_path, bucket_name=None, file_key=None):
    """Creates a lambda layer and uploads it to AWS

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

    # validate input
    if req_path is None or req_path == '' or out_path is None or out_path == '':
        raise Exception('Invalid file path')

    # check if absolute
    if not os.path.isabs(req_path):
        raise Exception('Must be an absolute path')
    if not os.path.isabs(out_path):
        raise Exception('Must be an absolute path')

    # run
    create_lambda_layer(req_path, out_path, bucket_name=bucket_name, file_key=file_key)
