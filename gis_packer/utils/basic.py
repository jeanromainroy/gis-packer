"""
    File contains useful methods
"""

import os
import logging
from datetime import datetime
from uuid import uuid4

def get_uuid():
    """
        Returns a random uuid4
    """
    return uuid4()


def get_timestamp():
    """
        Returns a timestamp of now as a int
    """
    return int(datetime.now().timestamp())

def get_iso_timestamp():
    """
        Returns a timestamp of now as iso format
    """
    return datetime.now().isoformat()


def is_iso_dt_str_valid(dt_str):
    """
        Returns true if provided str datetime is a valid iso format
    """
    try:
        datetime.fromisoformat(dt_str)
    except:
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return False
        return True
    return True


def is_int(val):
    """
        Returns true if value can be converted to integer
    """

    try:
        _ = int(val)
    except:
        return False

    return True
