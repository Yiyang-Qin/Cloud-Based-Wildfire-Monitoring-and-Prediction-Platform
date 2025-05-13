import boto3
import os

client = boto3.client(
    "ses",
    region_name="us-west-2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY")
)

client.send_email(
    Source="wke9991@gmail.com",
    Destination={"ToAddresses": ["kwang655@usc.edu"]},
    Message={
        "Subject": {"Data": "Test Email from SES"},
        "Body": {
            "Text": {"Data": "Hello, this is a test email without using a custom domain."}
        },
    },
)
