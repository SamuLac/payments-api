"""
AWS S3 Service

Handles all interactions with AWS S3 for receipt storage.
Uses boto3 with credentials loaded from environment variables.
"""

import os
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "payments-receipts-dev")


def get_s3_client():
    """
    Creates and returns a boto3 S3 client.

    Credentials are automatically picked up from environment variables:
    AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
    """
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def upload_receipt_to_s3(file: UploadFile, payment_id: str) -> str:
    """
    Uploads a receipt file to S3 and returns its public URL.
    """
    ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. Use: JPEG, PNG or PDF.",
        )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    s3_key = f"receipts/{payment_id}/{safe_filename}"

    s3 = get_s3_client()

    try:
        s3.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.content_type},
        )
    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload receipt to S3: {str(e)}",
        )

    url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    return url


def delete_receipt_from_s3(s3_url: str) -> bool:
    """
    Deletes a receipt file from S3 given its full URL.
    """
    try:
        key = s3_url.split(".amazonaws.com/")[-1]
        s3 = get_s3_client()
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=key)
        return True
    except ClientError:
        return False
