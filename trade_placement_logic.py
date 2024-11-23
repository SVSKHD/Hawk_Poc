import asyncio
import MetaTrader5 as mt5
from utils import get_open_positions
from datetime import datetime
from notifications import send_discord_message_async, send_discord_message_trade_async

TRADE_LIMIT = 2
HEDGE_TRADE_LIMIT = 2 * TRADE_LIMIT


async def place_trade_notify(symbol, action, lot_size):
    """Asynchronously place a trade and notify via Discord."""
    symbol_name = symbol['symbol']
    open_positions = await get_open_positions({"symbol": symbol_name})
    if open_positions["no_of_positions"] >= TRADE_LIMIT:
        await send_discord_message_trade_async(symbol,
                                               f"Trade limit reached for {symbol}. No further trades will be placed.")
        return  # Skip trade placement if limit is reached
    selected = await asyncio.to_thread(mt5.symbol_select, symbol_name, True)
    if not selected:
        print(f"Failed to select symbol {symbol}")
        return

    price_info = await asyncio.to_thread(mt5.symbol_info_tick, symbol_name)
    if price_info is None:
        print(f"Failed to get tick information for {symbol}")
        return

    price = price_info.ask if action == 'buy' else price_info.bid
    lot = lot_size if lot_size is not None else 1.0
    deviation = 50

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol_name,
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
        await send_discord_message_trade_async(message)
    else:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            message = f"Trade request failed for {symbol}, retcode={result.retcode}"
        else:
            now = datetime.now()
            message = f"Trade executed successfully at {now}, order={result}"
        print(message)


async def hedge_place_trade(symbol, action, lot_size):
    symbol_name = symbol['symbol']
    open_positions = await get_open_positions({"symbol": symbol_name})
    current_open_positions = open_positions["no_of_positions"]

    if current_open_positions == TRADE_LIMIT + HEDGE_TRADE_LIMIT:
        await send_discord_message_trade_async(f"Trade limit reached for {symbol}. No further hedging trades will be placed.")
        return  # Skip trade placement if limit is reached

    selected = await asyncio.to_thread(mt5.symbol_select, symbol_name, True)
    if not selected:
        print(f"Failed to select symbol {symbol}")
        return

    price_info = await asyncio.to_thread(mt5.symbol_info_tick, symbol_name)
    if price_info is None:
        print(f"Failed to get tick information for {symbol}")
        return

    price = price_info.ask if action == 'buy' else price_info.bid
    lot = lot_size if lot_size is not None else 1.0
    deviation = 50

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol_name,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": deviation,
        "magic": 234000,
        "comment": "hedge trade by script",
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
            message = f"Hedge trade request failed for {symbol}, retcode={result.retcode}"
        else:
            now = datetime.now()
            message = f"Hedge trade executed successfully at symbol : {symbol_name}  {now}, order={result}"

        print(message)
        await send_discord_message_trade_async(message)


async def close_trades_by_symbol(symbol):
    symbol_name = symbol['symbol']
    open_positions = await asyncio.to_thread(mt5.positions_get, symbol=symbol)

    if open_positions is None or len(open_positions) == 0:
        print(f"No open positions for {symbol}.")
        return

    for position in open_positions:
        ticket = position.ticket
        lot = position.volume
        trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        symbol_info = await asyncio.to_thread(mt5.symbol_info, symbol)

        if symbol_info is None:
            print(f"Symbol {symbol} not found.")
            continue

        price = symbol_info.bid if trade_type == mt5.ORDER_TYPE_SELL else symbol_info.ask

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": trade_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "Closing trade by script",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = await asyncio.to_thread(mt5.order_send, close_request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            message = f"Failed to close trade {ticket} for {symbol}, error code: {result.retcode}"
        else:
            message = f"Successfully closed trade {ticket} for {symbol}."

        print(message)
        await send_discord_message_trade_async(message)
