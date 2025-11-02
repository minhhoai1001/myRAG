import boto3, os, uuid
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3", 
    endpoint_url=os.getenv("MINIO_ENDPOINT_URL"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    config=boto3.session.Config(signature_version='s3v4')
)
BUCKET = os.getenv("S3_BUCKET")

def make_s3_key(knowledge_id: str, doc_id: str, filename: str) -> str:
    return f"knowledge/{knowledge_id}/{filename}"

def presign_put_url(bucket: str, key: str, content_type: str, ttl=900):
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=ttl,
    )
