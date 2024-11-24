import asyncio
import MetaTrader5 as mt5
import logging
from utils import log_error_and_notify
import pytz
from datetime import datetime, timedelta


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
    """Fetch price based on type, reusing code for start and current prices."""
    symbol_name = symbol["symbol"]

    # Ensure the symbol is selected in Market Watch
    selected = await asyncio.to_thread(mt5.symbol_select, symbol_name, True)
    if not selected:
        await log_error_and_notify(f"Failed to select symbol {symbol_name} for fetching {price_type} price.")
        return None

    if price_type == "current":
        tick = await asyncio.to_thread(mt5.symbol_info_tick, symbol_name)
        logging.info(f"Fetching current price for {symbol_name}-current_price{tick.bid}")
        if tick:
            return tick.bid  # or tick.ask depending on requirements

    elif price_type == "start":
        now = datetime.now(pytz.timezone('Asia/Kolkata'))
        if now.weekday() == 0:  # Monday
            return await fetch_friday_closing_price(symbol)

        start_of_day_utc = now.replace(hour=0, minute=0, second=0).astimezone(pytz.utc)
        rates = await asyncio.to_thread(mt5.copy_rates_from, symbol_name, mt5.TIMEFRAME_M5, start_of_day_utc, 1)
        if rates:
            logging.info(f"Fetching start price for {symbol_name}-start_price: {rates[0]['close']}")
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
        # print(f"Fetched last Friday's closing price for {symbol}: {closing_price}")
        return closing_price

    print(f"Failed to get last Friday's closing price for {symbol}")
    return None
