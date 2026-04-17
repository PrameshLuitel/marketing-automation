"""
Quick test for Groq LLM router.
Run: python test_llms.py
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()


async def test_groq():
    from agents.router import LLMRouter
    router = LLMRouter()

    print("=" * 50)
    print("GROQ-ONLY LLM Router Test")
    print("=" * 50)

    # 1. Test Fast tier
    print("\n1. GROQ FAST (llama-3.1-8b-instant)")
    try:
        res = await router.generate("Say hello in one sentence.", task_type="quick_summary")
        print(f"   Result: {res['text'][:100]}")
        print(f"   Model: {res['model']} | Tokens: {res['tokens_used']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 2. Test Balanced tier
    print("\n2. GROQ BALANCED (llama-4-scout)")
    try:
        res = await router.generate("Explain marketing automation in 2 sentences.", task_type="trend_analysis")
        print(f"   Result: {res['text'][:100]}")
        print(f"   Model: {res['model']} | Tokens: {res['tokens_used']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 3. Test Power tier
    print("\n3. GROQ POWER (llama-3.3-70b-versatile)")
    try:
        res = await router.generate("Write a marketing tagline for an AI company.", task_type="copy_generation")
        print(f"   Result: {res['text'][:100]}")
        print(f"   Model: {res['model']} | Tokens: {res['tokens_used']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    # 4. Usage stats
    print("\n4. USAGE STATS")
    print(f"   {router.get_usage_stats()}")

    print("\n" + "=" * 50)
    print("All tests complete!")


if __name__ == "__main__":
    asyncio.run(test_groq())
