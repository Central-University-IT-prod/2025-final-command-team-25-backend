import boto3
from botocore.client import Config

# Настройка клиента
s3 = boto3.client(
    's3',
    endpoint_url='http://s3:9000', 
    aws_access_key_id='prod_minio',
    aws_secret_access_key='prod_minio',
    config=Config(signature_version='s3v4'),
)


def add_passport(file):
    s3.upload_fileobj(file, 'photos', 'my-photo.jpg')