import logging
import os

from chalice import Chalice
from chalice.app import S3Event

from chalicelib import rekognition
from chalicelib import transcribe

app = Chalice(app_name='video-translator')
origin_bucket = os.getenv('MEDIA_BUCKET_ORIGIN_NAME')
destination_bucket = os.getenv('MEDIA_BUCKET_DESTINATION_NAME')


@app.on_s3_event(bucket=origin_bucket, events=['s3:ObjectCreated:*'], suffix='.mp4')
def handle_new_video(event: S3Event):
    """Detecta novo arquivo mp4 no bucket de origem e inicia os trabalhos de Rekognition e Transcribe"""
    rekognition.start_video_label(event.bucket, event.key)
    transcribe.start_transcription_job(event.bucket, event.key, destination_bucket)


@app.on_s3_event(bucket=destination_bucket, events=['s3:ObjectCreated:*'])
def handle_transcription(event: S3Event):
    """Detecta o fim do trabalho de Transcribe e inicia o trabalho de tradução"""
    logging.getLogger('video-translator').debug(f"New transcription detected: {event.bucket}/{event.key}")
