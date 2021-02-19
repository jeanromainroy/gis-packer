# GIS Helper
from .gis import get_pixel_in_m, bboxes_to_GeoJSON, pixel_bbox_to_lat_lng, bounds_to_postgis_polygon, get_crs

# basics
import os
import json
from tqdm import tqdm
from humanize import naturalsize as sz

import numpy as np
import matplotlib.pyplot as plt

from PIL import Image

from .basic import get_iso_timestamp, is_int

# import rasterio's tools
import rasterio
from rasterio.plot import show as rasterio_show
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform
from rasterio.warp import reproject as rasterio_reproject

# xarray
import xarray as xr

# Pretty print
import pprint
pp = pprint.PrettyPrinter(depth=4)



def load(src_path):
    """
        Loads raster as a rasterio object
    """

    # validate input
    if src_path is None or src_path == '':
        raise Exception('Must provide a file path')

    # check if on disk
    if not os.path.exists(src_path):
        raise Exception(f'File not found at {src_path}')

    # load with rasterio
    satdata = rasterio.open(src_path)

    return satdata


def get_attributes(src_path):
    """
        Returns a dict with all the important attributes about a .tif file
    """

    # load image
    satdata = load(src_path)

    # check input
    if not isinstance(satdata, rasterio.io.DatasetReader):
        raise Exception('Wrong Format')

    # init attributes
    attributes = {}

    # grab bands info
    bands_dict = bands_info(src_path)
    attributes['bands'] = bands_dict

    # taken_at
    attributes['taken_at'] = get_iso_timestamp()

    # grab image m / pixel
    x_res_in_m, y_res_in_m = get_pixel_in_m(satdata)
    pixel_size_m = (x_res_in_m + y_res_in_m)/2.0
    attributes['pixel_size_m'] = pixel_size_m

    # set geometry
    lat_1 = satdata.bounds.bottom
    lng_1 = satdata.bounds.left
    lat_2 = satdata.bounds.top
    lng_2 = satdata.bounds.right
    attributes['geometry'] = bounds_to_postgis_polygon(lat_1, lng_1, lat_2, lng_2)

    # grab crs
    crs = get_crs(satdata)

    # set profile
    profile = dict({k:v for k, v in satdata.profile.items() if k != 'crs'})
    profile['crs'] = crs
    attributes['profile'] = json.dumps(profile)

    return attributes


def bands_info(src_path):
    """Returns a dict containing the bands' information

    Arguments
    ---------
        src_path : str
            Path to .tif file

    Returns
    -------
        bands_dict : dict
            Dict of the bands
    """

    # load image
    satdata = load(src_path)

    # init
    bands_dict = {}

    # grab descriptions for all bands
    descriptions = satdata.descriptions

    # grab bands info
    for i in range(0, satdata.count):

        # grab band index
        band_index = i+1

        # init
        band_dict = {}

        # grab band's metadata
        band_metadata = satdata.tags(band_index)
        description = descriptions[i]

        # set attributes
        band_dict['index'] = band_index
        band_dict['description'] = description
        band_dict['metadata'] = band_metadata

        # append
        bands_dict[band_index] = band_dict

    return bands_dict


def info(src_path):
    """
        Display General Info about the satdata
    """

    # load image
    satdata = load(src_path)

    # check input
    if not isinstance(satdata, rasterio.io.DatasetReader):
        raise Exception('Wrong Format')

    # dataset name
    print(f'Dataset Name : {satdata.name}\n')

    # Minimum bounding box in projected units
    print(f'Min Bounding Box : {satdata.bounds}\n')

    # Get dimensions, in map units
    width_in_projected_units = abs(satdata.bounds.right - satdata.bounds.left)
    height_in_projected_units = abs(satdata.bounds.top - satdata.bounds.bottom)
    print(f"Projected units (width, height) : ({width_in_projected_units}, {height_in_projected_units})\n")

    # Number of rows and columns.
    print(f"Rows: {satdata.height}, Columns: {satdata.width}\n")

    # Get coordinate reference system
    print(f'Coordinates System : {satdata.crs}\n')

    # Convert pixel coordinates to world coordinates.
    # Upper left pixel
    row_min = 0
    col_min = 0

    # Lower right pixel.  Rows and columns are zero indexing.
    row_max = satdata.height - 1
    col_max = satdata.width - 1

    # Transform coordinates with the dataset's affine transformation.
    topleft = satdata.transform * (row_min, col_min)
    botright = satdata.transform * (row_max, col_max)

    print(f"Top left corner coordinates: {topleft}")
    print(f"Bottom right corner coordinates: {botright}\n")

    # grab image m / pixel
    x_res_in_m, y_res_in_m = get_pixel_in_m(satdata)
    print(f'Pixel width in meters: {x_res_in_m}')
    print(f'Pixel height in meters: {y_res_in_m}\n')

    # All of the metadata required to create an image of the same dimensions, datatype, format, etc. is stored in
    # the dataset's profile:
    pp.pprint(satdata.profile)
    print('\n')

    # grab bands info
    bands_dict = bands_info(src_path)

    # print
    print('--- Bands ---')
    for key in bands_dict.keys():
        pp.pprint(bands_dict[key])


