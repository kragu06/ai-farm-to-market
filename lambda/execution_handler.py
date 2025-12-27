import json

def handler(event, context):
    body = json.loads(event["body"])

    # Example: store request, notify ops team, etc.
    print("Execution request received:", body)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Execution request received"
        })
    }
