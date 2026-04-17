import asyncio
import json
from storage.database import get_session_direct, Campaign
from sqlalchemy import select

async def check():
    session = await get_session_direct()
    res = await session.execute(select(Campaign).limit(5))
    campaigns = res.scalars().all()
    if not campaigns:
        print("No campaigns found.")
    for c in campaigns:
        script_preview = c.video_script[:100] if c.video_script else "NONE"
        print(f"ID: {c.id} | Title: {c.title} | Status: {c.status}")
        print(f"Script: {script_preview}")
        print("-" * 20)
    await session.close()

if __name__ == "__main__":
    asyncio.run(check())
