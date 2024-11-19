import asyncio
import MetaTrader5 as mt5
from utils import get_open_positions
from datetime import datetime
from notifications import send_discord_message_async, send_limited_message

TRADE_LIMIT = 3

async def place_trade_notify(symbol, action, lot_size):
    """Asynchronously place a trade and notify via Discord."""
    open_positions = await get_open_positions({"symbol": symbol})
    if open_positions["no_of_positions"] >= TRADE_LIMIT:
        await send_limited_message(symbol, f"Trade limit reached for {symbol}. No further trades will be placed.")
        return  # Skip trade placement if limit is reached
    selected = await asyncio.to_thread(mt5.symbol_select, symbol, True)
    if not selected:
        print(f"Failed to select symbol {symbol}")
        return

    price_info = await asyncio.to_thread(mt5.symbol_info_tick, symbol)
    if price_info is None:
        print(f"Failed to get tick information for {symbol}")
        return

    price = price_info.ask if action == 'buy' else price_info.bid
    lot = lot_size if lot_size is not None else 1.0
    deviation = 50

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = await asyncio.to_thread(mt5.order_send, request)

    if result is None:
        message = f"Order send error: {mt5.last_error()}"
        print(message)
        await send_discord_message_async(message)
    else:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            message = f"Trade request failed for {symbol}, retcode={result.retcode}"
        else:
            now = datetime.now()
            message = f"Trade executed successfully at {now}, order={result}"

        print(message)