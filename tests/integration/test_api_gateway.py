import os
import boto3
import pytest
import json
import unittest.mock as mock
from authentication import app

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestApiGateway:

    @pytest.fixture()
    def api_gateway_url(self):
        """ Get the API Gateway URL from Cloudformation Stack outputs """
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise ValueError('Please set the AWS_SAM_STACK_NAME environment variable to the name of your stack')

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name} \n" f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "AuthenticationApi"]

        if not api_outputs:
            raise KeyError(f"AuthenticationAPI not found in stack {stack_name}")

        return api_outputs[0]["OutputValue"]

    @pytest.fixture()
    def apigw_event_get(self):
        return {
            "body": None,
            "resource": "/user/{cpf}",
            "path": "/user/01234567891",
            "httpMethod": "GET",
            "queryStringParameters": {},
            "pathParameters": {
                "cpf": "01234567891"
            },
            "headers": {
                "Accept": "application/json",
                "User-Agent": "Custom User Agent String"
            },
            "requestContext": {
                "resourceId": "123456",
                "apiId": "1234567890",
                "httpMethod": "GET",
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
                "accountId": "123456789012",
                "stage": "prod",
            }
        }

    @pytest.fixture()
    def apigw_event_post(self):
        return {
            "body": json.dumps({
                "name": "John Doe",
                "email": "john@example.com",
                "password": "secret123",
                "cpf": "01234567891"
            }),
            "resource": "/user",
            "path": "/user",
            "httpMethod": "POST",
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "Custom User Agent String"
            },
            "requestContext": {
                "resourceId": "123456",
                "apiId": "1234567890",
                "httpMethod": "POST",
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
                "accountId": "123456789012",
                "stage": "prod",
            }
        }

    @pytest.fixture(autouse=True)
    def mock_boto3(self):
        with mock.patch('authentication.app.cognito') as mock_cognito:
            mock_cognito.list_users.return_value = {
                'Users': [
                    {
                        'Username': 'test-user',
                        'Attributes': [
                            {'Name': 'email', 'Value': 'john@example.com'},
                            {'Name': 'name', 'Value': 'John Doe'},
                            {'Name': 'custom:cpf', 'Value': '01234567891'}
                        ]
                    }
                ]
            }
            mock_cognito.admin_create_user.return_value = {
                'User': {
                    'Username': 'john@example.com',
                    'Attributes': [
                        {'Name': 'email', 'Value': 'john@example.com'},
                        {'Name': 'name', 'Value': 'John Doe'},
                        {'Name': 'custom:cpf', 'Value': '01234567891'}
                    ]
                }
            }
            yield mock_cognito

    def test_api_gateway_get(self, apigw_event_get, mock_boto3):
        """ Test GET endpoint """
        response = app.lambda_handler(apigw_event_get, "")
        
        assert response["statusCode"] == 200
        data = json.loads(response["body"])
        assert "message" in data
        
        user_data = data["message"]
        assert "Attributes" in user_data
        
        user_attrs = {attr["Name"]: attr["Value"] for attr in user_data["Attributes"]}
        assert user_attrs["email"] == "john@example.com"
        assert user_attrs["name"] == "John Doe"
        assert user_attrs["custom:cpf"] == "01234567891"

    def test_api_gateway_post(self, apigw_event_post, mock_boto3):
        """ Test POST endpoint """
        response = app.lambda_handler(apigw_event_post, "")
        
        assert response["statusCode"] == 201
        data = json.loads(response["body"])
        assert "message" in data
        assert data["message"] == "Created user successfully"
