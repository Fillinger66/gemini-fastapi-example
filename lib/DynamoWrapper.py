"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""
from botocore.exceptions import ClientError

class DynamoWrapper():
    """
    This is a simple helper class to interect with DynamoDb
    Instantiate your AWS resource and pass it in Ctor

    Example:
        >>> dynamo_wrapper = DynamoWrapper(YOUR_AWS_RESOURCE)
    >>> dynamo_wrapper.getHystoryItem(session_id,table_name)
    """
    dynamodb = None

    def __init__(self, dynamodb):
        """
        Init the wrapper to communicaate with DynamoDb

        Args:
            ressource (str): "dynamodb"
            endpoint (str): DynamoDb endpoint
            region_name (str): AWS region

        """
        self.dynamodb = dynamodb

    def getHistory(self,session_id:str,table_name:str) -> str:
        """
        Get the history from DynamoDb as json string

        Args:
            session_id (str): the session id relate to the history
            table_name (str): the history table

        Returns:
            json_str  (str): history in json string format or {"error":"message"}
        """
        try:
            table = self.dynamodb.Table(table_name)
            print(f"DynamoWrapper::getHistory : {session_id}")
            response = table.get_item(Key={'session_id': session_id})

            if 'Item' in response:
                print(f"getHistory::response['Item'] : {response['Item']}")
                return response['Item'].get("history")
            else:
                print("DynamoWrapper::getHistoryItem:: item not found")
                return None

        except ClientError as e:
            print(f"DynamoWrapper::getHistory::Error : {e.response['Error']['Message']}")
            return {"error": e.response['Error']['Message']}
        
    def putHistory(self,session_id:str,history:str,table_name:str) -> dict:
        """
        Put the history to DynamoDb as json string

        Args:
            session_id (str): the session id relate to the history
            history (str): the history
            table_name (str): the history table

        Returns:
            reponse  (dict): updated_attributes and message or {"error":"message"}
        """
        try:
            table = self.dynamodb.Table(table_name)
        
            response = table.update_item(
                Key={'session_id': session_id},
                UpdateExpression="SET history = :val",
                ExpressionAttributeValues={
                    ':val': history,
                },
                ReturnValues="UPDATED_NEW"
            )
            print(f"DynamoWrapper::putHistoryItem -> Item updated successfully!")
            print(f'DynamoWrapper::putHistoryItem -> updated_attributes : {response["Attributes"]}')
            return {"message": "Item updated successfully!", "updated_attributes": response["Attributes"]}
        except ClientError as e:
            print(f"DynamoWrapper::putHistoryItem::insertOrAppend -> Error : {e.response['Error']['Message']}")
            return {"error": e.response['Error']['Message']}
        
    def getTableStatus(self,table_name:str) -> dict:
        """
        Helper route to verify table history

        Returns:
            json: Format    
            {
                    "status": "..."
            }

        """
        try:
            table = self.dynamodb.Table(table_name)
            return {"status": table.table_status}
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            print(f"DynamoWrapper::getTableStatus -> Resource not found for {table_name}")
        return {"error": "Table does not exist"}