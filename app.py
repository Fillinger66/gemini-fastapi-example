"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""


import boto3 #To access AWS resources

from fastapi import FastAPI #To create the FastAPI app
from fastapi.responses import JSONResponse #To return json response

import json #Json manipulation
import os #To access environement variables
from pydantic import BaseModel #To hanlde ChatRequest
import time #To trace execution time

from lib.ChatContent import ChatContent #To manage history chat
from lib.DynamoWrapper import DynamoWrapper #To communicate with dynamodb
from lib.GeminiWrapper import GeminiWrapper #To communicate with Gemini


#Set region if nessary
#if not os.getenv("AWS_REGION"):
#    os.environ["AWS_REGION"] = "us-west-2"

#Get AWS Region
region = os.getenv("AWS_DEFAULT_REGION","us-west-2")

# Pydantic model for request body
class ChatRequest(BaseModel):
    prompt: str
    session_id: str


#DynamoDb table
TABLE_HISTORY=os.getenv('TABLE_HISTORY', "ChatHistory")
# FastAPI app initialization
app = FastAPI()

# LocalStack DynamoDB connection
dynamodb = boto3.resource(
    "dynamodb", 
    endpoint_url= os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:4566'),
    region_name=region)

#Get Gemini key (see docker-compose file)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY",None)

#Helper to communicate with gemini
gemini_wrapper = None

#Helper to communicate with dynamodb on Localstack
dynamodb_wrapper = DynamoWrapper(dynamodb)


def startChat(prompt:str,session_id:int,history=None) -> str:
    """
        start a chat with Gemini pro

        Arguments:
            prompt (str): The prompt to send
    session_id (int): The second number to add
        history: List of history ([
                                {"role": "user", "parts": "Hello"},
                                {"role": "model", "parts": "Great to meet you. What would you like to know?"}
                            ])

        Returns:
            str_response (str): The answer
"""
    global gemini_wrapper
    global dynamodb_wrapper

    str_response = ""
    
    #Init the chat
    if not gemini_wrapper.initChat(history):
        print("Error initialize chat...")
        return "Error init chat..."

    #Send prompt to Gemini
    response = gemini_wrapper.chat(prompt)
    
    #Create string response
    #loop to concate in one string
    for chunk in response:
        str_response+= chunk.text

    print(f"model : {str_response}")
    print("_" * 80)
    
    #Get the chat history and save it
    history = gemini_wrapper.getChatHistory()
    if history != None:
        saveHistory(session_id,history)
    else:
        print(f"startChat:: No history for session id -> {session_id}")
    
    return str_response

def saveHistory(session_id,history) -> dict:
    """
    save the chat history to DynamoDb

    Args:

        session_id (int): The user session_id
        history ([
                    {"role": "user", "parts": "Hello"},
                    {"role": "model", "parts": "Great to meet you. What would you like to know?"},
                ]) : List of history

    Returns:
        str: The answer
    """

    print(f"saveHistory:: session id -> {session_id} \n history -> {history}")

    mylist = []

    #loop on the history 
    #and create a list of ChatContent to facilite 
    #the json manipulation for storing
    for content in history:
        part = content.parts[0]
        print(content.role, "->", type(part).to_dict(part))
        print('-'*80)
        mylist.append(ChatContent(content.role,type(part).to_dict(part)["text"]))

    history_string = json.dumps([ob.__dict__ for ob in mylist])

    return dynamodb_wrapper.putHistory(session_id,history_string,TABLE_HISTORY)
    
def getDynamoHistory(session_id:int) -> dict:
    """
    Get history from DynamoDb as dicttonary

    Args:
        session_id (int):

    Returns:
        dt  (dict): history in json string format or None
    """

    try:

        json_str = dynamodb_wrapper.getHistory(session_id,TABLE_HISTORY)
        history=None

        if json_str!=None:
            print(f"getDynamoHistory::session id : {session_id} -> read : {json_str}")
            history = json.loads(json_str)
            print(f"getDynamoHistory::dict : {history}")

        return history

    except Exception as e:
        print(f"getDynamoHistory:: exception : {e}")


"""""""""""""""""""""
        ROUTES
"""""""""""""""""""""

@app.post("/chat/")
def chat(request: ChatRequest) -> JSONResponse:
    """
    Chat with Gemini

    This endpoint allows you to send a prompt to Gemini
    and receive a response. It also handles the session history
    and saves it to DynamoDB.

    Args:
        request (ChatRequest): ChatRequest containing session_id and prompt

    Returns:
        json: Format    
        {
                "reply": {
                    "role": "...",
                    "response": "...."
                }
        }

    """
    try:

        global gemini_wrapper #GeminiWrapper

        start_time = time.time()
        #Init wrapper with gemini key
        gemini_wrapper = GeminiWrapper(GEMINI_API_KEY)
        end_time = time.time()
        print(f"GeminiWrapper instanciation time : {round((end_time-start_time))*1000} ms")

        start_time = time.time()
        #Try to get a history from DynamoDb
        history = getDynamoHistory(request.session_id)
        end_time = time.time()
        print(f"DynamoDb reading time : {round((end_time-start_time)*1000)} ms")

        start_time = time.time()
        #Start the chat with prompt
        response_json = startChat(request.prompt,request.session_id,history)
        end_time = time.time()
        print(f"Gemini response & parse time : {round((end_time-start_time)*1000)} ms")
        print(f"Response : {response_json}")

        #Check if there was an error
        if response_json[0:5]=="Error":
            print(f"Error decoding response: {response_json}")
            return {"error": "Failed to get Gemini API response."}

        response_json = ''.join([char for char in response_json if char != '\\'])
        #Construct the reply
        reply = {"session_id":request.session_id,"role":"model","response":response_json}

        return JSONResponse(content=reply,status_code=200)

    except Exception as e:
        print(f"Error decoding response: {e}")
        return JSONResponse(content={"error": "Operation failed."},status_code=400)

@app.get("/describe-table/")
def describe_table() -> JSONResponse:
    """
        Helper route to verify table history

        Returns:
            json: Format    
            {
                    "status": "..."
            }

    """
    try:
        table_status = dynamodb_wrapper.getTableStatus(TABLE_HISTORY)

        if table_status.get("error", False):
            return JSONResponse(content={"error":"Error no resource found"},status_code=404)
        
        return JSONResponse(content= table_status,status_code = 200)
    except Exception as e:
        print(f"describe_table:: exception : {e}")
        return JSONResponse(content={"error":"Error retreiving ressource"},status_code=500)

@app.get("/get-item/{session_id}")
def get_item(session_id: str) -> JSONResponse:
    """
    Helper route to get a session history

    Args:
        session_id (str): user session id

    Returns:
        json: Format    
        [{"role": "...","parts":"..."},{"role": "...","parts":"..."},...]
    """
    try:
        #Get the history from DynamoDb
        history = dynamodb_wrapper.getHistory(session_id,TABLE_HISTORY)
        #if the history is None, return 404
        if history == None:
            print(f"get_item:: No history")
            return JSONResponse(content={"error":"Resource not found"},status_code=404)

        print(f"get_item::session id : {session_id} -> read : {history}")

        return JSONResponse(content={"session_id":session_id,"history":json.loads(history)}, status_code=200)
    except Exception as e:
        print(f"get_item:: exception : {e}")
        return JSONResponse(content={"error":"Error retreiving ressource"},status_code=500)