import asyncio
import sys
import os

# Add backend to path
sys.path.append("/Users/prameshluitel/Documents/Marketing Deparment Automation/backend")

from agents.router import LLMRouter
from agents.council import AgentCouncil

async def main():
    print("🚀 Verifying Agent Council stability...")
    router = LLMRouter()
    council = AgentCouncil(router=router)
    
    # Simple data brief that mimics a real one but smaller
    brief = {
        "platform_counts": {"news": 1, "google_trends": 2},
        "items": [
            {"platform": "news", "title": "LoadSewa Expansion", "text": "LoadSewa is expanding to 5 new cities in Nepal with real-time tracking."},
            {"platform": "google_trends", "title": "Logistics Nepal", "text": "Search volume for logistics services in Kathmandu is up 40%."}
        ]
    }
    
    def live_log(agent, msg):
        print(f"  [{agent.upper()}] {msg[:60]}...")

    print("Running Council...")
    try:
        results = await council.run(brief, progress_callback=live_log)
        print("\n✅ COUNCIL SUCCESS!")
        print(f"Final Score: {results.get('quality_score')}/10")
        print(f"Passed Gate: {results.get('passed_quality_gate')}")
        
        # Verify debate contents exist
        for agent in ["trend_analyst", "strategy_planner", "copywriter", "creative_director"]:
            if agent in results["agents"]:
                debate = results["agents"][agent].get("debate", "")
                if debate:
                    print(f"  Debate for {agent}: OK ({len(debate)} chars)")
                else:
                    print(f"  Debate for {agent}: MISSING!")
    except Exception as e:
        print(f"\n❌ COUNCIL FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
