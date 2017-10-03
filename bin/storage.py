import json
from os import environ
from minio import Minio
from minio.error import ResponseError

bucket = 'foldit'
client = Minio('nyc3.digitaloceanspaces.com',
               access_key=environ['DO_ACCESS_KEY'],
               secret_key=environ['DO_SECRET_KEY'],
               secure=True)
objs = client.list_objects_v2(bucket)
for obj in objs:
    resp = client.get_object(bucket, obj.object_name)
    for line in resp.readlines():
        data = json.loads(line)
        print(data.keys())
        print(data['FILEPATH'])
