import asyncio
import logging
from config import symbols_config
from utils import connect_mt5
from fetch_prices import fetch_current_price, fetch_price
from trade_logic_normal import process_prices_with_hedging
from trade_placement_logic import place_trade_notify, close_trades_by_symbol

logging.basicConfig(level=logging.INFO)

def check_thresholds(data, symbol):
    symbol_name = data['symbol']
    threshold = data['threshold']
    current_price = data['current_price']
    lot_size = symbol['lot_size']
    print("symbol", symbol)
    if data['positive_threshold_reached'] and threshold > 1:
        logging.info(f"Positive threshold reached for {symbol_name} at {current_price} with threshold {threshold}.")
        asyncio.create_task(place_trade_notify(symbol, "buy", lot_size))
    elif data['negative_threshold_reached'] and threshold < -1:
        logging.info(f"Negative threshold reached for {symbol_name} at {current_price} with threshold {threshold}.")
        asyncio.create_task(place_trade_notify(symbol, "sell", lot_size))
    elif data['positive_hedging_activated'] and threshold < 0.5:
        logging.info(f"Positive hedging reached for {symbol_name} at {current_price} with threshold {threshold}.")
    elif data['negative_hedging_activated'] and threshold >= -0.5:
        logging.info(f"Negative hedging reached for {symbol_name} at {current_price} with threshold {threshold}.")
    elif data['positive_threshold_reached'] and threshold >= 2:
        print("Closing trades for symbol", symbol_name)
    elif data['negative_threshold_reached'] and threshold <= -2:
        print("Closing trades for symbol", symbol_name)

    # handle hedging and threshold deactivated case
    # handle the trade discord bot code.
    # chek the profit and also close code and also add the state to the data.

async def main():
    connect = await connect_mt5()
    if connect:
        logging.info("Connected to MT5")
        price_data = []
        for symbol in symbols_config:
            start_price = await fetch_price(symbol, "start")
            if start_price is not None:
                price_data.append({
                    'symbol': symbol['symbol'],
                    'start_price': start_price,
                    'current_price': start_price
                })

        while True:
            for data in price_data:
                current_price = await fetch_current_price({'symbol': data['symbol']})
                if current_price is not None:
                    data['current_price'] = current_price
                    symbol = next((s for s in symbols_config if s['symbol'] == data['symbol']), None)
                    if symbol:
                        threshold_triggered = process_prices_with_hedging(symbol, data['current_price'], data['start_price'])
                        check_thresholds(threshold_triggered, symbol)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())