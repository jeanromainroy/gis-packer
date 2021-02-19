"""
    File contains GIS functions
"""

import json
import numpy as np

from shapely.geometry import Point
import geopandas as gpd


def bboxes_to_GeoJSON(bboxes, crs, out_path=None):
    """Takes a bounding box as input and returns the GeoJSON

    Arguments
    ---------
    bbox : list
        Bounding box (eg. [[lat_1, lng_1],[lat_1 + lat_delta, lng_1],[lat_1 + lat_delta, lng_1 + lng_delta],[lat_1, lng_1 + lng_delta],[lat_1, lng_1]])
    crs : str
        Coordinates Reference system (e.g. '4326')

    Returns
    -------
    geojson : dict
        Geojson object
    """

    # convert bbox to json
    geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": f"urn:ogc:def:crs:EPSG::{crs}"
            }
        },
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": bboxes
                }
            }
        ]
    }

    # save geojson json
    if out_path is not None:
        with open(out_path, 'w') as outfile:
            json.dump(geojson, outfile)

    return geojson


def point_to_GeoJSON(point, crs, out_path=None):
    """Takes a point as input and returns the GeoJSON

    Arguments
    ---------
    point : list
        point (e.g. [lat, lng])
    crs : str
        Coordinates Reference system (e.g. '4326')

    Returns
    -------
    geojson : dict
        Geojson object
    """

    # convert point to json
    geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": f"urn:ogc:def:crs:EPSG::{crs}"
            }
        },
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [point]
                }
            }
        ]
    }

    # save geojson json
    if out_path is not None:
        with open(out_path, 'w') as outfile:
            json.dump(geojson, outfile)

    return geojson


def bounds_to_postgis_polygon(lat_1, lng_1, lat_2, lng_2):
    """ Takes the bounds and returns a postgis polygon
    """

    # init
    postgis_polygon = f"""
        POLYGON((
            {lng_1} {lat_1},
            {lng_1} {lat_2},
            {lng_2} {lat_2},
            {lng_2} {lat_1},
            {lng_1} {lat_1}
        ))
    """

    return postgis_polygon



def postgis_box2d_to_bbox(postgis_box2d_geometry):
    """
        Takes a postgis Box2D as input and returns the corners in the [xMin, yMin, xMax, yMax] order (reminder: postgis flips lat/lng to lng/lat)
    """

    # cast as str
    geometry = str(postgis_box2d_geometry)

    # parse
    geometry = geometry.split('(')[-1]
    geometry = geometry.replace(')', '')
    geometry = geometry.strip()

    # split points
    points = geometry.split(',')
    if len(points) != 2:
        raise Exception('Input bounding box is invalid')

    # go through points
    clean_pts = []
    for point in points:

        # split lat/lng
        point = point.strip()
        lng_lat = point.split(' ')
        if len(lng_lat) != 2:
            raise Exception('Input point is invalid')

        # parse
        lng, lat = lng_lat
        lng = lng.strip()
        lat = lat.strip()
        lat = float(lat)
        lng = float(lng)

        # append
        clean_pts.append([lng, lat])

    # check
    if len(clean_pts) != 2:
        raise Exception('Invalid bbox after processing')

    # grab corners
    x_1 = clean_pts[0][0]
    y_1 = clean_pts[0][1]
    x_2 = clean_pts[1][0]
    y_2 = clean_pts[1][1]
    x_diff = abs(x_2 - x_1)
    y_diff = abs(y_2 - y_1)
    min_x = min([x_1, x_2])
    min_y = min([y_1, y_2])
    max_x = min_x + x_diff
    max_y = min_y + y_diff

    # build bbox
    bbox = []
    bbox.append([min_y, min_x])
    bbox.append([min_y, max_x])
    bbox.append([max_y, max_x])
    bbox.append([max_y, min_x])
    bbox.append([min_y, min_x])

    return bbox


def postgis_point_to_lat_lng(postgis_point_geometry):
    """
        Takes a postgis Point as input and returns the latitude and longitude in the [lat, lng] order
    """

    # cast as str
    point = str(postgis_point_geometry)

    # parse
    point = point.split('(')[-1]
    point = point.replace(')', '')

    # split lat/lng
    point = point.strip()
    lng_lat = point.split(' ')
    if len(lng_lat) != 2:
        raise Exception('Input point is invalid')

    # parse
    lng, lat = lng_lat
    lng = lng.strip()
    lat = lat.strip()
    lat = float(lat)
    lng = float(lng)

    return [lat, lng]


def is_point_inside(satdata, lat, lng):
    """
        Returns true if point is inside
    """

    # grab bounds
    min_lng = min([satdata.bounds.right, satdata.bounds.left])
    max_lng = max([satdata.bounds.right, satdata.bounds.left])
    min_lat = min([satdata.bounds.top, satdata.bounds.bottom])
    max_lat = max([satdata.bounds.top, satdata.bounds.bottom])

    # check if inside
    if lng < min_lng or lng > max_lng:
        return False
    if lat < min_lat or lat > max_lat:
        return False

    return True


