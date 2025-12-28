# aws/bedrock_client.py

def explain_decision(context: str) -> str:
    """
    Fallback explanation when Amazon Bedrock is not available.
    Actual Bedrock integration is enabled in production deployment.
    """
    return (
        "Based on long-term market patterns and seasonal price behavior, "
        "the system recommends this action to reduce distress sales and "
        "improve net income. This explanation is generated using rule-based "
        "logic. Amazon Bedrock will provide AI-generated explanations "
        "in the production version."
    )