def show(src_path):
    """
        Display satdata as matplotlib figure
    """

    # load file
    satdata = load(src_path)

    # check input
    if not isinstance(satdata, rasterio.io.DatasetReader):
        raise Exception('Wrong Format')

    rasterio_show(satdata)


def show_chunk(src_path, chunk_size=512, offset_x=0, offset_y=0, block_size=512):
    """
        Preview .tif raster without crashing computer
    """

    if offset_x is None:
        offset_x = 0
    if offset_y is None:
        offset_y = 0

    # load
    bands = xr.open_rasterio(src_path, chunks={'x':block_size, 'y':block_size})

    # show
    _ = bands[:, offset_y:chunk_size+offset_y, offset_x:chunk_size+offset_x].plot.imshow()
    plt.show()


def write(data, meta, bands, out_path):
    """
        Write file with description and metadata
    """

    with rasterio.open(out_path, 'w', **meta) as dst:

        # write
        dst.write(data)

        # write bands info
        for i in range(0, len(data)):

            # grab band index
            band_index = i+1

            # grab description
            description = bands[band_index]['description']

            # grab band's metadata
            band_metadata = bands[band_index]['metadata']

            # description
            dst.set_band_description(band_index, description)

            # update tags
            if 'wavelength_units' in band_metadata.keys():
                dst.update_tags(band_index, wavelength_units=band_metadata['wavelength_units'])
            if 'wavelength' in band_metadata.keys():
                dst.update_tags(band_index, wavelength=band_metadata['wavelength'])


def unstack_bands(src_path, out_dir):
    """
        Unstacks an image into its individual bands
    """

    # load file
    satdata = load(src_path)

    # check out dir
    if not os.path.isdir(out_dir):
        raise Exception(f'Invalid output dir {out_dir}')

    # get basename
    basename = os.path.basename(src_path)

    # number of bands in this dataset
    print(f'Number of Bands : {satdata.count}\n')

    # get the metadata of original GeoTIFF:
    meta = satdata.meta.copy()

    # read all bands from source dataset into a single 3-dimensional ndarray
    data = satdata.read()

    #  update count
    meta.update(count=1)

    # grab bands info
    bands_dict = bands_info(src_path)

    # init list with all the names
    out_paths = []

    # save bands
    for i, band in enumerate(data):

        # grab band index
        band_index = i+1

        # output name
        new_basename = basename.replace('.', f'_{band_index}.')
        out_path = os.path.join(out_dir, new_basename)

        # band info
        new_bands_dict = {}
        new_bands_dict[1] = bands_dict[band_index]

        # add dimensions
        band = band[np.newaxis, :, :]

        # write
        write(band, meta, new_bands_dict, out_path)

        # append
        out_paths.append(out_path)

    return out_paths


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
    if not os.path.isdir(src_dir):
        raise Exception('Invalid source directory')

    # check out path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Invalid output path')

    # grab all files in source dir
    src_paths = []
    for filename in os.listdir(src_dir):
        if 'tif' in filename:
            src_paths.append(os.path.join(src_dir, filename))

    if len(src_paths) < 2:
        raise Exception(f'Found {len(src_paths)} in the source dir')

    # metadata of the first file
    ref_satdata = load(src_paths[0])
    ref_meta = ref_satdata.meta.copy()

    # validate bands sizes
    ref_w = ref_satdata.width
    ref_h = ref_satdata.height
    for src_path in src_paths:

        # load meta
        satdata_i = load(src_path)

        if satdata_i.count != 1:
            raise Exception(f'Contains more than one band {src_path}')

        if satdata_i.width != ref_w:
            raise Exception(f'Invalid width, {src_path}')

        if satdata_i.height != ref_h:
            raise Exception(f'Invalid height, {src_path}')

    # update count
    ref_meta.update(count=len(src_paths))

    # create bands
    bands_dict = {}
    canvas = np.zeros((len(src_paths), ref_h, ref_w), dtype=np.uint8)

    for i, src_path in enumerate(src_paths):

        # grab band index
        band_index = i+1

        # grab band info
        band_dict = bands_info(src_path)[1]

        # set new index
        band_dict['index'] = band_index

        # set on bands dict
        bands_dict[band_index] = band_dict

        # load data
        satdata = load(src_path)
        data = satdata.read(1)

        # add dimensions
        data = data[np.newaxis, :, :]

        # add to canvas
        canvas[band_index-1, :, :] = data

    # write
    write(canvas, ref_meta, bands_dict, out_path)


