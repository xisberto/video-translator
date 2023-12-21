import boto3


def upload(filename: str, bucket_name: str):
    s3_resource = boto3.client('s3')
    bucket = s3_resource.Bucket(bucket_name)
    with open(filename, 'rb') as data:
        bucket.put_object(Key=filename, Body=data)
