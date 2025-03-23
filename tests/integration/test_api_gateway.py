import os
import boto3
import pytest
import requests

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

    def test_api_gateway_get(self, api_gateway_url):
        """ Test GET endpoint """
        params = {
            "cpf": "01234567891"
        }
        response = requests.get(api_gateway_url, params=params)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert data["user"]["cpf"] == "01234567891"

    def test_api_gateway_post(self, api_gateway_url):
        """ Test POST endpoint """
        payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
            "cpf": "01234567891"
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(api_gateway_url, json=payload, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "User authenticated successfully"
        assert "token" in data
