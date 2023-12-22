import logging
import os

from chalice import Chalice
from chalice.app import S3Event

from chalicelib import rekognition
from chalicelib import transcribe

app = Chalice(app_name='video-translator')
origin_bucket = os.getenv('ORIGIN_BUCKET_NAME')
destination_bucket = os.getenv('DESTINATION_BUCKET_NAME')


@app.on_s3_event(bucket=origin_bucket, events=['s3:ObjectCreated:*'], suffix='.mp4')
def handle_new_video(event: S3Event):
    rekognition.start_video_label(event.bucket, event.key)
    transcribe.start_transcription_job(event.bucket, event.key, destination_bucket)


@app.on_s3_event(bucket=destination_bucket, events=['s3:ObjectCreated:*'])
def handle_transcription(event: S3Event):
    logging.getLogger('video-translator').debug(f"New transcription detected: {event.bucket}/{event.key}")
