"""
    Class to interact with database
"""

import json

import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.wkt import loads as wkt_loads

from sqlalchemy import create_engine


# config file interface
from ..config import get_config, DB_USERNAME_KEY, DB_PASSWORD_KEY, DB_HOSTNAME_KEY, DB_PORT_KEY, DB_NAME_KEY

# basic utils
from ..utils.basic import is_iso_dt_str_valid


# data model for raster
create_table_raster_query = """
    CREATE TABLE raster (
        index BIGINT GENERATED ALWAYS AS IDENTITY,
        taken_at TIMESTAMP NOT NULL,
        bucket_name VARCHAR(128) NOT NULL,
        file_key VARCHAR(1024) NOT NULL,
        pixel_size_m INT NOT NULL,
        geometry geometry(POLYGON) NOT NULL,
        bands JSONB NOT NULL,
        profile JSONB NOT NULL,
        created_at timestamp NOT NULL DEFAULT current_timestamp,
        PRIMARY KEY(index),
        UNIQUE (bucket_name, file_key)
    )
"""


__database = None
def get_database():
    global __database

    if __database is None:
        __database = Database()

    return __database


class Database:

    def __init__(self):

        # grab config
        config = get_config()
        username = config[DB_USERNAME_KEY]
        password = config[DB_PASSWORD_KEY]
        hostname = config[DB_HOSTNAME_KEY]
        port = config[DB_PORT_KEY]
        db_name = config[DB_NAME_KEY]

        # Set up database connection engine
        self.engine = create_engine(
            f'postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{db_name}',
            connect_args={'options': '-csearch_path={}'.format('public')}
        )

        # check if the raster table is in the database, if not create it
        self.init_raster_table()


    def execute_query(self, query):
        """
            Executes a SQL query on the database, returns nothing
        """

        with self.engine.connect() as connection:
            with connection.begin():
                connection.execute(query)


    def init_raster_table(self):
        """
            If the db doesn't contain the table raster, it creates it
        """

        # check if the table raster is in the table
        result = []
        with self.engine.connect() as connection:
            with connection.begin():
                rs = connection.execute("""
                    SELECT EXISTS (
                        SELECT FROM
                            information_schema.tables
                        WHERE
                            table_name = 'raster'
                    );
                """)

            for row in rs:
                result.append(row)

        # grab first row
        result = str(result[0][0])

        # convert to boolean
        has_table = (result in ('t', 'true', 'True'))

        # if the database doesn't have the table raster, create it
        if not has_table:
            print('Table raster not found in database, creating now...')
            self.execute_query(create_table_raster_query)


    def execute_query_with_return(self, query):

        # run
        results = pd.read_sql_query(
            con=self.engine,
            sql=query
        )

        # if query returns a geometry column
        if 'geometry' in results.columns:

            # parse geometry
            results['geometry'] = results['geometry'].apply(wkt_loads)

            # convert to geodataframe
            results = gpd.GeoDataFrame(results)


        return results


    def insert(
            self,
            taken_at,
            bucket_name,
            file_key,
            pixel_size_m,
            geometry,
            bands,
            profile
        ):
        """Inserts the metadata of a raster in the DB

        Arguments
        ---------
            taken_at : str
                ISO timestamp of the raster
            bucket_name : str
                Name of the bucket in which the raster is located
            file_key : str
                File key of the raster in the bucket
            pixel_size_m : int
                Pixel size in meters of the raster
            geometry : str
                PostGIS Polygon representing the area of the raster
            bands : dict
                Information about the bands
            profile : dict
                Other information about the raster
        """

        if not isinstance(taken_at, str):
            raise Exception('Invalid taken_at')

        if not isinstance(bucket_name, str):
            raise Exception('Invalid bucket_name')

        if not isinstance(file_key, str):
            raise Exception('Invalid file_key')

        if not isinstance(pixel_size_m, int):
            raise Exception('Invalid pixel_size_m')

        if not isinstance(geometry, str):
            raise Exception('Invalid geometry')

        if not isinstance(bands, dict):
            raise Exception('Invalid bands')

        if not isinstance(profile, dict):
            raise Exception('Invalid profile')

        # serialize the dicts
        bands = json.dumps(bands)
        profile = json.dumps(profile)

        # build sql query
        sql_query = f"""
            INSERT INTO raster
                (taken_at, bucket_name, file_key, pixel_size_m, geometry, bands, profile)
            VALUES
                ('{taken_at}', '{bucket_name}', '{file_key}', {pixel_size_m}, '{geometry}', '{bands}', '{profile}')
        """

        self.execute_query(sql_query)


    def delete(
            self,
            bucket_name,
            file_key
        ):
        """
            Deletes an raster from the database
        """

        # build sql query
        sql_query = f"""
            DELETE FROM raster WHERE bucket_name = '{bucket_name}' AND file_key = '{file_key}'
        """

        self.execute_query(sql_query)


    def select(
            self,
            OFFSET=0,
            LIMIT=1000,
            TAKEN_AT_MIN=None,
            TAKEN_AT_MAX=None,
            PIXEL_SIZE_M_MAX=None,
            POINT_CONTAINED=None
        ):
        """
            Returns the raster using filters
        """

        # validate input
        if not isinstance(LIMIT, int):
            raise Exception('invalid LIMIT arg')
        if TAKEN_AT_MIN is not None and not isinstance(TAKEN_AT_MIN, str):
            raise Exception('invalid TAKEN_AT_MIN arg')
        if TAKEN_AT_MAX is not None and not isinstance(TAKEN_AT_MAX, str):
            raise Exception('invalid TAKEN_AT_MAX arg')
        if POINT_CONTAINED is not None and not isinstance(POINT_CONTAINED, tuple):
            raise Exception('invalid POINT_CONTAINED arg')

        if TAKEN_AT_MAX is not None and not is_iso_dt_str_valid(TAKEN_AT_MAX):
            raise Exception('invalid iso format TAKEN_AT_MAX arg')
        if TAKEN_AT_MIN is not None and not is_iso_dt_str_valid(TAKEN_AT_MIN):
            raise Exception('invalid iso format TAKEN_AT_MIN arg')

        # convert point to postgis point
        point_contained = None
        if POINT_CONTAINED is not None:

            # validate lat, lng
            lat, lng = POINT_CONTAINED
            if not isinstance(lat, (float, int)) or not isinstance(lng, (float, int)):
                raise Exception('invalid POINT_CONTAINED arg')

            # parse
            point_contained = f'POINT({lng} {lat})'


        # where statements to filter raster
        WHERE_TAKEN_AT_MIN = ''
        if TAKEN_AT_MIN is not None:
            WHERE_TAKEN_AT_MIN = f"AND taken_at >= '{TAKEN_AT_MIN}'"

        WHERE_TAKEN_AT_MAX = ''
        if TAKEN_AT_MAX is not None:
            WHERE_TAKEN_AT_MAX = f"AND taken_at >= '{TAKEN_AT_MAX}'"

        WHERE_PIXEL_SIZE_M_MAX = ''
        if PIXEL_SIZE_M_MAX is not None:
            WHERE_PIXEL_SIZE_M_MAX = f'AND pixel_size_m <= {PIXEL_SIZE_M_MAX}'

        WHERE_POINT_CONTAINED = ''
        if point_contained is not None:
            WHERE_POINT_CONTAINED = f"AND ST_Contains(geometry, '{point_contained}')"


        # Build SQL Query
        sql_query = f"""
            SELECT
                index,
                taken_at,
                bucket_name,
                file_key,
                pixel_size_m,
                bands,
                ST_AsText(geometry) as geometry,
                created_at
            FROM
                raster
            WHERE
                true {WHERE_TAKEN_AT_MIN} {WHERE_TAKEN_AT_MAX} {WHERE_PIXEL_SIZE_M_MAX} {WHERE_POINT_CONTAINED}
            ORDER BY
                index
            OFFSET
                {OFFSET}
            LIMIT
                {LIMIT}
        """

        # run
        results = pd.read_sql_query(
            con=self.engine,
            sql=sql_query
        )

        if len(results.index) > 0:

            # parse geometry
            results['geometry'] = results['geometry'].apply(wkt_loads)

            # parse datetime columns
            results['taken_at'] = results['taken_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
            results['created_at'] = results['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # convert to geodataframe
        results = gpd.GeoDataFrame(results)

        return results
