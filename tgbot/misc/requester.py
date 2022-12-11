import asyncio

import aiohttp
import json



async def get_btc():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.blockonomics.co/api/price?currency=RUB') as resp:
            responce = await resp.read()
        data = json.loads(responce)
    return data['price']



