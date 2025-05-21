# Base image
FROM python:3.13.0-slim

# Declare build-time args
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG TABLE_HISTORY
ARG DYNAMODB_ENDPOINT

# Set environment variables
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV TABLE_HISTORY=${TABLE_HISTORY}
ENV DYNAMODB_ENDPOINT=${DYNAMODB_ENDPOINT}

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl unzip

# Install AWS CLI
RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Configure AWS CLI
RUN mkdir -p ~/.aws && \
    aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID --profile localstack && \
    aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY --profile localstack && \
    aws configure set region $AWS_DEFAULT_REGION --profile localstack

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app files
COPY lib /app/lib
COPY app.py .

# Setup Localstack init script
COPY localstack/init-aws.sh /app/localstack/init-aws.sh
RUN chmod +x /app/localstack/init-aws.sh

# Launch FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
