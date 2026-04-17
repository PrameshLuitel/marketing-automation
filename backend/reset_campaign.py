import asyncio
from storage.database import get_session_direct, Campaign
from sqlalchemy import select

async def reset():
    session = await get_session_direct()
    res = await session.execute(select(Campaign).where(Campaign.id == 3))
    c = res.scalar_one_or_none()
    if c:
        c.status = 'pending'
        await session.commit()
        print(f'Reset Campaign {c.id} to pending')
    else:
        print('Campaign 3 not found')
    await session.close()

if __name__ == "__main__":
    asyncio.run(reset())
