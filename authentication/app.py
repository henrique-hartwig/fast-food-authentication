import json
import boto3
import os
from datetime import datetime

cognito = boto3.client("cognito-idp")
USER_POOL_ID = os.environ["USER_POOL_ID"]

def lambda_handler(event, context):
    http_method = event["httpMethod"]

    if http_method == "POST":
        return create_user(event)
    elif http_method == "GET":
        return get_user(event)
    else:
        return {"statusCode": 405, "body": json.dumps({"message": "Method not allowed"})}

def create_user(event):
    try:
        body = json.loads(event["body"])
        cpf = body["cpf"]
        name = body["name"]
        email = body["email"]

        cognito.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "custom:cpf", "Value": cpf},
                {"Name": "name", "Value": name}
            ]
        )
        return {"statusCode": 201, "body": json.dumps({"message": "Created user successfully"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def get_user(event):
    try:
        cpf = event["pathParameters"]["cpf"]
        response = cognito.list_users(UserPoolId=USER_POOL_ID)
        
        for user in response.get("Users", []):
            user_data = {}
            for key, value in user.items():
                if isinstance(value, datetime):
                    user_data[key] = value.isoformat()
                else:
                    user_data[key] = value
                
            for attr in user.get("Attributes", []):
                if attr["Name"] == "custom:cpf" and attr["Value"] == cpf:
                    return {
                        "statusCode": 200,
                        "body": json.dumps({"message": user_data})
                    }
        
        return {"statusCode": 404, "body": json.dumps({"message": "User not found"})}
    
    except Exception as e:
        print(f"Error to search user: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}