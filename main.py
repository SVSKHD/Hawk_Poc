from config import symbols_config
from storage_state import get_symbol_data, get_start_trade, save_or_update_start_trade, clear_all_keys
from utils import connect_mt5
from fetch_prices import fetch_price
from trade_placement import place_trade_notify, hedge_place_trade, close_trades_by_symbol
import asyncio
from logic import analyze_pip_difference
from datetime import datetime

async def check_thresholds_and_trade(symbol):
    get_data = get_symbol_data(symbol["symbol"])
    if not get_data:
        raise ValueError(f"Symbol data not found for {symbol['symbol']}")
    start_price = get_data['start_price']
    current_price = get_data['current_price']
    thresholds = get_data['thresholds']
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

async def main():
    connect = await connect_mt5()
    if connect:
        price_data = []
        for symbol in symbols_config:
            start_price = await fetch_price(symbol, "start")
            print("checking for 12 am")
            if start_price is not None:
                price_data.append({
                    'symbol': symbol['symbol'],
                    'start_price': start_price,
                    'current_price': start_price
                })
        log_12_am_check = True
        while True:
            start_trade = get_start_trade()
            if not start_trade:
                print("Start trade is False. Waiting for next 12 AM to set it to True.")
                while True:
                    current_time = datetime.now().time()
                    if current_time.hour == 0 and current_time.minute == 0:
                        print("It's 12 AM. Setting start_trade to True.")
                        save_or_update_start_trade(True)
                        break
                    await asyncio.sleep(60)  # Sleep for 1 minute to avoid continuous checking
                continue

            print("start", start_trade)
            current_time = datetime.now().time()
            print(f"Current time: {current_time}")
            if log_12_am_check:
                if current_time.hour == 0 and current_time.minute == 0:
                    if not start_trade:
                        print("It's 12 AM. Setting start_trade to True.")
                        save_or_update_start_trade(True)
                    log_12_am_check = False
                else:
                    print("Checking for 12 AM...")
                await asyncio.sleep(60)  # Sleep for 1 minute to log the time every minute
                continue
            if current_time.hour >= 12:
                print("It's 12 PM or later. Setting start_trade to False.")
                save_or_update_start_trade(False)
                clear_all_keys()
                await asyncio.sleep(60)  # Sleep for 1 minute to avoid continuous checking
                continue

            for data in price_data:
                current_price = await fetch_price(data, "current")
                if current_price is not None:
                    data['current_price'] = current_price
                    symbol = next((s for s in symbols_config if s['symbol'] == data['symbol']), None)
                    analyze_pip_difference(symbol, data['start_price'], data['current_price'])
                    await check_thresholds_and_trade(symbol)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())