import argparse
import json
import os

import boto3
from botocore.config import Config
from dotenv import dotenv_values

# Cria os recursos utilizados pelo sistema, e cadastra seus nomes como environment_variables na config do Chalice

# O arquivo .env deve existir com as variáveis abaixo:
# ORIGIN_BUCKET_NAME
# DESTINATION_BUCKET_NAME
# AWS_SNS_TOPIC
# AWS_DEFAULT_REGION

# Permissões para estes recursos devem ser definidas posteriormente

config = dotenv_values(".env")
aws_config = Config(
    region_name=config.get('AWS_DEFAULT_REGION')
)

BUCKETS = [
    {
        'usage': 'ORIGIN',
        'name': config.get('ORIGIN_BUCKET_NAME'),
        'region': config.get('AWS_DEFAULT_REGION'),
        'acl': 'private'
    },
    {
        'usage': 'DESTINATION',
        'name': config.get('DESTINATION_BUCKET_NAME'),
        'region': config.get('AWS_DEFAULT_REGION'),
        'acl': 'private'
    }
]

SNS_TOPICS = [
    {
        'name': config.get('AWS_SNS_TOPIC')
    }
]


def _already_in_config(env_var: str, stage: str) -> bool:
    with open(os.path.join('.chalice', 'config.json'), 'r') as f:
        return env_var in json.load(f)['stages'].get(stage, {}).get('environment_variables', {})


def record_as_env(key: str, value: str, stage: str):
    chalice_config = os.path.join('.chalice', 'config.json')
    with open(chalice_config, 'r') as f:
        data = json.load(f)
        data['stages'].setdefault(stage, {}).setdefault('environment_tables', {})[key] = value
    with open(chalice_config, 'w') as f:
        serialized = json.dumps(data, indent=2, separators=(',', ': '))
        f.write(serialized + '\n')


def create_bucket(bucket_config, stage: str) -> str:
    bucket_name = f"{stage}-{bucket_config['name']}"
    client = boto3.client('s3', config=aws_config)
    try:
        client.create_bucket(
            Bucket=bucket_name,
            ACL=bucket_config['acl'],
            CreateBucketConfiguration={
                'LocationConstraint': bucket_config['region']
            }
        )
    except:
        pass
    return bucket_name


def create_topic(topic_config, stage: str) -> str:
    client = boto3.client('sns', config=aws_config)
    topic_name = f"{stage}-{topic_config['name']}"
    client.create_topic(
        Name=topic_name,
        Attributes={
            'FifoTopic': 'true'
        }
    )
    return topic_name


def create_resources(stage: str):
    for bucket in BUCKETS:
        if _already_in_config(bucket['name'], stage):
            continue
        print(f"Creating bucket {bucket['name']}")
        bucket_name = create_bucket(bucket, stage)
        record_as_env(f"{bucket['usage']}_BUCKET_NAME", bucket_name, stage)
    for topic in SNS_TOPICS:
        if _already_in_config(topic['name'], stage):
            continue
        print(f"Creating SNS Topic {topic['name']}")
        topic_name = create_topic(topic, stage)
        record_as_env("AWS_SNS_TOPIC", topic_name, stage)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage', default='dev')
    args = parser.parse_args()
    create_resources(args.stage)


if __name__ == '__main__':
    main()
