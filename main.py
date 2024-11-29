from config import symbols_config
from storage_state import get_symbol_data, get_start_trade, save_or_update_start_trade, clear_all_keys
from utils import connect_mt5
from fetch_prices import fetch_price, get_server_time
from trade_placement import place_trade_notify, hedge_place_trade, close_trades_by_symbol
import asyncio
from logic import analyze_pip_difference
from datetime import datetime, timedelta

async def check_thresholds_and_trade(symbol, start_price, current_price):
    symbol_name = symbol["symbol"]
    get_data = get_symbol_data(symbol_name)
    if not get_data:
        print(f"Symbol data not found for {symbol_name}. Running analyze_pip_difference to generate data.")
        get_data = analyze_pip_difference(symbol, start_price, current_price)
    else:
        start_price = get_data['start_price']
        current_price = get_data['current_price']

    thresholds = get_data['thresholds']
    # Positive thresholds
    positive_threshold = get_data['positive_threshold']
    positive_threshold_price = get_data['positive_threshold_price']
    positive_second_threshold = get_data['positive_second_threshold']
    positive_second_threshold_price = get_data['positive_second_threshold_price']
    # Negative thresholds
    negative_threshold = get_data['negative_threshold']
    negative_threshold_price = get_data['negative_threshold_price']
    negative_second_threshold = get_data['negative_second_threshold']
    negative_second_threshold_price = get_data['negative_second_threshold_price']

    positive_hedging = get_data['positive_hedging']
    positive_hedging_price = get_data['positive_hedging_price']
    negative_hedging = get_data['negative_hedging']
    negative_hedging_price = get_data['negative_hedging_price']

    if positive_threshold and 1 < thresholds < 1.5:
        print("positive_threshold", positive_threshold, positive_threshold_price)
        await place_trade_notify(symbol, "buy", 1.0)
    if negative_threshold and -1.5 < thresholds < -1:
        print("negative_threshold", negative_threshold, negative_threshold_price)
        await place_trade_notify(symbol, "sell", 1.0)
    if positive_second_threshold and thresholds >= 2:
        print("positive_second_threshold", positive_second_threshold, positive_second_threshold_price)
        await close_trades_by_symbol(symbol)
    if negative_second_threshold and thresholds <= -2:
        print("negative_second_threshold", negative_second_threshold, negative_second_threshold_price)
        await close_trades_by_symbol(symbol)
    if positive_hedging:
        print("positive_hedging", positive_hedging, positive_hedging_price)
        await hedge_place_trade(symbol, "sell", 1.0)
    if negative_hedging:
        print("negative_hedging", negative_hedging, negative_hedging_price)
        await hedge_place_trade(symbol, "buy", 1.0)

async def calculate_time_difference():
    server_time = await get_server_time()
    if not server_time:
        print("Failed to fetch server time.")
        return None

    local_time = datetime.utcnow()
    time_difference = server_time - local_time
    return time_difference

async def main():
    connect = await connect_mt5()
    if connect:
        price_data = []
        time_difference = await calculate_time_difference()
        if time_difference is None:
            print("Failed to calculate time difference. Exiting.")
            return

        server_time = datetime.utcnow() + time_difference
        print(f"Current server time: {server_time}")

        local_12am = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + time_difference).time()
        local_12pm = (datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0) + time_difference).time()
        print(f"Server 12 AM will be at local time: {local_12am}")
        print(f"Server 12 PM will be at local time: {local_12pm}")

        if server_time.hour >= 0 and server_time.hour < 12:
            print("It's between 12 AM and 12 PM server time. Setting start_trade to True and fetching start prices.")
            save_or_update_start_trade(False)
            for symbol in symbols_config:
                start_price = await fetch_price(symbol, "start")
                if start_price is not None:
                    price_data.append({
                        'symbol': symbol['symbol'],
                        'start_price': start_price,
                        'current_price': start_price
                    })
        else:
            print("It's 12 PM or later server time. Setting start_trade to False.")
            save_or_update_start_trade(False)
            clear_all_keys()

        while True:
            server_time = datetime.utcnow() + time_difference
            print(f"Current server time: {server_time}")

            if server_time.hour == 0 and server_time.minute == 0:
                print("It's server 12 AM. Setting start_trade to True and fetching start prices.")
                save_or_update_start_trade(True)
                price_data = []
                for symbol in symbols_config:
                    start_price = await fetch_price(symbol, "start")
                    if start_price is not None:
                        price_data.append({
                            'symbol': symbol['symbol'],
                            'start_price': start_price,
                            'current_price': start_price
                        })
            elif server_time.hour >= 12:
                print("It's server 12 PM or later. Setting start_trade to False and clearing all keys.")
                save_or_update_start_trade(False)
                clear_all_keys()

            start_trade = get_start_trade()

            if start_trade:
                for data in price_data:
                    current_price = await fetch_price(data, "current")
                    if current_price is not None:
                        data['current_price'] = current_price
                        symbol = next((s for s in symbols_config if s['symbol'] == data['symbol']), None)
                        if symbol:
                            analyze_pip_difference(symbol, data['start_price'], data['current_price'])
                            await check_thresholds_and_trade(symbol, data['start_price'], data['current_price'])
            else:
                print("Start trade is False. Waiting for server 12 AM.")

            await asyncio.sleep(60)  # Sleep for 1 minute to reduce API calls

if __name__ == "__main__":
    asyncio.run(main())