def select_bands(src_path, out_path, band_indexes):
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

    # load file
    satdata = load(src_path)

    # check out path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Invalid output path')

    # check number of bands
    nbr_of_bands = satdata.count
    if nbr_of_bands < 2:
        raise Exception(f'File only has {nbr_of_bands} bands')

    # validate band indexes
    if not isinstance(band_indexes, list):
        raise Exception(f'Band indexes must be a list')

    if len(band_indexes) > nbr_of_bands:
        raise Exception('Too many band indexes')

    if len(band_indexes) == 0:
        raise Exception('Too few band indexes')

    for band_index in band_indexes:
        if not is_int(band_index):
            raise Exception(f'Invalid band indexes')

    # convert to int
    band_indexes = [int(b) for b in band_indexes]

    for band_index in band_indexes:
        if band_index < 1 or band_index > nbr_of_bands:
            raise Exception('Invalid band indexes')

    # convert band indexes to numpy indexes -1
    band_indexes = [ind-1 for ind in band_indexes]

    # get the metadata of original GeoTIFF:
    meta = satdata.meta.copy()

    # read all bands from source dataset into a single ndarray
    data = satdata.read()

    # grab the selected bands
    data = data[band_indexes, :, :]

    # update
    meta.update(count=len(band_indexes))

    # grab bands information
    bands_dict = bands_info(src_path)

    # new bands info
    new_bands_dict = {}
    for i, band_index in enumerate(band_indexes):
        new_bands_dict[i+1] = bands_dict[band_index+1]

    # write
    write(data, meta, new_bands_dict, out_path)


def fix_nodata(src_path, out_path):
    """If the raster's nodata attribute both not none and not zero it will change the nodata value to zero

    Arguments
    ---------
        src_path : str
            Path to source .tif file
        out_path : str
            Path to output .tif file
    """

    # load
    satdata = load(src_path)

    # check out path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Invalid output path')

    # load metadata
    meta = satdata.meta.copy()

    # get band info
    bands_dict = bands_info(src_path)

    # check if nodata attribute
    if 'nodata' in meta and meta['nodata'] is not None and meta['nodata'] != 0:

        # grab nodata value
        nodata_val = meta['nodata']

        # read all bands from source dataset into a single ndarray
        data = satdata.read()

        # set
        data[data == nodata_val] = 0

        # update meta
        meta.update(nodata=None)

        # write new image
        write(data, meta, bands_dict, out_path)


