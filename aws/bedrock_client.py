import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"  # change if needed
)

def explain_decision(context):
    prompt = f"""
You are an agricultural market advisor in India.

Explain the following decision in simple terms:
{context}

Explain in a way a farmer can understand.
"""

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 300,
            "temperature": 0.3
        })
    )

    result = json.loads(response["body"].read())
    return result["completion"]
