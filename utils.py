import asyncio
import MetaTrader5 as mt5
import logging
from notifications import send_discord_message_async


async def log_error_and_notify(message):
    logging.error(message)
    await send_discord_message_async(message)


async def connect_mt5():
    """Asynchronously initialize and log in to MetaTrader 5."""
    initialized = await asyncio.to_thread(mt5.initialize)
    if not initialized:
        print("Failed to initialize MetaTrader5")
        return False

    login = 213171528  # Replace with actual login
    password = "AHe@Yps3"  # Replace with actual password
    server = "OctaFX-Demo"  # Replace with actual server

    authorized = await asyncio.to_thread(mt5.login, login, password, server)
    if not authorized:
        print(f"Login failed for account {login}")
        return False

    print(f"Successfully logged into account {login} on server {server}")
    return True
