import logging

import boto3
import fnmatch

from botocore.exceptions import ClientError

s3 = boto3.client('s3')
response = s3.list_buckets()


def post_image(image_path):
    image_name = image_path.split("/")
    print(image_name)
    filtered = fnmatch.filter(image_name, '*.jpg')
    print(filtered)
    print(type(filtered))
    s3.upload_file(image_path, 'henri-bucket', filtered[0], ExtraArgs={'ACL': 'public-read'})


def create_query_string(values):
    s = ''
    for i in range(len(values)):
        if not s:
            s += 'tag{}={}'.format(i+1, values[i])
        else:
            s += '&tag{}={}'.format(i+1, values[i])
    return s



response = input('Menu \n [1] Upload Image \n [2] Search Images \n')
if response == '1':
    image_path = input('Please provide an absolute path to your image: ')
    try:
        post_image(image_path)
    except ClientError as e:
        logging.error(e)
elif response == '2':
    input = input('Please input the objects that you would like to search for (separated by spaces for multiple tags): \n')
    values = input.split(' ')
    while "" in values:
        values.remove("")
    print(values)
else:
    print('Please provide valid input.')


