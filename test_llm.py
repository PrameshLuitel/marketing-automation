import asyncio
from backend.agents.router import LLMRouter

async def main():
    router = LLMRouter()
    
    print("Testing Groq...")
    res1 = await router.generate("Hello", force_provider="groq")
    print(res1)
    
    print("Testing Gemini...")
    res2 = await router.generate("Hello", force_provider="gemini")
    print(res2)
    
    print("Testing Mistral...")
    res3 = await router.generate("Hello", force_provider="mistral")
    print(res3)

asyncio.run(main())
