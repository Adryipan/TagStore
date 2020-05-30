import logging
import boto3
import fnmatch
from botocore.exceptions import ClientError
import requests


def post_image(image_path):


    if image_path.find("\\"):
        image_name = image_path.split('\\')
        print(image_name)

    elif image_path.find("/"):
        image_name = image_path.split("/")
        print(image_name)
    
    else:
        print("incorrect path provided")

    filtered = fnmatch.filter(image_name, '*.jpg')
    bucket=input("Please enter the bucket you want to upload to \n (Note: Only Bucket Available is fit5225-a2-team) \n")
    s3.upload_file(image_path, bucket, filtered[0], ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})


def create_query_string(values):
    s = ''
    URL="https://8wl1a323h1.execute-api.us-east-1.amazonaws.com/prod/api/search?" 
    for i in range(len(values)):
        if not s:
            s += "tag{}={}".format(i+1, values[i])
        else:
            s += "&tag{}={}".format(i+1, values[i])
    URL+=s
    r = requests.get(url=URL)
    print(r.json())


def main():

    response = input("Menu \n [1] Upload Image \n [2] Search Images \n")

    if response == '1':
        image_path = input('Please provide an absolute path to your image: ')
        try:
            post_image(image_path)
        except ClientError as e:
            logging.error(e)
    elif response == '2':
        inPut = input('Please input the objects that you would like to search for (separated by spaces for multiple tags): \n')
        values = inPut.split(' ')
        while "" in values:
            values.remove("")

        create_query_string(values)

    else:
        print('Please provide valid input.')

if __name__ == "__main__":
    s3 = boto3.client('s3')
    main()    
