# Serverless Contact API with Pulumi & AWS

This project demonstrates a **serverless API** using **AWS Lambda**, **API Gateway v2**, and **DynamoDB**, managed with **Pulumi** in Python. It provides endpoints to submit a contact form and list submitted messages.

---

## Features

- **POST /contact** – Submit a new contact message.
- **GET /contacts** – List submitted messages.
- **Serverless** – No servers to manage; everything runs in AWS Lambda.
- **Infrastructure as Code** – Fully defined in Pulumi, easy to deploy and destroy.
- **Ready for JWT authentication** – Can integrate AWS Cognito for auth later.

---

## Project Structure

```project-root/
├─ Pulumi.yaml # Pulumi project configuration
├─ main.py # Pulumi stack defining AWS resources
├─ functions/
│ ├─ post_contact/ # Lambda code for submitting messages
│ │ └─ handler.py
│ └─ list_contacts/ # Lambda code for listing messages
│ └─ handler.py
└─ README.md
```


## Requirements

- Python 3.11+
- Pulumi CLI: [Install Pulumi](https://www.pulumi.com/docs/get-started/install/)
- AWS CLI configured with credentials
- `boto3` library for Lambda functions

---

## Setup & Deployment

1. **Install dependencies**

```bash
pip install pulumi pulumi-aws boto3
```
1. **Configure Pulumi**

```
pulumi login   # choose local or cloud backend
pulumi stack init dev
pulumi config set aws:region eu-north-1
```
3. **Deploy your stack**

```
pulumi up
```
- Pulumi will show a preview of resources.
- Confirm (yes) to create API Gateway, Lambdas, DynamoDB table, and IAM roles.
- After deployment, you will see outputs like:

```
apiEndpoint    : https://xxxxxx.execute-api.eu-north-1.amazonaws.com
dynamoTableName: contactMessages-xxxxxx
```
## Testing the API
### Using `curl`
```
# Submit a contact message
curl -X POST https://<API_ENDPOINT>/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Hamze","email":"hamze@example.com","message":"Hello World"}'

# List submitted messages
curl -X GET https://<API_ENDPOINT>/contacts
```
### Using Python
```python
import requests

API_URL = "https://<API_ENDPOINT>"

# POST
post_data = {"name": "Hamze", "email": "hamze@example.com", "message": "Hello World"}
post_response = requests.post(f"{API_URL}/contact", json=post_data)
print(post_response.json())

# GET
get_response = requests.get(f"{API_URL}/contacts")
print(get_response.json())
```
---
## Cleaning Up
To remove all resources and avoid AWS charges:
```
pulumi destroy
```

## Next Steps / Improvements
- Enable JWT authentication using AWS Cognito for secure endpoints.
- Add pagination for GET /contacts.
- Add input validation and error handling in Lambdas.
- Connect to a frontend (web/mobile) to interact with the API.
- Explore Pulumi stacks for dev/staging/production environments.

## Notes
- All infrastructure is defined in Pulumi; you don’t need to manually create resources in AWS.
- DynamoDB table is on-demand, no provisioning needed.
- CORS is open (*) for now. Tighten it for production.
- Lambda functions are Python 3.11; you can add layers or other dependencies as needed.
