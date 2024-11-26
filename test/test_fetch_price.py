import asyncio
import MetaTrader5 as mt5
import logging
from utils import log_error_and_notify
import pytz
from datetime import datetime, timedelta
from storage_state import save_or_update_start_trade, get_symbol_data, get_start_trade

start_trade = get_start_trade()

async def fetch_current_price(symbol):
    symbol_name = symbol["symbol"]
    # Ensure the symbol is available in Market Watch
    selected = await asyncio.to_thread(mt5.symbol_select, symbol_name, True)
    if not selected:
        await log_error_and_notify(f"Failed to select symbol {symbol_name} for fetching current price.")
        return None

    # Fetch current price
    tick = await asyncio.to_thread(mt5.symbol_info_tick, symbol_name)
    if tick:
        return tick.bid  # or tick.ask depending on your logic
    else:
        await log_error_and_notify(f"Failed to get current price for {symbol_name}")
        return None


async def fetch_price(symbol, price_type):
    symbol_name = symbol["symbol"]

    # Ensure the symbol is selected in Market Watch
    selected = await asyncio.to_thread(mt5.symbol_select, symbol_name, True)
    if not selected:
        await log_error_and_notify(f"Failed to select symbol {symbol_name} for fetching {price_type} price.")
        return None

    if price_type == "current":
        tick = await asyncio.to_thread(mt5.symbol_info_tick, symbol_name)
        if tick:
            logging.info(f"Fetching current price for {symbol_name} - current_price: {tick.bid}")
            return tick.bid  # or tick.ask depending on requirements

    elif price_type == "start":
        now = datetime.now(pytz.timezone('Asia/Kolkata'))
        if now.weekday() == 0:  # Monday
            # Fetch the price at the start of Monday
            start_of_monday_utc = now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
            rates = await asyncio.to_thread(mt5.copy_rates_from, symbol_name, mt5.TIMEFRAME_M5, start_of_monday_utc, 1)
            if rates and len(rates) > 0:
                if not start_trade:
                    save_or_update_start_trade(True)
                logging.info(f"Fetching Monday start price for {symbol_name} - start_price: {rates[0]['close']}")
                return rates[0]["close"]

        # For other days, fetch the start price of the day
        start_of_day_utc = now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
        rates = await asyncio.to_thread(mt5.copy_rates_from, symbol_name, mt5.TIMEFRAME_M5, start_of_day_utc, 1)
        if rates and len(rates) > 0:
            logging.info(f"Fetching start price for {symbol_name} - start_price: {rates[0]['close']}")
            return rates[0]["close"]

    await log_error_and_notify(f"Failed to get {price_type} price for {symbol_name}")
    return None


async def fetch_friday_closing_price(symbol):
    """Asynchronously fetch the last Friday's closing price for a symbol."""
    today = datetime.now(pytz.timezone('Asia/Kolkata'))
    days_ago = (today.weekday() + 3) % 7 + 2
    last_friday = today - timedelta(days=days_ago)
    last_friday = last_friday.replace(hour=23, minute=59, second=59)
    utc_from = last_friday.astimezone(pytz.utc)

    rates = await asyncio.to_thread(mt5.copy_rates_from, symbol["symbol"], mt5.TIMEFRAME_M5, utc_from, 1)
    if rates is not None and len(rates) > 0:
        closing_price = rates[0]['close']
        logging.info(f"Fetched last Friday's closing price for {symbol['symbol']}: {closing_price}")
        return closing_price

    await log_error_and_notify(f"Failed to get last Friday's closing price for {symbol['symbol']}")
    return None


async def main():
    connect = await connect_mt5()
    if connect:
        price_data = []
        for symbol in symbols_config:
            start_price = await fetch_price(symbol, "start")
            if start_price is not None:
                price_data.append({
                    'symbol': symbol['symbol'],
                    'start_price': start_price,
                    'current_price': start_price
                })
        while start_trade:
            current_time = datetime.now().time()
            if current_time.hour == 12 and current_time.minute == 0:
                print("It's 12 PM. Setting start_trade to False.")
                save_or_update_start_trade(False)
                start_trade = False
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