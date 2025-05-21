# Gemini API

#### **Hi! 👋 This is a small Python project demonstrating how to interact with Gemini to create a chat under a simple API using [FastAPI](https://fastapi.tiangolo.com/), [LocalStack](https://github.com/localstack/localstack), and [Docker](https://www.docker.com/).** 

#### **The API stores chat history using **DynamoDB**, which is emulated locally via **LocalStack**. At the end of the setup, you'll have a Docker container running a FastAPI server connected to Gemini and DynamoDB.**

#### **Also there is a small GUI Application using PyQt6 to interact with the API.**

<br>

---

# 📚 Table of Contents

1.  [Features](#features)
2.  [Project Structure](#project-structure)
3.  [Prerequisites](#prerequisites)
4.  [FastAPI Application (app.py)](#fastapi-application-app.py)
    * [API Endpoints](#api-endpoints)
        * [POST `/chat/`](#post-chat)
        * [GET `/describe-table`](#get-describe-table)
        * [GET `/get-item/{session_id}`](#get-item-session_id)
        * [GET `/docs`](#get-docs)
    * [Core Components](#core-components)
    * [Dependencies](#dependencies)
5.  [How to Run](#how-to-run)
    * [Gemini API Key](#gemini-api-key)
    * [.env File Example](#env-file-example)
    * [Docker Container](#docker-container)
        * [Step 1: Add Your API Key](#step-1-add-your-api-key)
        * [Step 2: Build and Run](#step-2-build-and-run)
        * [Step 3: Stop the Container](#step-3-stop-the-container)
        * [Step 4: Restart the Container](#step-4-restart-the-container)
    * [Logs](#logs)
    * [DynamoDB](#dynamodb)
        * [Verify Table Creation](#verify-table-creation)
6.  [Dockerfile Breakdown](#dockerfile-breakdown)
    * [Base Image](#base-image)
    * [Environment Variables](#environment-variables)
    * [System Dependencies](#system-dependencies)
    * [AWS CLI Installation](#aws-cli-installation)
    * [AWS Profile Configuration](#aws-profile-configuration)
    * [Application Setup](#application-setup)
    * [LocalStack Initialization](#localstack-initialization)
    * [Container Entry Point](#container-entry-point)
7.  [Docker Compose Setup](#docker-compose-setup)
    * [Features](#features-1)
    * [docker-compose.yml](#docker-compose.yml)
    * [What It Does](#what-it-does)
    * [Run the Containers](#run-the-containers)
    * [Check Logs](#check-logs)
    * [Notes](#notes)
8.  [Chat GUI (PyQt6)](#chat-gui-pyqt6)
    * [Features](#features-2)
    * [Requirements](#requirements)
    * [Running the GUI](#running-the-gui)
9.  [API Testing Tips](#api-testing-tips)
10. [License](#license)


<br>

# 🚀 Features

* 🔌 FastAPI backend connected to Gemini
* 🗂️ Chat history persistence via DynamoDB
* 🐳 Containerized with Docker
* 🌐 Local AWS service emulation using LocalStack

---
<br>

# 📁 Project Structure

```bash
gemini-api/
├── Dockerfile           # Dockerfile 
├── docker-compose.yml   # Docker compose file
├── requirements.txt     # Dependencies for API
├── app.py               # API
├── LICENSE              # Educational and Non-Commercial Use License
├── postman/
│   └── ...              # Simple postman collection
├── lib/
│   └── DynamoWrapper.py # Wrapper to interact with DynamoDb
│   └── GeminiWrapper.py # Wrapper to interact with Gemini
│   └── ChatContent.py   # Mapper class to convert history
├── ui/
│   └── ChatApp.py       # GUI app
│   └── requirements.txt # dependencies needed to run GUI app
│   └── assets/          # assets for GUI app
└── localstack/
    └── init-aws.sh      # Script to initialize DynamoDB

```
---

<br><br> 

# 🧰 Prerequisites

* [Docker](https://www.docker.com/)
* [Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key?hl=fr)
* [Python](https://www.python.org/)

---

<br><br>

# ⚙️ **FastAPI Application (app.py)**

**This application exposes a REST API to interact with Google Gemini Pro, storing and retrieving conversation history in DynamoDB (via LocalStack).**

**It integrates:**

* 🌐 **FastAPI for the web framework**

* 🧠 **GeminiWrapper for chatting with Google's Gemini API**

* 💾 **DynamoWrapper for accessing chat history stored in DynamoDB**

* **🧩 ChatContent model for serializing history messages**

<br>

## 📋 **API Endpoints**

### 📬 **POST `/chat/`**

**Send a user message to Gemini and get a response.**

**Request:**

```json
{
  "user_input": "Can you tell me a joke?",
  "session_id": "123"
}
```

**Curl Example:**

```bash
curl -X POST http://127.0.0.1:8000/chat/ \
     -H "Content-Type: application/json" \
     -d '{"user_input": "Can you tell me a joke?", "session_id": "123"}'
```

**Response:**
```json
{
    "session_id": "123",
    "role": "model",
    "response": "Okay, here's one:\n\nWhy did the scarecrow win an award?\n\nBecause he was outstanding in his field!\n"
}
```
---


### 📄 **GET `/describe-table`**

**Check the status of the `ChatHistory` table.**

**Response:**

```json
{
  "status": "ACTIVE"
}
```

---

### 📂 **GET `/get-item/{session_id}`**

**Get chat history for a given session ID.**

**Example Response:**

```json
{
    "session_id": "123",
    "history": [
        {
            "role": "user",
            "parts": "Tell me a joke"
        },
        {
            "role": "model",
            "parts": "Why don't scientists trust atoms?\n\nBecause they make up everything!\n"
        }
    ]
}
```
### 📂 **GET `/docs`**

**Use this route in your browser to explore API with [Swagger](https://swagger.io/)**

<br>

## 🧱 **Core Components**

* **ChatRequest: A Pydantic model for request validation**

* **startChat(prompt, session_id, history): Handles chat lifecycle and saves history**

* **saveHistory(session_id, history): Persists structured chat history into DynamoDB**

* **getDynamoHistory(session_id): Fetches existing history for a session**

<br>

## 📂 **Dependencies**

**Your lib/ directory should include:**

* ### **```GeminiWrapper.py```**

  **A class that wraps interaction with the Google Gemini API.**
**Handles chat session management, context handling, and response.**
**Used internally by /chat endpoints.**

* ### **```DynamoWrapper.py```**: 
  
  **Provides abstraction over DynamoDB access.**
**Used to read/write session history and manage table metadata (e.g. in ```/describe-table```).**

* ### **```ChatContent.py```**: 
  
  **Model for serializing chat messages for storage**

<br><br>

# ⚙️ How to Run

## Gemini API Key

4**To use Gemini, you need an API key. Get one [here](https://ai.google.dev/gemini-api/docs/api-key?hl=fr).**

## 🔐 .env File Example
### Create a .env file at the root of the project to securely manage environment variables:
```ini
GEMINI_API_KEY=<YOUR_API_KEY_HERE>
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=stack
AWS_DEFAULT_REGION=us-west-2
TABLE_HISTORY=ChatHistory
DYNAMODB_ENDPOINT=http://localstack:4566
```

## **Docker Container**

**This project uses **Docker Compose** to build and run two containers:**

1. **LocalStack** – simulates AWS services locally.
2. **Gemini API** – simulates a backend server (like an AWS EC2 instance).

### **Step 1: Add Your API Key**

### **If not already done, create a .env file at the root of the project to securely manage environment variables:**

**Will be used in ```docker-compose.yml```**
```yaml
...
environment:
  - GEMINI_API_KEY=${GEMINI_API_KEY}
...
```

### **Step 2: Build and Run**

**From the project root, run:**

*(-d for detach so your terminal will be free for other use after start)*

***This will pull localstack image if you don't already have one and construct the £API image right after***

```bash
docker-compose up -d --build
...
[+] Building 1.9s (17/17) FINISHED                                                                                                                                                      
 => [gemini-api internal] load build definition from Dockerfile                                                                                                                
 => => transferring dockerfile: 1.29kB                                                                                                                                                         
 => [gemini-api internal] load metadata for docker.io/library/python:3.13.0-slim     
 => [gemini-api internal] load .dockerignore                                                                                                              
 => => transferring context: 2B                                                                                                                                                           
 => [gemini-api  1/12] FROM docker.io/library/python:3.13.0-slim@sha256:0de818129b26ed8f46fd772f540c80e277b67a28229531a1ba0fdacfaed19bcb                                                                               
 => [gemini-api internal] load build context                                                                                                                                                      
 => => transferring context: 20.75kB                                                                                                                                                         
 => CACHED [gemini-api  2/12] RUN apt-get update && apt-get install -y --no-install-recommends curl unzip                                                                                                                                                        
 => CACHED [gemini-api  3/12] RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install                                                                                                           
 => CACHED [gemini-api  4/12] RUN mkdir -p ~/.aws                                                                                                                                                          
 => CACHED [gemini-api  5/12] RUN aws configure set aws_access_key_id local --profile localstack && aws configure set aws_secret_access_key stack --profile localstack && aws configure set region us-west-2 --profile localstack                                             
 => CACHED [gemini-api  6/12] WORKDIR /app                                                                                                                                                          
 => CACHED [gemini-api  7/12] COPY requirements.txt .                                                                                                                                                        
 => CACHED [gemini-api  8/12] RUN pip install -r requirements.txt                                                                                                                                                           
 => [gemini-api  9/12] COPY lib /app/lib                                                                                                                                                           
 => [gemini-api 10/12] COPY app.py .                                                                                                                                                         
 => [gemini-api 11/12] COPY localstack/init-aws.sh /app/localstack/init-aws.sh                                                                                                                                                           
 => [gemini-api 12/12] RUN chmod +x /app/localstack/init-aws.sh                                                                                                                                                           
 => [gemini-api] exporting to image                                                                                                                                                        
 => => exporting layers                                                                                                                                                       
 => => writing image sha256:a4c57312dd6b33e927f82a4a4fa8e245f04b6a5cd6dabf1b0f7b2f7bc81f6bbf                                                                                      
 => => naming to docker.io/library/gemini-chat-gemini-api                                                                                                                                       
[+] Running 3/2
 ✔ Network gemini-chat_default  Created                                                                                                                                                      
 ✔ Container localstack         Created                                                                                                                                                                                                                    
 ✔ Container gemini-api         Created                
```

**This will build images and start the containers.**

### Step 3: Stop the Container

```bash
docker-compose down
```

### Step 4: Restart the container

  * *use "-d" to detach the terminal*
```bash
docker-compose up
```

---

## 📜 **Logs**

**You can inspect logs using:**

```bash
docker logs gemini-api
docker logs localstack
```

---

## 📂 **DynamoDB**

**During container build, a script initializes DynamoDB.**

📄 **File: `localstack/init-aws.sh`**

**This script:**

* **Creates a DynamoDB table**
* **Inserts a starter record for testing**

```bash
...

echo "Start creating '$TABLE_HISTORY'"
# Create DynamoDB table with session_id as the hash key of type S
output=$(aws dynamodb create-table \
    --table-name "$TABLE_HISTORY" \
    --attribute-definitions AttributeName=session_id,AttributeType=S \
    --key-schema AttributeName=session_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url "$DYNAMODB_ENDPOINT" \
    --region "$AWS_REGION")

echo "$output"
...
```

### **Verify Table Creation**

**Run:**

```bash
docker logs localstack
```

**Look for output similar to:**

```bash
localstack  | {
localstack  |     "TableDescription": {
localstack  |         "AttributeDefinitions": [                              
localstack  |             {                      
localstack  |                 "AttributeName": "session_id",                                                                                         
localstack  |                 "AttributeType": "S"                                                                                                   
localstack  |             }                                                                                                                
localstack  |         ],                                                                                                                       
localstack  |         "TableName": "ChatHistory",                                                                                        
localstack  |         "KeySchema": [                                                                                                     
localstack  |             {                                                                                                     
localstack  |                 "AttributeName": "session_id",                                                                                         
localstack  |                 "KeyType": "HASH"                                                                                                
localstack  |             }
localstack  |         ],                                                                                             
localstack  |         "TableStatus": "ACTIVE", 
localstack  |         "CreationDateTime": 1747682496.274,                                                                                                  
localstack  |         "ProvisionedThroughput": {                                                                                                     
localstack  |             "LastIncreaseDateTime": 0.0,                                                                                                    
localstack  |             "LastDecreaseDateTime": 0.0,                                                                                                    
localstack  |             "NumberOfDecreasesToday": 0,                                                                                                    
localstack  |             "ReadCapacityUnits": 0,                                                                                                    
localstack  |             "WriteCapacityUnits": 0                                                                                                     
localstack  |         },                                                                                               
localstack  |         "TableSizeBytes": 0,
localstack  |         "ItemCount": 0,                                                                                                    
localstack  |         "TableArn": "arn:aws:dynamodb:us-west-2:000000000000:table/ChatHistory",                                                                                                                        
localstack  |         "TableId": "721164d1-1f03-487a-ae76-c9e6fd7464ba",                                                               
localstack  |         "BillingModeSummary": {                                                                                                     
localstack  |             "BillingMode": "PAY_PER_REQUEST",                                                                                    
localstack  |             "LastUpdateToPayPerRequestDateTime": 1747682496.274                                                                                                   
localstack  |         },                                                                              
localstack  |         "DeletionProtectionEnabled": false                                                                                                 
localstack  |     }                                                                                   
localstack  | }                                                        

```

<br><br>

# 📦 Dockerfile Breakdown
**This project includes a custom Dockerfile used to create the FastAPI Gemini Chat API container. It installs dependencies, sets up AWS CLI, and configures LocalStack integration for DynamoDB emulation.**

## 🧱 **Base Image**
```dockerfile
FROM python:3.13.0-slim
```
**Uses a lightweight Python 3.13 base for minimal overhead.**

## 🌍 **Environment Variables**
```dockerfile
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV TABLE_HISTORY=${TABLE_HISTORY}
ENV DYNAMODB_ENDPOINT=${DYNAMODB_ENDPOINT}
```
**Sets up environment variables to interact with LocalStack and defines the default DynamoDB table.**

## 📦 **System Dependencies**
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip
```
**Installs essential tools like curl and unzip, required for downloading AWS CLI.**

## ☁️ **AWS CLI Installation**
```dockerfile
RUN curl "...awscli-exe..." -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install
```
**Installs the AWS CLI to enable script-based creation of DynamoDB resources through LocalStack.**

## 🛠️ **AWS Profile Configuration**
```dockerfile
RUN mkdir -p ~/.aws
RUN aws configure set ... --profile localstack
```
**Configures a local profile to interact with** ***LocalStack's AWS endpoints.***

## 📁 **Application Setup**
```dockerfile
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY lib /app/lib
COPY app.py .
```
* **Installs Python dependencies**
* **Copies the FastAPI app and supporting files**

## 📜 LocalStack Initialization
```dockerfile
COPY localstack/init-aws.sh /app/localstack/init-aws.sh
RUN chmod +x /app/localstack/init-aws.sh
```
**Adds and prepares a shell script that will create the DynamoDB table during container startup.**

🔧 ***Note: By default, the script is not run in the Dockerfile but can be triggered on container start manually or via docker-compose.***

## 🚀 **Container Entry Point**
```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```
**Starts the FastAPI application on port 8000 within the container, accessible from the host machine.**

---

<br><br>

# 🐳 **Docker Compose Setup**
**This project uses Docker Compose to manage and run two integrated services:**

* 🔧 **LocalStack — A local AWS cloud emulator used to host DynamoDB and other AWS services.**

* 🚀 **Gemini API (FastAPI) — Your Python application embedding the Gemini chat model.**

**The ```docker-compose.yml``` file simplifies setup and allows both services to run in isolated, connected containers.**

## 🚀 **Features**

* **Environment variables managed via .env file. Use ```${VARIABLE_NAME}``` in the yml and Dockerfile files**
* **AWS resource auto-creation via init-aws.sh script**
* **Dependency ordering (depends_on)**
* **Build-time arguments passed for image customization**

## 📄 **docker-compose.yml**
```yaml
version: "3.8"

services:
  localstack:
    image: localstack/localstack
    container_name: localstack
    environment:
      - SERVICES=dynamodb,s3,apigateway,cloudwatch # Add other services as needed
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - TABLE_HISTORY=${TABLE_HISTORY}
      - DYNAMODB_ENDPOINT=${DYNAMODB_ENDPOINT}
    ports:
      - "4566:4566"
    volumes:
      - "./localstack/init-aws.sh:/etc/localstack/init/ready.d/init-aws.sh"

  gemini-api:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
        AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
        AWS_DEFAULT_REGION: ${AWS_REGION}
        TABLE_HISTORY: ${TABLE_HISTORY}
    container_name: gemini-api
    depends_on:
      - localstack
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - DYNAMODB_ENDPOINT=${DYNAMODB_ENDPOINT}
      - TABLE_HISTORY=${TABLE_HISTORY}
```
### ⚙️ **What It Does**
* **LocalStack container launches first and simulates AWS services:**

  * **DynamoDB, S3, CloudWatch, and API Gateway**

  * **Executes the init-aws.sh script to create the ChatHistory table on startup**

* **Gemini API container:**

  * **Waits for LocalStack to be ready**

  * **Starts a FastAPI server on http://localhost:8000**

  * **Connects to LocalStack's DynamoDB using environment configuration**

  * **Retreive Gemini API key from environment variables**

  * **Prepare arguments for the ```Dockerfile```**


## ▶️ **Run the Containers**
**To build and start the services in detach mode:**
```bash
docker-compose up -d --build
```
**To stop the services:**
```bash
docker-compose down
```
## 📊 **Check Logs**
* **FastAPI app logs:**
```bash
docker logs gemini-api
```
* **LocalStack logs:**
```bash
docker logs localstack
```
## 📌 **Notes**
* **Make sure to create ```.env``` file and place your Gemini API key and AWS resources in the the root directory of the project**

* **If you need to add more AWS services, you can extend the ```SERVICES``` environment variable under ```localstack```.
But go check [localstack documentation](https://docs.localstack.cloud/user-guide/) for more informations**

 

<br><br>


---

# 💬 Chat GUI (PyQt6)

**This project includes a lightweight desktop chat application built using PyQt6. It provides a user-friendly interface to interact with the Gemini-powered API, enabling real-time conversations with session-based chat history.**


## ✨ Features
* ✅**Clean and responsive PyQt6-based GUI**

* 🔑 **User-defined session IDs for personalized chat history**

* ♻️ **Real-time messaging with Gemini via FastAPI backend**

* 📜 **Possibility to retrieves and displays full conversation history for a session id**

* 🖥️ **Possibility to set API endpoint**

* ⚙️ **Uses QThread to perform asynchronous API calls (non-blocking UI)**

* 🌐**Renders chat using QWebEngineView with dynamic JavaScript execution**

* 🎨 **Styled using CSS for both PyQt widgets and HTML chat interface**


## 🧰 Requirements
**Make sure you have the following installed:**
```bash
pip install PyQt6 requests
```
**Or install requirements under ui/requirements.txt**
```bash
pip install -r ui/requirements.txt
```
## Running the GUI

**Navigate to the gui folder:**


```
cd ui
```
**Run the app:**
```
python chat_app.py
```
**Ensure your FastAPI server is running at http://127.0.0.1:8000 for the GUI to connect successfully or you can set it in the application through menu "Options" -> "API Endpoint"**

---

<br><br>

# 🔮 **API Testing Tips**

**You can test API endpoints using:**

* **`curl` (as shown above)**
* **[Postman](https://www.postman.com/) – for a GUI-based approach**
* **Swagger UI (auto-generated by FastAPI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
* **Use ChatApp located under "ui" folder**

---

<br><br>

# 📄 License

**This project is licensed under the **Educational and Non-Commercial Use License**.
See the [LICENSE](LICENSE) file for full details.**

---

<br>

**Made for educational purposes.**
