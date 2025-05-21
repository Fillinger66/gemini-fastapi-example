#!/bin/bash
set -x

echo "Start creating '$TABLE_HISTORY' with endpoint '$DYNAMODB_ENDPOINT' from '$AWS_DEFAULT_REGION'" 
# Create DynamoDB table with session_id as the hash key of type S
output=$(aws dynamodb create-table \
    --table-name "$TABLE_HISTORY" \
    --attribute-definitions AttributeName=session_id,AttributeType=S \
    --key-schema AttributeName=session_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url "$DYNAMODB_ENDPOINT" \
    --region "$AWS_DEFAULT_REGION")

echo "$output"

#Put item into the table
echo "Start putting item into '$TABLE_HISTORY'"
output=$(aws dynamodb put-item \
    --table-name "$TABLE_HISTORY" \
    --item "{\"session_id\": {\"S\": \"123\"}, \"history\": {\"S\": \"[{\\\"role\\\": \\\"user\\\",\\\"parts\\\": \\\"Tell me a joke\\\"},{\\\"role\\\": \\\"model\\\",\\\"parts\\\": \\\"Why don't scientists trust atoms?\\\\n\\\\nBecause they make up everything!\\\\n\\\"}]\"}}" \
    --endpoint-url "$DYNAMODB_ENDPOINT" \
    --region "$AWS_DEFAULT_REGION"
)

echo "$output"






