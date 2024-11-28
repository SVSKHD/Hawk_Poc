import asyncio
import MetaTrader5 as mt5
import logging
from utils import log_error_and_notify
from datetime import datetime, timedelta


async def get_server_time():
    """Fetch the server's current time using the latest tick."""
    tick = await asyncio.to_thread(mt5.symbol_info_tick, "EURUSD")  # Use any active symbol
    if tick:
        return datetime.utcfromtimestamp(tick.time)  # Server time in UTC
    return None


async def fetch_price(symbol, price_type):
    symbol_name = symbol["symbol"]

    # Ensure the symbol is selected in Market Watch
    selected = await asyncio.to_thread(mt5.symbol_select, symbol_name, True)
    if not selected:
        await log_error_and_notify(f"Failed to select symbol {symbol_name} for fetching {price_type} price.")
        return None

    server_time = await get_server_time()
    if not server_time:
        await log_error_and_notify("Failed to fetch server time.")
        return None

    if price_type == "current":
        tick = await asyncio.to_thread(mt5.symbol_info_tick, symbol_name)
        if tick:
            logging.info(f"Fetching current price for {symbol_name} - current_price: {tick.bid}")
            return tick.bid  # or tick.ask depending on requirements

    elif price_type == "start":
        # Server midnight for the current day
        server_midnight = server_time.replace(hour=0, minute=0, second=0, microsecond=0)
        rates = await asyncio.to_thread(mt5.copy_rates_from, symbol_name, mt5.TIMEFRAME_M5, server_midnight, 1)
        if rates and len(rates) > 0:
            logging.info(f"Fetching start price for {symbol_name} - start_price: {rates[0]['close']}")
            return rates[0]["close"]

    await log_error_and_notify(f"Failed to get {price_type} price for {symbol_name}")
    return None


async def fetch_friday_closing_price(symbol):
    """Fetch the last Friday's closing price using server time."""
    server_time = await get_server_time()
    if not server_time:
        await log_error_and_notify("Failed to fetch server time for Friday's closing price.")
        return None

    # Calculate last Friday's date and time (23:59:59 server time)
    days_since_friday = (server_time.weekday() - 4) % 7
    last_friday = server_time - timedelta(days=days_since_friday)
    last_friday_close_time = last_friday.replace(hour=23, minute=59, second=59, microsecond=0)

    rates = await asyncio.to_thread(mt5.copy_rates_from, symbol["symbol"], mt5.TIMEFRAME_M5, last_friday_close_time, 1)
    if rates and len(rates) > 0:
        closing_price = rates[0]['close']
        logging.info(f"Fetched last Friday's closing price for {symbol['symbol']}: {closing_price}")
        return closing_price

    await log_error_and_notify(f"Failed to get last Friday's closing price for {symbol['symbol']}")
    return None
