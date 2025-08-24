import datetime
import json
import os
import uuid
import boto3

TABLE = os.environ["TABLE_NAME"]
ddb = boto3.resource("dynamodb")

def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")

        # Extract fields
        name = body.get("name")
        mobile = body.get("mobile")
        email = body.get("email")
        message = body.get("message")

        if not (name and email and message):
            return _response(400, {"error": "name, email, and message are required"})

        item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "mobile": mobile,
            "email": email,
            "message": message,
            "date": datetime.datetime.utcnow().isoformat(),
        }

        table = ddb.Table(TABLE)
        table.put_item(Item=item)

        return _response(200, {"message": "Contact submitted", "id": item["id"]})
    except Exception as e:
        return _response(500, {"error": str(e)})
