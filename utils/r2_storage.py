import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

access_key = os.getenv('R2_ACCESS_KEY_ID')
secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
bucket_name = os.getenv('R2_BUCKET_NAME', 'brahminet-memes')
account_id = os.getenv('R2_ACCOUNT_ID')

s3_client = None

if all([access_key, secret_key, account_id]):
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto'
    )
else:
    print("Warning: R2 Credentials not fully configured in environment.")

def upload_image(file_obj, object_name: str, content_type: str = "image/jpeg"):
    """
    Upload a file object to Cloudflare R2 bucket.
    """
    if not s3_client:
        raise ValueError("R2 Client not initialized")
    
    try:
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            object_name,
            ExtraArgs={'ContentType': content_type}
        )
        return True
    except ClientError as e:
        print(f"Error uploading to R2: {e}")
        return False

def get_image_url(object_name: str):
    """
    Get public or presigned URL for an image.
    Assuming the bucket is configured for public access or returning presigned URL.
    """
    if not s3_client:
        return None
    # For a private bucket you might generate a presigned URL:
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=3600
        )
        return url
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None
