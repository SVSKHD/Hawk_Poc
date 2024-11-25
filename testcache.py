from storage_state import get_symbol_data
from config import symbols_config


for symbol in symbols_config:
    data = get_symbol_data(symbol['symbol'])
    if data:
        print(data)
    else:
        print(f"No data found for {symbol['symbol']}")