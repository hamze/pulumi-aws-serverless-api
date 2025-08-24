import json
import os
import base64
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
        qs = (event.get("queryStringParameters") or {})
        limit = int(qs.get("limit", 25))
        next_token = qs.get("nextToken")

        kwargs = {"Limit": max(1, min(limit, 100))}
        if next_token:
            kwargs["ExclusiveStartKey"] = json.loads(
                base64.urlsafe_b64decode(next_token.encode()).decode()
            )

        table = ddb.Table(TABLE)
        res = table.scan(**kwargs)
        items = res.get("Items", [])
        last_key = res.get("LastEvaluatedKey")

        out_token = None
        if last_key:
            out_token = base64.urlsafe_b64encode(json.dumps(last_key).encode()).decode()

        return _response(200, {"items": items, "nextToken": out_token})
    except Exception as e:
        return _response(500, {"error": str(e)})
