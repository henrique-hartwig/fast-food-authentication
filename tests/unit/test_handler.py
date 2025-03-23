import json
import pytest
import unittest.mock as mock
from authentication import app


@pytest.fixture()
def apigw_event_get():
    """ Generates API GW Event for GET method"""
    return {
        "body": None,
        "resource": "/user",
        "path": "/user",
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
def apigw_event_post():
    """ Generates API GW Event for POST method"""
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
def mock_boto3():
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

def test_get_lambda_handler(apigw_event_get):
    ret = app.lambda_handler(apigw_event_get, "")
    data = json.loads(ret["body"])
    
    assert ret["statusCode"] == 200
    assert "message" in data
    user_data = data["message"]
    assert "Attributes" in user_data
    
    user_attrs = {attr["Name"]: attr["Value"] for attr in user_data["Attributes"]}
    assert user_attrs["email"] == "john@example.com"
    assert user_attrs["name"] == "John Doe"
    assert user_attrs["custom:cpf"] == "01234567891"

def test_post_lambda_handler(apigw_event_post):
    ret = app.lambda_handler(apigw_event_post, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 201
    assert "message" in data
    assert data["message"] == "Created user successfully"
