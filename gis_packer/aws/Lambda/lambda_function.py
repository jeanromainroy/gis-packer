# Add path to layers
import sys
sys.path.append('/opt/')

# other libs
import os
import shutil
import tempfile
import json
import boto3
import requests

import numpy as np
import cv2 as cv


def clear_tmp():
    """
        Clears the temp folder
    """

    folder = '/tmp'
    for filename in os.listdir(folder):

        if('.pt' in filename):
            continue

        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def get_file(url):
    """
        Get a file from a URL
    """

    # request object from S3
    response = bucket.Object(key=image_key).get()

    # grab image
    imgBytes = response['Body'].read()

    # Init temp file
    tmp = tempfile.NamedTemporaryFile()

    # save file to temp folder
    with open(tmp.name, 'wb') as fh:
        fh.write(imgBytes)

    # load image file with opencv
    img = cv.imread(tmp.name)

    # if could not load
    if(img is None or type(img) is not np.ndarray):
        img = None

    return img, tmp.name


def lambda_handler(event, context):

    # grab inputs from body
    if 'url' not in event or event['url'] is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Must provide file url')
        }

    url = event['url']

    # validate
    if not isinstance(url, str):
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid url')
        }

    # get file
    try:
        img, img_path = get_image(bucket, f'{SHARDED_PATH}{image_id}/src.jpg')
    except:
        return {
            'statusCode': 500,
            'body': json.dumps('Error occurred when trying to load the image')
        }

    # if could not load
    if(img is None):
        return {
            'statusCode': 500,
            'body': json.dumps('Could not load image')
        }

    # clear tmp folder
    clear_tmp()

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
