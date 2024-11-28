import MetaTrader5 as mt5
from datetime import datetime

# Initialize MT5 connection
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Select the GBPUSD symbol in Market Watch
selected = mt5.symbol_select("GBPUSD", True)
if not selected:
    print("Failed to select GBPUSD")
    mt5.shutdown()
    quit()

# Retrieve the latest tick data
last_tick = mt5.symbol_info_tick("GBPUSD")
if last_tick is None:
    print("Failed to get the latest tick data")
    mt5.shutdown()
    quit()

# Convert the timestamp to human-readable format
server_time = datetime.utcfromtimestamp(last_tick.time)
print(f"Server Time (UTC): {server_time}")
print(f"Server Time (Raw Timestamp): {last_tick.time}")

# Fetch local UTC time for comparison
local_utc_time = datetime.utcnow()
print(f"Local Time (UTC): {local_utc_time}")

# Calculate the time difference
time_difference = server_time - local_utc_time
time_difference_hours = time_difference.total_seconds() / 3600
print(f"Time Difference (Server - Local in UTC): {time_difference_hours:.2f} hours")

# Shutdown MT5 connection
mt5.shutdown()
