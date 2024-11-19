from config import symbols_config
from utils import connect_mt5
from fetch_prices import fetch_current_price, fetch_price
import asyncio
from trade_logic_normal import process_prices_with_hedging

def check_thresholds(data):
    symbol_name = data['symbol']
    threshold = data['threshold']
    current_price = data['current_price']

    if data['positive_threshold_reached'] and threshold > 1:
        print(f"Positive threshold reached for {symbol_name} at {current_price} with threshold {threshold}.")
    elif data['negative_threshold_reached'] and threshold < -1:
        print(f"Negative threshold reached for {symbol_name} at {current_price} with threshold {threshold}.")
    elif data['positive_hedging_activated'] and threshold < 0.5:
        print(f"Positive hedging reached for {symbol_name} at {current_price} with threshold {threshold}.")
    elif data['negative_hedging_activated'] and threshold >= -0.5:
        print(f"Negative hedging reached for {symbol_name} at {current_price} with threshold {threshold}.")

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
                # print(f"Symbol: {symbol['symbol']}, Start Price: {start_price}")

        while True:
            for data in price_data:
                current_price = await fetch_current_price({'symbol': data['symbol']})
                if current_price is not None:
                    data['current_price'] = current_price
                    # print(f"Symbol: {data['symbol']}, Current Price: {current_price} Start price : {round(data['start_price'],4)} {data}")
                    symbol = next((s for s in symbols_config if s['symbol'] == data['symbol']), None)
                    if symbol:
                        threshold_triggered = process_prices_with_hedging(symbol, data['current_price'], data['start_price'])
                        check_thresholds(threshold_triggered)
            await asyncio.sleep(1)  # Wait for 1 second before fetching the prices again


if __name__ == "__main__":
    asyncio.run(main())
