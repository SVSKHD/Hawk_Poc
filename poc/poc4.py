from state2 import TradingState

state = TradingState()

symbol_data = {
    "symbol": "EURUSD",
    "positive_pip_difference": 15,
    "negative_pip_difference": -15,
    "positive_pip_range": 17,
    "negative_pip_range": -17,
    "close_trade_at": 10,
    "close_trade_at_opposite_direction": 8,
    "pip_size": 0.0001,
    "lot_size": 1.0,
}


def check_thresholds(symbol, current_price, start_price):
    """
    Check thresholds and trigger hedging if conditions are met.

    :param symbol: Dictionary containing symbol configuration.
    :param current_price: Current market price.
    :param start_price: Price at the start of the trade.
    :return: Tuple (result, format_result, threshold_calculator, direction).
    """
    symbol_pip = symbol['pip_size']
    symbol_pip_difference = symbol['positive_pip_difference']
    result = current_price - start_price
    format_result = result / symbol_pip
    threshold_calculator = format_result / symbol_pip_difference

    direction = None

    if state.threshold:
        print(f"Threshold already reached at {current_price}, format_result: {format_result}")
        if not state.hedging and format_result < 0.5:
            state.update(hedging=True, hedging_price=current_price)
            print(f"Hedging activated at {current_price}.")
    else:
        print(f"Threshold not reached at {current_price}")

    if state.hedging:
        print("hedging")

    if not state.threshold:
        if threshold_calculator > 1:  # Price moved significantly upwards
            direction = "up"
            state.update(threshold=True, threshold_price=current_price)
            print(f"Threshold reached: Price moved up to {current_price}.")
        elif threshold_calculator < -1:  # Price moved significantly downwards
            direction = "down"
            state.update(threshold=True, threshold_price=current_price)
            print(f"Threshold reached: Price moved down to {current_price}.")
        else:
            state.update(threshold=False, threshold_price="no")

    return result, format_result, threshold_calculator, direction


def process_prices(symbol, prices, start_price):
    for price in prices:
        result = check_thresholds(symbol, price, start_price)
        print(result)


def calculate_pip_difference(symbol, current_price, start_price):
    symbol_pip = symbol['pip_size']
    symbol_pip_difference = symbol['positive_pip_difference']
    symbol_name = symbol['symbol']

    result = (current_price - start_price) / symbol_pip
    threshold_calculator = result / symbol_pip_difference
    direction = None
    if threshold_calculator > 1:
        direction = "up"
    elif threshold_calculator < 1:
        direction = "down"
    else:
        direction = None
    data = {'symbol': symbol_name, 'symbol_pip_difference': result,
            'format_symbol_pip_difference': threshold_calculator, 'direction': direction, 'current_price': current_price}
    # print(symbol_name, symbol_pip_difference, symbol_pip, result, threshold_calculator)
    return data


# Example usage
prices = [1.0695, 1.07000, 1.07005, 1.07010, 1.07015, 1.07010, 1.07000, 1.0682]
# process_prices(symbol_data, prices, 1.0686)

for price in prices:
    data = calculate_pip_difference(symbol_data, price, 1.06770)
    if data['format_symbol_pip_difference'] >= 1:
        print(
            f"symbol : {data['symbol']} threshold:{round(data['format_symbol_pip_difference'], 2)} current_price:{data['current_price']}")
    if data['format_symbol_pip_difference'] < 0.5:
        print(
            f"symbol : {data['symbol']} threshold:{round(data['format_symbol_pip_difference'], 2)} hedging activated")
