import json
import boto3

sns = boto3.client('sns')

TOPIC_ARN = 'arn:aws:sns:ap-south-2:875219073276:disaster-alert-topic'

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])

        message = f"DISASTER REPORT ALERT

File: {body.get('file_key')}
Bucket: {body.get('bucket')}
Uploaded at: {body.get('uploaded_at')}
Status: {body.get('status')}

Please review this report as soon as possible."

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='New Disaster Report Received',
            Message=message
        )

        print(f"Alert sent for: {body.get('file_key')}")

    return {
        'statusCode': 200,
        'body': json.dumps('Alert sent')
    }
