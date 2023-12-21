import boto3


def start_transcription_job(bucket_name: str, filename: str):
    transc_client = boto3.client('transcribe')
    return transc_client.start_transcription_job(
        TranscriptionJobName=f"{bucket_name}__{filename}",
        MediaFormat="mp4",
        Media={
            'MediaFileUri': f"https://{bucket_name}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/{filename}"
        }
    )
