#!/usr/bin/env bash
set -euo pipefail

EDGE=http://localstack:4566     # <— สำคัญ: ใช้ hostname ของ service
REGION=ap-southeast-1

echo "Waiting for LocalStack..."
until curl -s ${EDGE}/_localstack/health | grep '"ready": true' >/dev/null 2>&1; do
  sleep 2
done
echo "LocalStack is ready."

# ---------- S3 ----------
BUCKET=dev-sandbox-bucket
awslocal --endpoint-url ${EDGE} s3 mb s3://$BUCKET || true
awslocal --endpoint-url ${EDGE} s3 ls

# ---------- IAM Role for Lambda ----------
ROLE_NAME=lambda-exec-role
POLICY_NAME=lambda-basic-logs
ASSUME_ROLE_DOC='{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}'
awslocal --endpoint-url ${EDGE} iam create-role \
  --role-name "$ROLE_NAME" \
  --assume-role-policy-document "$ASSUME_ROLE_DOC" >/dev/null 2>&1 || true

LOGS_POLICY_DOC='{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect":"Allow",
    "Action":[
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ],
    "Resource":"*"
  }]
}'
awslocal --endpoint-url ${EDGE} iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "$POLICY_NAME" \
  --policy-document "$LOGS_POLICY_DOC"

ROLE_ARN=$(awslocal --endpoint-url ${EDGE} iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
echo "Role ARN: $ROLE_ARN"

# ---------- Lambda (ทำ zip ด้วย python แทน 'zip' เพื่อไม่ต้องติดตั้งเพิ่ม) ----------
mkdir -p /tmp/lambda-src
cat >/tmp/lambda-src/index.mjs <<'EOF'
export const handler = async (event) => {
  return {
    statusCode: 200,
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ ok: true, message: "Hello from Local Lambda!", event }),
  };
};
EOF

# สร้าง zip โดยใช้ python (เลี่ยงการพึ่งพาแพ็กเกจ 'zip')
python3 - <<'PY'
import zipfile, os
zf = zipfile.ZipFile('/tmp/lambda.zip','w',zipfile.ZIP_DEFLATED)
zf.write('/tmp/lambda-src/index.mjs','index.mjs')
zf.close()
PY

FUNCTION_NAME=hello-local
# ถ้ามีอยู่แล้วให้ลบก่อน (ป้องกัน error จาก set -e)
awslocal --endpoint-url ${EDGE} lambda delete-function --function-name "$FUNCTION_NAME" >/dev/null 2>&1 || true

awslocal --endpoint-url ${EDGE} lambda create-function \
  --function-name "$FUNCTION_NAME" \
  --runtime nodejs18.x \
  --role "$ROLE_ARN" \
  --handler index.handler \
  --zip-file fileb:///tmp/lambda.zip \
  --timeout 10 \
  --memory-size 256

awslocal --endpoint-url ${EDGE} lambda invoke --function-name "$FUNCTION_NAME" /tmp/out.json >/dev/null 2>&1 || true
echo "Lambda invoke output:"
cat /tmp/out.json || true
echo

# ---------- API Gateway ----------
REST_API_ID=$(awslocal --endpoint-url ${EDGE} apigateway create-rest-api --name dev-sandbox-api --query 'id' --output text)
PARENT_ID=$(awslocal --endpoint-url ${EDGE} apigateway get-resources --rest-api-id "$REST_API_ID" --query 'items[0].id' --output text)
RESOURCE_ID=$(awslocal --endpoint-url ${EDGE} apigateway create-resource --rest-api-id "$REST_API_ID" --parent-id "$PARENT_ID" --path-part "hello" --query 'id' --output text)

awslocal --endpoint-url ${EDGE} apigateway put-method \
  --rest-api-id "$REST_API_ID" \
  --resource-id "$RESOURCE_ID" \
  --http-method GET \
  --authorization-type "NONE"

awslocal --endpoint-url ${EDGE} apigateway put-integration \
  --rest-api-id "$REST_API_ID" \
  --resource-id "$RESOURCE_ID" \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:000000000000:function:${FUNCTION_NAME}/invocations

awslocal --endpoint-url ${EDGE} lambda add-permission \
  --function-name "$FUNCTION_NAME" \
  --statement-id api-gw-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn arn:aws:execute-api:${REGION}:000000000000:${REST_API_ID}/*/GET/hello

awslocal --endpoint-url ${EDGE} apigateway create-deployment \
  --rest-api-id "$REST_API_ID" \
  --stage-name dev

API_URL="http://localhost:4566/restapis/${REST_API_ID}/dev/_user_request_/hello"
echo "API URL: $API_URL"
echo "API response:"
curl -s "$API_URL" || true
echo

echo "Log groups:"
awslocal --endpoint-url ${EDGE} logs describe-log-groups --query 'logGroups[].logGroupName' || true

echo "✅ init.sh finished."
