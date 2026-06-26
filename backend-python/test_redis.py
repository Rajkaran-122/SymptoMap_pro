import asyncio
from app.core.redis import redis_client

async def test():
    await redis_client.connect()
    print('Connected')
    await redis_client.disconnect()

asyncio.run(test())
