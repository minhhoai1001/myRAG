import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET = os.getenv("S3_BUCKET", "insightscanx")

def make_s3_key(knowledge_name: str, doc_id: str) -> str:
    return f"knowledge-data/{knowledge_name}/{doc_id}"

def s3_key_exists(bucket: str, key: str) -> bool:
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True  # file already exists
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False  # file chưa có
        raise 

def presign_put_url(key: str, content_type: str = None, expires=900):
    params = {'Bucket': BUCKET, 'Key': key}
    if content_type:
        params['ContentType'] = content_type
    
    presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params=params,
            ExpiresIn=expires
    )
    
    return presigned_url

def presign_delete_url(key: str, expires=900):
    params = {'Bucket': BUCKET, 'Key': key}
    
    presigned_url = s3_client.generate_presigned_url(
            'delete_object',
            Params=params,
            ExpiresIn=expires
    )
    
    return presigned_url

def delete_s3_object(key: str):
    """Delete an object from S3"""
    try:
        s3_client.delete_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError as e:
        print(f"Error deleting S3 object {key}: {e}")
        raise
