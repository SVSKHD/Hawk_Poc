import asyncio
import MetaTrader5 as mt5
import logging
from utils import log_error_and_notify

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