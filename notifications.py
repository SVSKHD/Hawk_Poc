import aiohttp
from datetime import datetime
import logging

last_message_time = {}
MESSAGE_INTERVAL = 60

general_url = "https://discord.com/api/webhooks/1286192684834488350/gmXLG-RJT7WdiVNcT5Jw610lstwHRrU-lMmEgcBmQ538HlJp7ya1UyY7MJ46n5OAlIrk"
trade_url = "https://discord.com/api/webhooks/1305415279303458866/JkDauJ4ZSc0ACmz6DP01dPmtqIsGO12mz5SspSBAEUUpYrXUznEtSuQrCYG3czHmQ9Ny"


async def send_discord_message_async(message):
    webhook_url = general_url
    data = {"content": message}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=data) as response:
                if response.status == 204:
                    print("Message sent successfully!")
                else:
                    print(f"Failed to send message: {response.status}, {await response.text()}")
        except Exception as e:
            print(f"Error sending message: {e}")


async def send_limited_message(symbol, message):
    current_time = datetime.now()
    last_time = last_message_time.get(symbol)
    if last_time is None or (current_time - last_time).total_seconds() > MESSAGE_INTERVAL:
        logging.info(f"Sending message for {symbol}: {message}")
        await send_discord_message_async(message)
        last_message_time[symbol] = current_time
    else:
        logging.info(f"Message for {symbol} rate-limited; not sent.")


async def send_discord_message_trade_async(message):
    webhook_url = trade_url
    data = {"content": message}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=data) as response:
                if response.status == 204:
                    print("Message sent successfully!")
                else:
                    print(f"Failed to send message: {response.status}, {await response.text()}")
        except Exception as e:
            print(f"Error sending message: {e}")