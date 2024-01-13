import datetime
import json
import os
import re

import boto3
from chalice import Chalice
from chalice.app import S3Event, SNSEvent

app = Chalice(app_name='video-translator')
app.debug = True

origin_bucket = os.getenv('MEDIA_BUCKET_ORIGIN_NAME')
destination_bucket = os.getenv('MEDIA_BUCKET_DESTINATION_NAME')
default_region = os.getenv('AWS_DEFAULT_REGION')
sns_topic = os.getenv('VIDEO_TOPIC_ARN')
role_arn = os.getenv('VIDEO_ROLE_ARN')


@app.on_s3_event(bucket=origin_bucket, events=['s3:ObjectCreated:*'], suffix='.mp4')
def handle_new_video(event: S3Event):
    """Detecta novo arquivo mp4 no bucket de origem e inicia os trabalhos de Rekognition e Transcribe"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
    filename = re.compile(r"(.*).mp4").match(event.key).groups()[0]
    rek_client = boto3.client('rekognition')
    rek_client.start_label_detection(
        Video={
            'S3Object': {
                'Bucket': event.bucket,
                'Name': event.key
            }
        },
        MinConfidence=80,
        NotificationChannel={
            'SNSTopicArn': sns_topic,
            'RoleArn': role_arn
        },
        JobTag=f"{timestamp}__{event.bucket}__{filename}"
    )
    transc_client = boto3.client('transcribe')
    transc_client.start_transcription_job(
        TranscriptionJobName=f"{timestamp}__{filename}",
        MediaFormat="mp4",
        IdentifyLanguage=True,
        Media={
            'MediaFileUri': f"https://{event.bucket}.s3.{default_region}.amazonaws.com/{event.key}"
        },
        Subtitles={
            'Formats': ['srt']
        },
        OutputBucketName=destination_bucket,
        OutputKey=f"{timestamp}__{filename}/subtitles/"
    )


@app.on_s3_event(bucket=destination_bucket, events=['s3:ObjectCreated:*'], suffix='.srt')
def handle_transcription(event: S3Event):
    """Detecta o fim do trabalho de Transcribe e inicia o trabalho de tradução"""
    app.log.debug(f"New transcription detected: {event.key}")
    transl_client = boto3.client('translate')
    containing_folder = re.compile(r"(.*)/subtitles/.*").match(event.key).groups()[0]
    if containing_folder is None:
        return
    input_uri = f"s3://{event.bucket}/{containing_folder}/subtitles"
    output_uri = f"s3://{destination_bucket}/{containing_folder}/translations"
    app.log.debug(f"Input: {input_uri}")
    app.log.debug(f"Output: {output_uri}")
    transl_client.start_text_translation_job(
        JobName=f"{event.bucket}__{event.key}",
        InputDataConfig={
            'S3Uri': input_uri,
            'ContentType': "text/plain"
        },
        OutputDataConfig={
            'S3Uri': output_uri
        },
        DataAccessRoleArn=role_arn,
        SourceLanguageCode="pt",
        TargetLanguageCodes=["en"]
    )


@app.on_sns_message(topic=sns_topic)
def handle_video_label_detected(event: SNSEvent):
    message = json.loads(event.message)
    app.log.debug(event.message)
    bucket = message['Video']['S3Bucket']
    filename = re.compile(r"(.*).mp4").match(message['Video']['S3ObjectName']).groups()[0]
    app.log.debug(f"New SNS message for {bucket}/{filename}")
    rek_client = boto3.client('rekognition')
    job = rek_client.get_label_detection(
        JobId=message['JobId'],
        SortBy='TIMESTAMP'
    )
    job_tag = job['JobTag']
    timestamp = re.compile(r"(.*)__.*__.*").match(job_tag).groups()[0]
    object_key = f"{timestamp}__{filename}/labels.json"
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(destination_bucket)
    bucket.put_object(Key=object_key, Body=json.dumps(job))
