import json
import os
import re

import boto3


def start_video_label(timestamp: str, bucket_name: str, filename: str):
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
        JobTag=f"{timestamp}__{bucket_name}__{filename}"
    )


def save_label_detection(message: dict):
    rek_client = boto3.client('rekognition')
    job = rek_client.get_label_detection(
        JobId=message['JobId'],
        SortBy='TIMESTAMP'
    )
    job_tag = job['JobTag']
    timestamp = re.compile(r"(.*)__.*__.*").match(job_tag).groups()[0]
    object_key = f"{timestamp}__{message['Video']['S3Bucket']}__{message['Video']['S3ObjectName']}-labels.json"
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(os.getenv('MEDIA_BUCKET_DESTINATION_NAME'))
    bucket.put_object(Key=object_key, Body=json.dumps(job))
