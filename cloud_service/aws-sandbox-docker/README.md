# AWS Sandbox with Docker Compose (LocalStack)

## Requirements
- Docker & Docker Compose
- AWS CLI
- `awslocal` CLI (ติดตั้งด้วย `pip install awscli-local`)

## Setup
1. Clone ไฟล์นี้แล้วแตก zip
2. รัน
   ```bash
   docker compose up -d
   ```



chmod +x ./init.sh
3. ตั้งค่า AWS CLI (ค่าใส่อะไรก็ได้)
   ```bash
   aws configure
   # Access Key: test
   # Secret Key: test
   # Region: ap-southeast-1
   # Output: json
   ```

4. รันสคริปต์ตั้งต้น
   ```bash
   chmod +x init.sh
   ./init.sh
   ```

## Services ที่รวมมา
- Lambda
- API Gateway
- S3
- IAM
- STS
- Logs
- CloudWatch
- Docker Registry (mock ECR)

## การทดสอบ
- Lambda function: `hello-local`
- API Gateway: URL ที่แสดงตอนรัน `init.sh`
- S3: bucket `dev-sandbox-bucket`
- Logs: ใช้ `awslocal logs describe-log-groups`
