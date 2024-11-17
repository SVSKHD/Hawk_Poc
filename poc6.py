from state2 import TradingState
def calculate_pip_difference(symbol, current_price, start_price):
    """
    Calculate pip difference and determine threshold direction.

    :param symbol: Dictionary containing symbol configuration.
    :param current_price: Current market price.
    :param start_price: Price at the start of the trade.
    :return: Dictionary with calculated values.
    """
    symbol_pip = symbol['pip_size']
    symbol_pip_difference = symbol['positive_pip_difference']
    symbol_name = symbol['symbol']

    result = (current_price - start_price) / symbol_pip
    threshold_calculator = result / symbol_pip_difference
    direction = "up" if threshold_calculator > 1 else "down" if threshold_calculator < -1 else None

    data = {
        'symbol': symbol_name,
        'symbol_pip_difference': result,
        'format_symbol_pip_difference': threshold_calculator,
        'direction': direction,
        'current_price': current_price
    }
    return data


def process_prices_with_hedging(symbol, prices, start_price):
    """
    Process prices to evaluate thresholds and handle hedging for both directions.

    :param symbol: Dictionary containing symbol configuration.
    :param prices: List of prices to process.
    :param start_price: Starting price for calculations.
    """
    for price in prices:
        data = calculate_pip_difference(symbol, price, start_price)
        direction = data['direction']

        if direction == "up":
            # Handle positive threshold
            if not state.positive_threshold and data['format_symbol_pip_difference'] >= 1:
                state.update(positive_threshold=True, positive_threshold_price=price)
                print(f"Positive threshold reached for {data['symbol']} at {price}.")

            # Handle positive hedging (only after threshold is reached)
            if state.positive_threshold and not state.positive_hedging and data['format_symbol_pip_difference'] <= 0.5:
                state.update(positive_hedging=True, positive_hedging_price=price)
                print(f"Positive hedging activated for {data['symbol']} at {price}.")

        elif direction == "down":
            # Handle negative threshold
            if not state.negative_threshold and data['format_symbol_pip_difference'] <= -1:
                state.update(negative_threshold=True, negative_threshold_price=price)
                print(f"Negative threshold reached for {data['symbol']} at {price}.")

            # Handle negative hedging (only after threshold is reached)
            if state.negative_threshold and not state.negative_hedging and data['format_symbol_pip_difference'] > -0.5:
                state.update(negative_hedging=True, negative_hedging_price=price)
                print(f"Negative hedging activated for {data['symbol']} at {price}.")

        # Print the status for each price
        print(
            f"symbol: {data['symbol']} | direction: {direction} | "
            f"threshold: {round(data['format_symbol_pip_difference'], 2)} | "
            f"current_price: {data['current_price']} | "
            f"positive_threshold_reached: {state.positive_threshold} | "
            f"positive_hedging_activated: {state.positive_hedging} | "
            f"negative_threshold_reached: {state.negative_threshold} | "
            f"negative_hedging_activated: {state.negative_hedging}"
        )

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

positive_prices = [1.0695, 1.07000, 1.07005, 1.07010, 1.07015, 1.07010, 1.07000, 1.0682]
negative_prices = [1.06640, 1.06560, 1.06450, 1.06380, 1.06300, 1.06600]

process_prices_with_hedging(symbol_data, positive_prices, 1.06770)
print("positive-case", state)
process_prices_with_hedging(symbol_data, negative_prices, 1.06770)
print("negative-case", state)