import asyncio
from storage.database import get_session_direct, CreativeAsset
from sqlalchemy import select

async def check():
    session = await get_session_direct()
    res = await session.execute(select(CreativeAsset).where(CreativeAsset.campaign_id == 2))
    assets = res.scalars().all()
    if not assets:
        print("No assets found for campaign ID 2.")
    for a in assets:
        print(f"Asset ID: {a.id} | Type: {a.asset_type} | Path: {a.file_path}")
    await session.close()

if __name__ == "__main__":
    asyncio.run(check())
