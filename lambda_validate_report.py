import json
import boto3
import urllib.parse
from datetime import datetime

sqs = boto3.client('sqs')

QUEUE_URL = 'https://sqs.ap-south-2.amazonaws.com/875219073276/disaster-alert-queue'

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        raw_key = record['s3']['object']['key']
        key = urllib.parse.unquote_plus(raw_key)

        allowed_extensions = ('.jpg', '.jpeg', '.png', '.pdf', '.txt')
        if not key.lower().endswith(allowed_extensions):
            print(f"Rejected file (invalid type): {key}")
            continue

        message = {
            'bucket': bucket,
            'file_key': key,
            'uploaded_at': datetime.utcnow().isoformat(),
            'status': 'validated'
        }

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        print(f"Validated and queued report: {key}")

    return {
        'statusCode': 200,
        'body': json.dumps('Validation complete')
    }
