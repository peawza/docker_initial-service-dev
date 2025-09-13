#!/usr/bin/env bash
set -euo pipefail

EDGE=http://localhost:4566
REGION=ap-southeast-1

echo "Waiting for LocalStack..."
until curl -s ${EDGE}/_localstack/health | grep '"ready": true' >/dev/null 2>&1; do
  sleep 2
done
echo "LocalStack is ready."

BUCKET=dev-sandbox-bucket
awslocal s3 mb s3://$BUCKET || true
awslocal s3 ls

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
awslocal iam create-role   --role-name "$ROLE_NAME"   --assume-role-policy-document "$ASSUME_ROLE_DOC" >/dev/null 2>&1 || true

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
awslocal iam put-role-policy   --role-name "$ROLE_NAME"   --policy-name "$POLICY_NAME"   --policy-document "$LOGS_POLICY_DOC"

ROLE_ARN=$(awslocal iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
echo "Role ARN: $ROLE_ARN"

mkdir -p lambda-src
cat > lambda-src/index.mjs <<'EOF'
export const handler = async (event) => {
  return {
    statusCode: 200,
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ ok: true, message: "Hello from Local Lambda!", event }),
  };
};
EOF

(cd lambda-src && zip -r ../lambda.zip . >/dev/null)
FUNCTION_NAME=hello-local

awslocal lambda create-function   --function-name "$FUNCTION_NAME"   --runtime nodejs18.x   --role "$ROLE_ARN"   --handler index.handler   --zip-file fileb://lambda.zip   --timeout 10   --memory-size 256

awslocal lambda invoke --function-name "$FUNCTION_NAME" /tmp/out.json
cat /tmp/out.json && echo

REST_API_ID=$(awslocal apigateway create-rest-api --name dev-sandbox-api --query 'id' --output text)
PARENT_ID=$(awslocal apigateway get-resources --rest-api-id "$REST_API_ID" --query 'items[0].id' --output text)
RESOURCE_ID=$(awslocal apigateway create-resource --rest-api-id "$REST_API_ID" --parent-id "$PARENT_ID" --path-part "hello" --query 'id' --output text)

awslocal apigateway put-method   --rest-api-id "$REST_API_ID"   --resource-id "$RESOURCE_ID"   --http-method GET   --authorization-type "NONE"

awslocal apigateway put-integration   --rest-api-id "$REST_API_ID"   --resource-id "$RESOURCE_ID"   --http-method GET   --type AWS_PROXY   --integration-http-method POST   --uri arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:000000000000:function:${FUNCTION_NAME}/invocations

awslocal lambda add-permission   --function-name "$FUNCTION_NAME"   --statement-id api-gw-invoke   --action lambda:InvokeFunction   --principal apigateway.amazonaws.com   --source-arn arn:aws:execute-api:${REGION}:000000000000:${REST_API_ID}/*/GET/hello

awslocal apigateway create-deployment   --rest-api-id "$REST_API_ID"   --stage-name dev

API_URL="http://localhost:4566/restapis/${REST_API_ID}/dev/_user_request_/hello"
echo "API URL: $API_URL"
curl -s "$API_URL" | jq .

echo "Log groups:"
awslocal logs describe-log-groups --query 'logGroups[].logGroupName'
