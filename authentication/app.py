import json
import boto3
import os

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

        response = cognito.admin_create_user(
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

        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'custom:cpf = "{cpf}"'
        )

        users = response.get("Users", [])

        if not users:
            return {"statusCode": 404, "body": json.dumps({"message": "User not found"})}

        user_data = users[0]
        user_info = {attr["Name"]: attr["Value"] for attr in user_data["Attributes"]}

        return {"statusCode": 200, "body": json.dumps(user_info)}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
