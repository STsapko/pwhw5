import sys
from datetime import datetime, timedelta
import aiohttp
import platform
import asyncio
import json

pb_api_url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

async def get_date_exchange_rates(session: aiohttp.ClientSession, date_: str):
    try:
        async with session.get(f"{pb_api_url}{date_}") as resp:
            if resp.status == 200:
                return await resp.json()
    except aiohttp.ClientConnectorError:
            pass

async def get_days_exchange_rates(days: int):
        async with aiohttp.ClientSession() as session:
            tasks = []
            today = datetime.today()
            for i in range(days):
                date_ = (today - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(get_date_exchange_rates(session, date_))                    
            results = await asyncio.gather(*tasks)
        # get exchange rates for USD, EUR
        exchange_rates = {}
        for result in results:
            if result:
                exchange_rates[result.get('date')] = \
            {rate['currency']: {'sale': rate['saleRate'], 'purchase': rate['purchaseRate']} \
                    for rate in result.get('exchangeRate') \
                    if rate.get('currency') in ['EUR','USD']} 
        # prettify output
        exchange_rates = json.dumps(
                            exchange_rates,
                            sort_keys=True,
                            indent=4,
                            separators=(',', ': ')
                        )
        return exchange_rates

async def main():
    try:
        sys.argv[1].isdigit()
        days = min(int(sys.argv[1]), 10)
    except:
        pass
    
    exchange_rates = await get_days_exchange_rates(days)
    return exchange_rates

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())