import os

import boto3


def start_transcription_job(orig_bucket: str, filename: str, dest_bucket: str):
    transc_client = boto3.client('transcribe')
    return transc_client.start_transcription_job(
        TranscriptionJobName=f"{orig_bucket}__{filename}",
        MediaFormat="mp4",
        IdentifyLanguage=True,
        Media={
            'MediaFileUri': f"https://{orig_bucket}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/{filename}"
        },
        Subtitles={
            'Formats': ['srt']
        },
        OutputBucketName=dest_bucket
    )
