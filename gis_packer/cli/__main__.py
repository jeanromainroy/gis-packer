"""
    Command line interface triggered by main
"""
import sys
import click

# config file interface
from ..config import load_config, create_template_config_file, DEFAULT_CONFIG_FILE

# import api funcs
from .api import configure as configure_api
from .api import notebook as notebook_api
from .api import search as search_api
from .api import lab as lab_api
from .api import tutorials as tutorials_api
from .api import get_file as get_file_api
from .api import post_file as post_file_api
from .api import info as info_api
from .api import autotest as autotest_api
from .api import create_tiles as create_tiles_api
from .api import unstack_bands as unstack_bands_api
from .api import stack_bands as stack_bands_api
from .api import to_uint8 as to_uint8_api
from .api import compress as compress_api
from .api import documentation as documentation_api
from .api import reproject as reproject_api
from .api import select_bands as select_bands_api
from .api import create_aws_lambda_layer as create_aws_lambda_layer_api


@click.group()
def cli():
    pass


@click.command()
def configure():
    """
        Sets the variables in the config file
    """
    configure_api()


@click.command()
def notebook():
    """
        Launches a jupyter notebook runtime environment on port 8888
    """
    notebook_api()


@click.command()
def lab():
    """
        Launches a jupyter lab runtime environment on port 8888
    """
    lab_api()


@click.command()
def documentation():
    """
        Launches a web server exposing the documentation on port
    """
    documentation_api()


@click.command()
def tutorials():
    """
        Launches an ephemerous jupyter notebook runtime environment on port 8888 in the tutorials folder
    """
    tutorials_api()


@click.command()
@click.option('--bucket-name', type=str, help='Name of the AWS S3 bucket')
@click.option('--file-key', type=str, help='File key')
@click.option('--out-path', type=str, help='Output path to save the file')
def get_file(bucket_name, file_key, out_path):
    """
        Downloads a file from the an AWS S3 Bucket
    """

    # check input
    if out_path is None:
        raise Exception('Must provide an output path')

    if bucket_name is None:
        raise Exception('Must provide a bucket name')

    if file_key is None:
        raise Exception('Must provide a file key')

    get_file_api(bucket_name, file_key, out_path)


@click.command()
@click.option('--bucket-name', type=str, help='Name of the AWS S3 bucket')
@click.option('--file-key', type=str, help='File key')
@click.option('--file-path', type=str, help='Path to .tif file')
def post_file(bucket_name, file_key, file_path):
    """
        Uploads a file to the AWS S3 Bucket
    """

    # check input
    if file_path is None:
        raise Exception('Must provide a file path')

    if bucket_name is None:
        raise Exception('Must provide a bucket name')

    if file_key is None:
        raise Exception('Must provide a file key')

    post_file_api(bucket_name, file_key, file_path)


@click.command()
@click.option('--file-path', type=str, help='Path to .tif file')
def info(file_path):
    """
        Prints the GIS info about the .tif file
    """

    # check input
    if file_path is None:
        raise Exception('Must provide a file path')

    info_api(file_path)


@click.command()
@click.option('--file-path', type=str, help='Path to .tif file')
@click.option('--out-dir', type=str, help='Path to output directory')
def unstack_bands(file_path, out_dir):
    """
        Unstacks an image into its individual bands
    """

    # check input
    if file_path is None:
        raise Exception('Must provide a file path')

    if out_dir is None:
        raise Exception('Must provide a output directory')

    unstack_bands_api(file_path, out_dir)


@click.command()
@click.option('--src-dir', type=str, help='Path to source directory containing the single bands .tif files')
@click.option('--out-path', type=str, help='Path to output .tif file')
def stack_bands(src_dir, out_path):
    """
        Stacks bands into a single raster
    """

    # check input
    if src_dir is None:
        raise Exception('Must provide a source directory')

    if out_path is None:
        raise Exception('Must provide an output path')

    stack_bands_api(src_dir, out_path)


@click.command()
@click.option('--file-path', type=str, help='Path to .tif file')
@click.option('--out-path', type=str, help='Path to output .tif file')
def to_uint8(file_path, out_path):
    """
        Converts the pixels of an image to the uint8 format
    """

    # check input
    if file_path is None:
        raise Exception('Must provide a file path')

    if out_path is None:
        raise Exception('Must provide a output path')

    to_uint8_api(file_path, out_path)


@click.command()
@click.option('--file-path', type=str, help='Path to source .tif file')
@click.option('--out-path', type=str, help='Path to output .tif file')
def compress(file_path, out_path):
    """
        Compresses an image to a lossy format
    """

    # check input
    if file_path is None:
        raise Exception('Must provide a file path')

    if out_path is None:
        raise Exception('Must provide a output path')

    compress_api(file_path, out_path)


