"""
Diagnose available Groq models and connection.
Run: python diagnose_models.py
"""

import os
from dotenv import load_dotenv
load_dotenv()


def diagnose():
    # Test Groq connection & available models
    print("--- Testing Groq Connection ---")
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        models = client.models.list()
        for m in models.data:
            print(f"  Available: {m.id}")
        print(f"\nTotal models: {len(models.data)}")
    except Exception as e:
        print(f"  Groq Error: {e}")


if __name__ == "__main__":
    diagnose()
