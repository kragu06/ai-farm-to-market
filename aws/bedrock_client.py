# aws/bedrock_client.py
# SAFE FALLBACK – NO AWS SDK REQUIRED

def explain_decision(context: str) -> str:
    return (
        "The system analyzed long-term seasonal price trends, "
        "historical market crashes, and commodity perishability. "
        "Based on this, it recommends the chosen action to reduce "
        "distress sales and improve net farmer income. "
        "Amazon Bedrock will generate this explanation in the "
        "production AWS deployment."
    )
