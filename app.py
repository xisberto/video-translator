import datetime
import json
import os

from chalice import Chalice
from chalice.app import S3Event, SNSEvent

from chalicelib import rekognition
from chalicelib import transcribe

app = Chalice(app_name='video-translator')
app.debug = True
origin_bucket = os.getenv('MEDIA_BUCKET_ORIGIN_NAME')
destination_bucket = os.getenv('MEDIA_BUCKET_DESTINATION_NAME')
sns_topic = os.getenv('VIDEO_TOPIC_ARN')


@app.on_s3_event(bucket=origin_bucket, events=['s3:ObjectCreated:*'], suffix='.mp4')
def handle_new_video(event: S3Event):
    """Detecta novo arquivo mp4 no bucket de origem e inicia os trabalhos de Rekognition e Transcribe"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H.%M.%S")
    rekognition.start_video_label(timestamp, event.bucket, event.key)
    transcribe.start_transcription_job(timestamp, event.bucket, event.key, destination_bucket)


@app.on_s3_event(bucket=destination_bucket, events=['s3:ObjectCreated:*'], suffix='.srt')
def handle_transcription(event: S3Event):
    """Detecta o fim do trabalho de Transcribe e inicia o trabalho de tradução"""
    app.log.debug(f"New transcription detected: {event.bucket}/{event.key}")


@app.on_sns_message(topic=sns_topic)
def handle_video_label_detected(event: SNSEvent):
    message = json.loads(event.message)
    app.log.debug(event.message)
    bucket = message['Video']['S3Bucket']
    filename = message['Video']['S3ObjectName']
    app.log.debug(f"New SNS message for {bucket}/{filename}")
    rekognition.save_label_detection(message)
