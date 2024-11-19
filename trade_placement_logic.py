from MetaTrader5 import mt5

async def place_order(symbol, action, volume):
    """
    Place an order on MT5.

    :param symbol: Symbol to place the order on.
    :param action: Action to take (BUY/SELL).
    :param volume: Volume of the order.
    :return: Order result.
    """
    request = {
        "action": action,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_MARKET,
        "price": 0,
        "sl": 0,
        "tp": 0,
        "deviation": 20,
        "magic": 234000,
        "comment": "Hawk POC"
    }

    result = mt5.order_send(request)
    return result

async def close_order(order):
    """
    Close an order on MT5.

    :param order: Order to close.
    :return: Close order result.
    """
    request = {
        "action": mt5.ORDER_ACTION_CLOSE,
        "ticket": order.ticket,
        "volume": order.volume
    }

    result = mt5.order_send(request)
    return result


async def close_all_orders():
    """
    Close all orders on MT5.
    """
    orders = mt5.orders_get()
    for order in orders:
        await close_order(order)
    print("All orders closed.")