def compress(src_path, out_path, compression_type='JPEG'):
    """
        Compress raster to reduce filesize

        Raster datasets use compression to reduce filesize. There are a number of compression methods,
        all of which fall into two categories: lossy and lossless. Lossless compression methods retain
        the original values in each pixel of the raster, while lossy methods result in some values
        being removed. Because of this, lossy compression is generally not well-suited for analytic
        purposes, but can be very useful for reducing storage size of visual raster.

        By creating a lossy-compressed copy of a visual asset, we can significantly reduce the
        dataset's filesize. In this example, we will create a copy using the "JPEG" lossy compression method
    """

    # load file
    satdata = load(src_path)

    # check out path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Invalid output path')

    # get the metadata of original GeoTIFF:
    meta = satdata.meta.copy()

    # get initial size in bytes
    init_size = os.path.getsize(src_path)

    # check number of bands
    nbr_of_bands = satdata.count
    if nbr_of_bands not in (1, 3):
        raise Exception(f'Raster has {nbr_of_bands} bands, only 1 or 3 are allowed. Use select-bands to fix')

    # check dtype
    img_dtype = meta['dtype']
    if img_dtype != 'uint8':
        raise Exception(f'Raster uses the {img_dtype} data type. Use to-uint8 to fix')

    # check if nodata attribute
    if 'nodata' in meta and meta['nodata'] is not None and meta['nodata'] != 0:

        # fix it
        fix_nodata(src_path, out_path)

        # change src to temp
        src_path = out_path

        # reload metadata
        satdata = load(src_path)
        meta = satdata.meta.copy()

    # update the 'compress' value
    meta.update(compress=compression_type)

    # grab bands info
    bands_dict = bands_info(src_path)

    # read
    data = satdata.read()

    # write file
    write(data, meta, bands_dict, out_path)

    # returns size in bytes
    final_size = os.path.getsize(out_path)

    # compute diff
    ratio = round(10000.0*final_size/float(init_size))/100.0

    # output a human-friendly size
    print(f'(Initial size, Final Size, Ratio) : ({sz(init_size)}, {sz(final_size)}, {ratio}%)\n')


def to_uint8(src_path, out_path, min_pixel_value=None, max_pixel_value=None):
    """
        Takes an image and converts the data type to uint8 by scaling down the pixel values
    """

    # load file
    satdata = load(src_path)

    # check out path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Invalid output path')

    # get the metadata of original GeoTIFF:
    meta = satdata.meta

    # check if nodata attribute
    nodata_val = None
    if 'nodata' in meta:
        nodata_val = meta['nodata']

    # read all bands from source dataset into a single ndarray
    bands = satdata.read()

    # if nodata value, fix it here
    if nodata_val is not None:
        meta.update(nodata=0)
        bands[bands == nodata_val] = 0

    # get max pixel values
    max_pix_val = np.max(bands)
    min_pix_val = np.min(bands)
    if max_pixel_value is not None:
        max_pix_val = max_pixel_value
    if min_pixel_value is not None:
        min_pix_val = min_pixel_value
    print(f'Using ({min_pix_val}/{max_pix_val}) as (min/max) pixel value')

    def scale(band):

        # get min/max val for band
        min_val = np.min(band)
        max_val = np.max(band)

        # if it hasn't been scaled to uint8
        if max_val > 255 or min_val < 0:
            band = (band - min_val)/(max_val - min_val)
            band[band > 1.0] = 1.0                      # if above set to max
            band[band < 0.0] = 0.0                      # if under set to min
            band = np.round(np.multiply(band, 255.0))

        return band

    # scale each band
    for i, band in enumerate(bands):
        bands[i] = scale(band).astype(np.uint8)

    # get count
    count = len(bands)

    # stack
    scaled_img = np.dstack(bands).astype(np.uint8)

    # move axis with entries to beginning
    scaled_img = np.moveaxis(scaled_img,-1,0)

    # get the dtype
    m_dtype = scaled_img.dtype

    # update the 'dtype' value
    meta.update(dtype=m_dtype)

    # update the 'count' value
    meta.update(count=count)

    # grab bands info
    bands_dict = bands_info(src_path)

    # write file
    write(scaled_img, meta, bands_dict, out_path)


