import os
import psycopg2
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import redis
# Load environment variables from .env file
load_dotenv()

def test_neon_connection():
    """Simple synchronous database connection test"""
    try:
        # Get connection string from environment
        conn_string = os.getenv('NEON_DATABASE_URL')
        print(conn_string)
        if not conn_string:
            print("Error: NEON_DATABASE_URL not found in environment variables")
            return False
            
        print(f"Attempting to connect with: {conn_string[:50]}...")
        
        # Connect to database
        with psycopg2.connect(conn_string) as conn:
            print("✅ Neon Connection successful!")
            
            # Test a simple query
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"PostgreSQL version: {version[0]}")
                
            return True
            
    except Exception as e:
        print(f"❌ NeonConnection failed: {e}")
        return False

def test_r2_connection():
    """Test connection to Cloudflare R2 bucket using boto3"""
    try:


        # Get credentials and config from environment
        access_key = os.getenv('R2_ACCESS_KEY_ID')
        secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('R2_BUCKET_NAME')
        account_id = os.getenv('R2_ACCOUNT_ID')

        if not all([access_key, secret_key, bucket_name, account_id]):
            print("Error: One or more R2 environment variables are missing.")
            return False

        # R2 endpoint format
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

        # Create boto3 S3 client for R2
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'  # R2 uses 'auto' region
        )

        # Try listing objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        print(f"✅ R2 Connection successful! Bucket '{bucket_name}' is accessible.")
        if 'Contents' in response:
            print(f"Sample object: {response['Contents'][0]['Key']}")
        else:
            print("Bucket is empty.")
        return True

    except ClientError as e:
        print(f"❌ R2 Connection failed (ClientError): {e}")
        return False
    except Exception as e:
        print(f"❌ R2 Connection failed: {e}")
        return False

def test_upstash_redis_connection():
    """Test connection to Upstash Redis using redis-py library"""


    try:
        rest_token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
        rest_url = os.getenv('UPSTASH_REDIS_REST_URL')

        if not all([rest_token, rest_url]):
            print("Error: One or more Upstash Redis environment variables are missing.")
            return False

        # The redis-py library expects a URL in the format:
        # rediss://:<token>@<host>:<port>
        # UPSTASH_REDIS_REST_URL is usually like https://<host>.upstash.io
        # We need to convert it to rediss://:<token>@<host>.upstash.io:port

        # Remove protocol and trailing slash if present
        url = rest_url.replace("https://", "").replace("http://", "").rstrip("/")
        # Upstash Redis typically uses port 6379 for TLS
        redis_url = f"rediss://:{rest_token}@{url}:6379"

        r = redis.Redis.from_url(redis_url)

        pong = r.ping()
        if pong:
            print("✅ Upstash Redis connection successful! PING returned PONG.")
            return True
        else:
            print("❌ Upstash Redis connection failed. PING did not return PONG.")
            return False

    except Exception as e:
        print(f"❌ Upstash Redis connection failed: {e}")
        return False


if __name__ == "__main__":
    test_neon_connection()
    test_r2_connection()   
    test_upstash_redis_connection()