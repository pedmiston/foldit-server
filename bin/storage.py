from os import environ
from minio import Minio
from minio.error import ResponseError

client = Minio('nyc3.digitaloceanspaces.com',
               access_key=environ['DO_ACCESS_KEY'],
               secret_key=environ['DO_SECRET_KEY'],
               secure=True)