def crop(src_path, out_path, aoi_geojson):
    """
        Crop raster using a Postgis Box2d geometry
    """

    # load raster
    satdata = load(src_path)

    # check out path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Invalid output path')

    # Using a copy of the metadata from our original raster dataset, we can write a new geoTIFF
    # containing the new, clipped raster data:
    meta = satdata.meta.copy()

    # grab geometries from geojson
    geoms = [feature["geometry"] for feature in aoi_geojson['features']]

    # apply mask with crop=True to crop the resulting raster to the AOI's bounding box
    clipped, transform = mask(satdata, geoms, crop=True)

    # update metadata with new, clipped mosaic's boundaries
    meta.update({
        "transform": transform,
        "height":clipped.shape[1],
        "width":clipped.shape[2]
    })

    # grab bands info
    bands_dict = bands_info(src_path)

    # write the clipped-and-cropped dataset to a new GeoTIFF
    write(clipped, meta, bands_dict, out_path)


def reproject(src_path, out_path, target_crs='4326'):
    """
        Reprojects the raster to a new coordinate system

        In order to translate pixel coordinates in a raster dataset into coordinates that use a
        spatial reference system, an **affine transformation** must be applied to the dataset.
        This **transform** is a matrix used to translate rows and columns of pixels into (x,y)
        spatial coordinate pairs. Every spatially referenced raster dataset has an affine transform
        that describes its pixel-to-map-coordinate transformation.

        In order to reproject a raster dataset from one coordinate reference system to another,
        rasterio uses the **transform** of the dataset: this can be calculated automatically using
        rasterio's `calculate_default_transform` method:

        target CRS: rasterio will accept any CRS that can be defined using WKT
    """

    # load satdata
    satdata = load(src_path)

    # check out path
    if not os.access(os.path.dirname(out_path), os.W_OK):
        raise Exception(f'Invalid output path')

    # calculate a transform and new dimensions using our dataset's current CRS and dimensions
    transform, width, height = calculate_default_transform(satdata.crs,
                                                        f'EPSG:{target_crs}',
                                                        satdata.width,
                                                        satdata.height,
                                                        *satdata.bounds)

    # Using a copy of the metadata from the clipped raster dataset and the transform we defined above,
    # we can write a new geoTIFF containing the reprojected and clipped raster data:
    metadata = satdata.meta.copy()

    # Change the CRS, transform, and dimensions in metadata to match our desired output dataset
    metadata.update({'crs':f'EPSG:{target_crs}',
                    'transform':transform,
                    'width':width,
                    'height':height})

    # apply the transform & metadata to perform the reprojection
    with rasterio.open(out_path, 'w', **metadata) as reprojected:
        for band in range(1, satdata.count + 1):
            rasterio_reproject(
                source=rasterio.band(satdata, band),
                destination=rasterio.band(reprojected, band),
                src_transform=satdata.transform,
                src_crs=satdata.crs,
                dst_transform=transform,
                dst_crs=f'EPSG:{target_crs}'
            )

    # Set tags & description
    satdata = load(out_path)
    data = satdata.read()

    # get meta
    meta = satdata.meta.copy()

    # get band info
    bands_dict = bands_info(src_path)

    # add other data
    write(data, meta, bands_dict, out_path)


