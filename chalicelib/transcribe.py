import os

import boto3


def start_transcription_job(timestamp: str, orig_bucket: str, filename: str, dest_bucket: str):
    """
    Recebe uma referência a um arquivo mp4 e inicia a transcrição do áudio. O resultado será salvo em um arquivo srt.
    :param timestamp: a hora de início do job em formato ISO
    :param orig_bucket: o nome do bucket de origem
    :param filename: o nome do arquivo mp4
    :param dest_bucket: o nome do bucket de destino
    """
    transc_client = boto3.client('transcribe')
    return transc_client.start_transcription_job(
        TranscriptionJobName=f"{timestamp}__{orig_bucket}__{filename}",
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


def start_translate_job(dest_bucket: str, filename: str):
    """
    Recebe a referência a um arquivo srt e inicia um job de translate para seu conteúdo.
    :param dest_bucket:
    :param filename:
    """
    transl_client = boto3.client('translate')
    return transl_client.start_text_translation_job(
        JobName=f"{dest_bucket}__{filename}",
        InputDataConfig={
            'S3Uri': f"https://{dest_bucket}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/{filename}",
            'ContentType': "text/plain"
        },
        OutputDataConfig={
            'S3Uri': f"https://{dest_bucket}.s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com/"
        }
    )
