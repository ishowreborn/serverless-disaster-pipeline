# Serverless Disaster Alert Pipeline
# Serverless Disaster Alert Pipeline

This is my second AWS project - a serverless pipeline that automatically alerts someone when a new disaster report gets uploaded. Built this to learn a fuller event-driven chain than my first project (S3, SQS, and two Lambdas talking to each other, plus SNS for actual notifications).

Basically: someone uploads a report (image, PDF, or text file) describing a local issue, and within seconds an email alert goes out with the report details.

## How it works

1. A report file gets uploaded to the input S3 bucket.
2. S3 triggers a Lambda function that validates the file type and packages the metadata into a message.
3. That message goes into an SQS queue.
4. A second Lambda picks up the message from the queue.
5. That Lambda publishes an alert to an SNS topic, which sends out an email notification.

## Stack I used

- S3 - stores the uploaded report files
- SQS - decouples validation from alerting, adds retry and dead-letter handling
- Lambda (Python 3.13), two functions - one validates and queues, one sends the alert
- SNS - handles the actual email notification delivery
- IAM - separate custom policies per Lambda, scoped to only what each one needs

## Files in this repo

- lambda_validate_report.py - first Lambda, validates uploaded files and sends a message to SQS
- lambda_send_alert.py - second Lambda, reads from SQS and publishes an alert to SNS
## Bugs I ran into (and how I fixed them)

This project had more moving parts than my first one, so debugging took longer, but each issue taught me something real:

- Mixed up which IAM role needed which permission - I have two separate Lambda functions with two separate roles. Early on I attached an SQS permission to the wrong Lambda's role by mistake. Lesson learned: always double check which function you are actually configuring, especially when tab names look similar.
- SQS trigger would not attach to the second Lambda - same root cause as my first project, the default Lambda role only has logging permissions. Had to manually attach AWSLambdaSQSQueueExecutionRole before the trigger would connect.
- SNS email confirmations kept silently failing - this was the strangest bug I hit. I would subscribe my email, get the confirmation email, click confirm, and moments later get ANOTHER email saying my subscription had been deactivated. Turns out Gmail automatically scans and prefetches every link in incoming emails as a security measure, including the unsubscribe link sitting right next to the confirm link in AWS's confirmation email. Gmail's scanner was auto-clicking unsubscribe before I ever got the chance to. I confirmed this was actually happening by checking CloudWatch logs, which showed my Lambda functions successfully calling sns.publish() every single time, proving the pipeline logic was correct even though no email was arriving. I eventually tested with a temporary, non-Gmail email address and the alert came through immediately, which confirmed the issue was Gmail's link-scanning behavior, not my code.

