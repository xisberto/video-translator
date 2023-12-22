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
            'SNSTopicArn': os.getenv("AWS_SNS_TOPIC"),
            'RoleArn': os.getenv("AWS_SNS_ROLE")
        },
        JobTag=f"{bucket_name}_{filename}"
    )
