# Fast Food Authentication Service

A serverless authentication service built with AWS Lambda, API Gateway, and Cognito. This service provides user management capabilities through a RESTful API, implemented using AWS SAM (Serverless Application Model).

## Architecture

- **AWS Lambda**: Handles the business logic for user operations
- **API Gateway**: Exposes RESTful endpoints
- **Cognito**: Manages user pool and authentication
- **SAM**: Infrastructure as Code for AWS resources

## API Endpoints

- `POST /user`: Create a new user
- `GET /user`: Get user information

## Prerequisites

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Python 3.12](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started) (for local testing)
- AWS Account and configured credentials

## Local Development

1. **Install Dependencies**
   ```bash
   pip install -r authentication/requirements.txt
   pip install -r tests/requirements.txt
   ```

2. **Run Local API**
   ```bash
   sam build --use-container
   sam local start-api
   ```

3. **Test Endpoints Locally**
   ```bash
   # Create user
   curl -X POST http://localhost:3000/user -d '{"name": "John Doe", "email": "john@example.com", "password": "secret123", "cpf": "01234567891"}'

   # Get user
   curl http://localhost:3000/user?cpf=01234567891
   ```

## Testing

1. **Unit Tests**
   ```bash
   pytest tests/unit -v --cov=authentication/
   ```

2. **Integration Tests**
   ```bash
   AWS_SAM_STACK_NAME="fast-food-authentication" pytest tests/integration -v
   ```

## Deployment

1. **First Time Deployment**
   ```bash
   sam build
   sam deploy --guided
   ```

2. **Subsequent Deployments**
   ```bash
   sam build
   sam deploy
   ```

## CI/CD Pipeline

The project includes a GitHub Actions pipeline that:
- Runs tests on PR creation/updates
- Deploys to AWS when changes are merged to master
- Ensures code quality and test coverage

## Environment Variables

Required for deployment and testing:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: Target AWS region
- `USER_POOL_ID`: Cognito User Pool ID

## Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Run tests locally
4. Create a PR to `develop`
5. After approval and merge to `develop`, create a PR to `master`
