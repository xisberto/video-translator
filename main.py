import argparse
import os.path

from chalicelib import rekognition, s3, transcribe


def get_parser():
    arg_parser = argparse.ArgumentParser(description="Trabalho para cadeira de Computação em Nuvem 2023.2. "
                                                 "Equipe: Humberto Fraga, Moesio Medieros")
    arg_parser.add_argument('video', help="O arquivo de vídeo que deverá ser trabalhado.", metavar='VIDEO', type=str)
    return arg_parser


def main(filename: str, bucket_name: str):
    if not os.path.exists(filename):
        raise FileNotFoundError("O arquivo informado não existe")
    s3.upload(filename, bucket_name)
    rek_job_id = rekognition.start_video_label(bucket_name, filename)
    transc_job = transcribe.start_transcription_job(bucket_name, filename)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    bkt_name = os.getenv('BUCKET_NAME')
    main(vars(args)['video'], bkt_name)