def create_tiles(src_path, out_dir, tile_size_in_m=None, tile_size_in_pixels=None, tile_overlap=0.0):
    """
    Function to tile an image into smaller square chunks with embedded georeferencing info
    allowing an end user to specify the size of the tile, the overlap of each tile, and when to discard
    a tile if it contains blank datasets

    Arguments
    ----------
        src_path : str
            path to source image
        out_dir : str
            Path to output the .tif tiles
        tile_size_in_m : tuple
            Tile (height,width) in ground meters
        tile_size_in_pixels : tuple
            Tile (height,width) in pixels
        tile_overlap : float
            Amount of overlap of each tile in float format. Should range between [0.0,0.9]
    """

    # load data
    satdata = load(src_path)

    # check out dir
    if not os.path.isdir(out_dir):
        raise Exception(f'Invalid output dir {out_dir}')

    # validate input
    if tile_overlap is None or tile_overlap < 0 or tile_overlap > 0.9:
        raise Exception('Invalid tile overlap')

    if tile_size_in_m is None and tile_size_in_pixels is None:
        raise Exception('Must choose a tile length option')

    if tile_size_in_m is not None and tile_size_in_pixels is not None:
        raise Exception('Must choose only one tile length option')

    if tile_size_in_m is not None:

        if not isinstance(tile_size_in_m, tuple):
            raise Exception('invalid tile_size_in_m arg, must be a tuple')

        if len(tile_size_in_m) != 2:
            raise Exception('invalid tile_size_in_m arg, must be of length 2')

        l_y, l_x = tile_size_in_m
        if not isinstance(l_y, (float, int)) or not isinstance(l_x, (float, int)):
            raise Exception('invalid tile_size_in_m arg, components are not numbers')

    if tile_size_in_pixels is not None:

        if not isinstance(tile_size_in_pixels, tuple):
            raise Exception('invalid tile_size_in_pixels arg, must be a tuple')

        if len(tile_size_in_pixels) != 2:
            raise Exception('invalid tile_size_in_m arg, must be of length 2')

        l_y, l_x = tile_size_in_pixels
        if not isinstance(l_y, (float, int)) or not isinstance(l_x, (float, int)):
            raise Exception('invalid tile_size_in_pixels arg, components are not numbers')

    # grab crs
    crs = get_crs(satdata)

    # grab dimensions of image in pixels
    width = satdata.width
    height = satdata.height

    # init vars
    tile_size_x = 0.0
    tile_size_y = 0.0
    tile_size_x_m = 0.0
    tile_size_y_m = 0.0

    # grab image m / pixel
    y_res_in_m, x_res_in_m = get_pixel_in_m(satdata)

    if tile_size_in_pixels is not None:
        (tile_size_y, tile_size_x) = tile_size_in_pixels
        tile_size_x_m = tile_size_x*x_res_in_m
        tile_size_y_m = tile_size_y*y_res_in_m

    elif tile_size_in_m is not None:
        # if tile length is specified in meters, convert to pixels
        (tile_size_y_m, tile_size_x_m) = tile_size_in_m
        tile_size_x = int(tile_size_x_m/float(x_res_in_m))
        tile_size_y = int(tile_size_y_m/float(y_res_in_m))

    else:
        raise Exception('Invalid tile length')

    # round tile length in meters
    tile_size_y_m = int(tile_size_y_m)
    tile_size_x_m = int(tile_size_x_m)

    # validate tile length
    if tile_size_x < 2 or tile_size_y < 2:
        raise Exception('Tile length too small')

    # create bounding boxes
    bboxes = []
    overflow_x = False
    overflow_y = False
    tile_actual_length_x = int(tile_size_x * (1 - tile_overlap))
    tile_actual_length_y = int(tile_size_y * (1 - tile_overlap))
    for x_pos in range(0, width, tile_actual_length_x):

        # create bounding coordinates
        min_x = x_pos
        max_x = x_pos + tile_size_x

        # check if we overflow
        if max_x > width:
            overflow_x = True
            max_x = width
            min_x = width - tile_size_x

        for y_pos in range(0, height, tile_actual_length_y):

            # create bounding coordinates
            min_y = y_pos
            max_y = y_pos + tile_size_y

            # check if we overflow
            if max_y > height:
                overflow_y = True
                max_y = height
                min_y = height - tile_size_y

            # create bounding box
            bbox = []
            bbox.append([min_y, min_x])
            bbox.append([min_y, max_x])
            bbox.append([max_y, max_x])
            bbox.append([max_y, min_x])
            bbox.append([min_y, min_x])

            # map bbox to raster's crs
            bbox_mapped = pixel_bbox_to_lat_lng(satdata, bbox)

            # append
            bboxes.append(bbox_mapped)

            # stop here if we are overflowing
            if overflow_y:
                overflow_y = False
                break

        # stop here if we are overflowing
        if overflow_x:
            overflow_x = False
            break

    # inform user with the number of tiles about to be written to disk
    print(f'Number of tiles = {len(bboxes)}, using tile length = ({tile_size_y},{tile_size_x}) pixels / ({tile_size_y_m},{tile_size_x_m}) meters')

    # go through and crop
    ind = 0
    for bbox in tqdm(bboxes):

        # increment
        ind += 1

        # output path
        out_path = os.path.join(out_dir, f'{ind}.tif')

        # convert to geojson
        bboxes_geojson = bboxes_to_GeoJSON([bbox], crs)

        # crop
        crop(src_path, out_path, bboxes_geojson)
