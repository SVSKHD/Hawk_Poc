from storage_state import get_symbol_data, save_symbol_data, save_or_update_start_trade, get_start_trade
from config import symbols_config

for symbol in symbols_config:
    data = get_symbol_data(symbol['symbol'])
    if data:
        print(data)
    else:
        print(f"No data found for {symbol['symbol']}")

save_or_update_start_trade(True)

data = get_start_trade()
print("state", data)