@click.command()
@click.option('--file-path', type=str, help='Path to source .tif file')
@click.option('--out-dir', type=str, help='Path to output .tif tiles')
@click.option('--tile-width-meters', type=int, help='Tile with in ground meters')
@click.option('--tile-height-meters', type=int, help='Tile height in ground meters')
@click.option('--tile-width-pixels', type=int, help='Tile with in pixels')
@click.option('--tile-height-pixels', type=int, help='Tile height in pixels')
@click.option('--tile-overlap', type=float, help='Amount of overlap of each tile in float format. Should range between [0.0,0.9]')
def create_tiles(file_path, out_dir, tile_width_meters=None, tile_height_meters=None, tile_width_pixels=None, tile_height_pixels=None, tile_overlap=0.0):
    """
        Tiles an image into smaller square chunks
    """

    # check input
    if file_path is None:
        raise Exception('Must provide a file path')

    if out_dir is None:
        raise Exception('Must provide a output directory')

    # validate
    dimensions_set = [tile_width_meters, tile_height_meters, tile_width_pixels, tile_height_pixels]
    nbr_of_nones = dimensions_set.count(None)

    if nbr_of_nones != 2:
        raise Exception('Must set width and height')

    if tile_width_meters is not None:
        if tile_height_meters is None:
            raise Exception('If width is provided in meters, height must be provided in meters')

    if tile_height_meters is not None:
        if tile_width_meters is None:
            raise Exception('If width is provided in meters, height must be provided in meters')

    if tile_width_pixels is not None:
        if tile_height_pixels is None:
            raise Exception('If width is provided in pixels, height must be provided in pixels')

    if tile_height_pixels is not None:
        if tile_width_pixels is None:
            raise Exception('If width is provided in pixels, height must be provided in pixels')

    # create tuples
    tile_meters = None
    tile_pixels = None
    if tile_width_meters is not None:
        tile_meters = (tile_height_meters, tile_width_meters)
    if tile_height_pixels is not None:
        tile_pixels = (tile_height_pixels, tile_width_pixels)

    create_tiles_api(
        file_path,
        out_dir,
        tile_size_in_m=tile_meters,
        tile_size_in_pixels=tile_pixels,
        tile_overlap=tile_overlap
    )


@click.command()
@click.option('--limit', type=int, default=100, help='Limit to the number of rows returned by the SQL query')
@click.option('--taken-at-min', type=str, help='Min timestamp for when the raster was taken')
@click.option('--taken-at-max', type=str, help='Max timestamp for when the raster was taken')
@click.option('--pixel-size-m-max', type=int, help='Max pixel size in ground meters')
@click.option('--point-contained', type=tuple, help='Point in the (lat,lng) format that must be contained by the geometry')
def search(limit=100, taken_at_min=None, taken_at_max=None, pixel_size_m_max=None, point_contained=None):
    """
        Searches for raster on the database
    """
    search_api(
            limit=limit,
            taken_at_min=taken_at_min,
            taken_at_max=taken_at_max,
            pixel_size_m_max=pixel_size_m_max,
            point_contained=point_contained
        )


@click.command()
@click.option('--module-name', type=str, help='If only one module, state the name here')
def autotest(module_name=None):
    """
        Runs unit tests
    """
    autotest_api(module_name=module_name)


@click.command()
@click.option('--file-path', type=str, help='Path to source .tif file')
@click.option('--out-path', type=str, help='Path to output .tif file')
@click.option('--target-espg', type=int, help='ESPG code of the target coordinates reference system')
def reproject(file_path, out_path, target_espg=4326):
    """
        Reproject an image to a different coordinates reference system
    """
    reproject_api(file_path, out_path, target_crs=target_espg)


@click.command()
@click.option('--file-path', type=str, help='Path to source .tif file')
@click.option('--out-path', type=str, help='Path to output .tif file')
def select_bands(file_path, out_path):
    """
        Takes a multi-band .tif file and creates a new image with only selected bands
    """
    select_bands_api(file_path, out_path)


@click.command()
@click.option('--req-path', type=str, help='Path to the requirements.txt file containing all the desired python libraries')
@click.option('--out-path', type=str, help='Path to output lambda layer file')
@click.option('--bucket-name', type=str, help='Name of the AWS S3 bucket')
@click.option('--file-key', type=str, help='File key')
def create_aws_lambda_layer(req_path, out_path, bucket_name, file_key):
    """
        Creates a lambda layer and uploads it to AWS
    """

    # check input
    if req_path is None:
        raise Exception('Must provide a file path')
    if out_path is None:
        raise Exception('Must provide an output path')

    # run
    create_aws_lambda_layer_api(req_path, out_path, bucket_name=bucket_name, file_key=file_key)


# add commands
cli.add_command(configure)
cli.add_command(search)
cli.add_command(get_file)
cli.add_command(post_file)
cli.add_command(to_uint8)
cli.add_command(compress)
cli.add_command(unstack_bands)
cli.add_command(info)
cli.add_command(create_tiles)
cli.add_command(notebook)
cli.add_command(lab)
cli.add_command(tutorials)
cli.add_command(autotest)
cli.add_command(documentation)
cli.add_command(reproject)
cli.add_command(select_bands)
cli.add_command(create_aws_lambda_layer)


if __name__ == "__main__":

    # load the config file
    try:
        config = load_config()

    except FileNotFoundError:
        print(f'Unable to find the config file.')
        create_template_config_file()
        print(f'Created an empty config file at {DEFAULT_CONFIG_FILE}')
        sys.exit()

    # checks to make sure the config file is valid
    if not config.is_valid():
        print('Config file is invalid, refreshing it')
        config.delete()
        create_template_config_file()
        sys.exit()

    # check that all the values are set in the config file
    if not config.is_configured():
        print('Config file is not configured, please configure now')

        # launch config routine
        configure()

    # run app
    cli()