def convert_lat_lng_to_pixel(satdata, lat, lng):
    """
        Maps a (lat, lng) point to a pixel (y, x) point
    """

    # check if inside
    if not is_point_inside(satdata, lat, lng):
        raise Exception('Invalid lat/lng, outside of raster')

    # Get dimensions, in map units
    width_in_projected_units = np.abs(satdata.bounds.right - satdata.bounds.left)
    height_in_projected_units = np.abs(satdata.bounds.top - satdata.bounds.bottom)

    # compute crs length / pix
    xres = width_in_projected_units/float(satdata.width)
    yres = height_in_projected_units/float(satdata.height)

    # compute
    xpos = (satdata.bounds.right-lng)/xres
    ypos = (satdata.bounds.top-lat)/yres

    # round
    xpos = int(xpos)
    ypos = int(ypos)

    return ypos, xpos


def pixel_pos_to_lat_lng(satdata, y_pos, x_pos):
    """
        Given a pixel position return the lat/lng position
    """

    # A dataset’s transform is an affine transformation matrix that maps
    # pixel locations in (row, col) coordinates to (x, y) spatial positions.
    # The product of this matrix and (0, 0), the row and column coordinates
    # of the upper left corner of the dataset, is the spatial position of the upper left corner.
    lng, lat = satdata.transform * (x_pos, y_pos)

    # check if inside
    if not is_point_inside(satdata, lat, lng):

        # grab bounds
        min_lng = min([satdata.bounds.right, satdata.bounds.left])
        max_lng = max([satdata.bounds.right, satdata.bounds.left])
        min_lat = min([satdata.bounds.top, satdata.bounds.bottom])
        max_lat = max([satdata.bounds.top, satdata.bounds.bottom])

        if lng < min_lng:
            print(f'Longitude {lng} < {min_lng}')
            lng = min_lng

        if lng > max_lng:
            print(f'Longitude {lng} > {max_lng}')
            lng = max_lng

        if lat < min_lat:
            print(f'Latitude {lat} < {min_lat}')
            lat = min_lat

        if lat > max_lat:
            print(f'Latitude {lat} > {max_lat}')
            lat = max_lat

    return lat, lng


def pixel_bbox_to_lat_lng(satdata, bbox):
    """
        Given a pixel bounding box return the lng/lat equivalent
    """

    # init
    bbox_mapped = []

    for pt in bbox:

        # split
        y_pos, x_pos = pt

        # map pixel position to lng/lat position
        lat, lng = pixel_pos_to_lat_lng(satdata, y_pos, x_pos)

        # append
        bbox_mapped.append([lng, lat])

    return bbox_mapped


def get_pixel_in_m(satdata):
    """
        Returns the height and width of a pixel in meters
    """

    # grab bounds
    min_lng = min([satdata.bounds.right, satdata.bounds.left])
    max_lng = max([satdata.bounds.right, satdata.bounds.left])
    min_lat = min([satdata.bounds.top, satdata.bounds.bottom])
    max_lat = max([satdata.bounds.top, satdata.bounds.bottom])

    # create lines
    top_line = [Point(min_lng, max_lat), Point(max_lng, max_lat)]
    bottom_line = [Point(min_lng, min_lat), Point(max_lng, min_lat)]
    left_line = [Point(min_lng, min_lat), Point(min_lng, max_lat)]
    right_line = [Point(max_lng, min_lat), Point(max_lng, max_lat)]

    def compute_dist(line, crs):

        gdf_1 = gpd.GeoDataFrame(geometry=[line[0]], crs=crs)
        gdf_2 = gpd.GeoDataFrame(geometry=[line[1]], crs=crs)

        gdf_1.to_crs(epsg=3857, inplace=True)
        gdf_2.to_crs(epsg=3857, inplace=True)

        # validate
        lat_1 = gdf_1.to_numpy()[0][0].y
        lat_2 = gdf_1.to_numpy()[0][0].y
        if np.abs(lat_1) > 19971800 or np.abs(lat_2) > 19971800:
            raise Exception('The crs used to compute the distance does not work for abs(latitude) > 85 deg')

        l = gdf_1.distance(gdf_2)
        l = l.to_numpy()[0]

        return l

    # compute distance
    top = compute_dist(top_line, satdata.crs)
    bottom = compute_dist(bottom_line, satdata.crs)
    left = compute_dist(left_line, satdata.crs)
    right = compute_dist(right_line, satdata.crs)

    # average
    dist_x = (top + bottom)/2.0
    dist_y = (left + right)/2.0

    # per pixel
    x_res_in_m = dist_x/float(satdata.width)
    y_res_in_m = dist_y/float(satdata.height)

    return y_res_in_m, x_res_in_m


def get_crs(satdata):
    """
        Returns the ESPG CRS code
    """
    return str(satdata.crs).split(':')[-1]
