from config import symbols_config
from storage_state import save_symbol_data, delete_symbol_data, get_symbol_data, update_symbol_data
from utils import connect_mt5
from fetch_prices import fetch_price
import asyncio
from logic import analyze_pip_difference


def check_thresholds_and_trade(symbol):
    get_data = get_symbol_data(symbol["symbol"])
    if get_data:
        print("get_data", get_data['symbol'])
        start_price = get_data['start_price']
        current_price = get_data['current_price']
        # positive aspects
        positive_threshold = get_data['positive_threshold']
        positive_threshold_price = get_data['positive_threshold_price']
        positive_second_threshold = get_data['positive_second_threshold']
        positive_second_threshold_price = get_data['positive_second_threshold_price']
        # negative aspects
        negative_threshold = get_data['negative_threshold']
        negative_threshold_price = get_data['negative_threshold_price']
        negative_second_threshold = get_data['negative_second_threshold']
        negative_second_threshold_price = get_data['negative_second_threshold_price']

        positive_hedging = get_data['positive_hedging']
        positive_hedging_price = get_data['positive_hedging_price']
        negative_threshold = get_data['negative_threshold']
        negative_threshold_price = get_data['negative_threshold_price']

        if positive_threshold:
            print("positive_threshold", positive_threshold, positive_threshold_price)
        if negative_threshold:
            print("negative_threshold", negative_threshold, negative_threshold_price)

        if positive_second_threshold:
            print("positive_second_threshold", positive_second_threshold, positive_second_threshold_price)
        if negative_second_threshold:
            print("negative_second_threshold", negative_second_threshold, negative_second_threshold_price)

        if positive_hedging:
            print("positive_hedging", positive_hedging, positive_hedging_price)
        if negative_threshold:
            print("negative_threshold", negative_threshold, negative_threshold_price)

        # current_price = get_data['current_price']
        # symbol = next((s for s in symbols_config if s['symbol'] == symbol), None)
        # if thresold


async def main():
    connect = await connect_mt5()
    if connect:
        price_data = []
        for symbol in symbols_config:
            start_price = await fetch_price(symbol['symbol'], "start")
            if start_price is not None:
                price_data.append({
                    'symbol': symbol['symbol'],
                    'start_price': start_price,
                    'current_price': start_price
                })
        while True:
            for data in price_data:
                current_price = await fetch_price(data['symbol'], "current")
                if current_price is not None:
                    data['current_price'] = current_price
                    symbol = next((s for s in symbols_config if s['symbol'] == data['symbol']), None)
                    print("symbol", symbol)
                    threshold_calculator = analyze_pip_difference(symbol, data['start_price'], data['current_price'])

                    print("threshold_calculator", threshold_calculator)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
