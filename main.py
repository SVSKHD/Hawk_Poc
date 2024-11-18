from config import symbols_config
from utils import connect_mt5
from fetch_prices import fetch_current_price, fetch_price
import asyncio

async def main():
    connect = await connect_mt5()
    if connect:
        print("Connected to MT5")
        price_data = []
        for symbol in symbols_config:
            start_price = await fetch_price(symbol, "start")
            if start_price is not None:
                price_data.append({
                    'symbol': symbol['symbol'],
                    'start_price': start_price,
                    'current_price': start_price
                })
                print(f"Symbol: {symbol['symbol']}, Start Price: {start_price}")

        while True:
            for data in price_data:
                current_price = await fetch_current_price({'symbol': data['symbol']})
                if current_price is not None:
                    data['current_price'] = current_price
                    print(f"Symbol: {data['symbol']}, Current Price: {current_price}")
            await asyncio.sleep(1)  # Wait for 1 second before fetching the prices again

if __name__ == "__main__":
    asyncio.run(main())