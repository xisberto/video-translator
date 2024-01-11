import json
import os

import boto3


def start_video_label(bucket_name: str, filename: str):
    rek_client = boto3.client('rekognition')
    return rek_client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': filename
            }
        },
        MinConfidence=80,
        NotificationChannel={
            'SNSTopicArn': os.getenv("VIDEO_TOPIC_ARN"),
            'RoleArn': os.getenv("VIDEO_ROLE_ARN")
        },
        JobTag=f"{bucket_name}_{filename}"
    )


def save_label_detection(message: dict):
    rek_client = boto3.client('rekognition')
    job = rek_client.get_label_detection(
        JobId=message['JobId'],
        SortBy='TIMESTAMP'
    )
    object_key = f"{message['Video']['S3ObjectName']}-labels.json"
    s3_resource = boto3.client('s3')
    bucket = s3_resource.Bucket(os.getenv('MEDIA_BUCKET_DESTINATION_NAME'))
    bucket.put_object(Key=object_key, Body=json.dumps(job))
