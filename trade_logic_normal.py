from state2 import TradingState

state = TradingState()
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


def calculate_next_hedging_prices(activated_price, pip_difference, count=3):
    """
    Generate additional hedging prices after hedging is activated.

    :param activated_price: The price at which hedging was activated.
    :param pip_difference: Pip difference for subsequent hedging prices.
    :param count: Number of additional hedging prices to generate.
    :return: List of hedging prices.
    """
    return [activated_price + (i * pip_difference) for i in range(1, count + 1)]


def process_prices_with_hedging(symbol, current_price, start_price):
    """
    Process prices to evaluate thresholds and handle hedging for both directions.

    :param symbol: Dictionary containing symbol configuration.
    :param prices: List of prices to process.
    :param start_price: Starting price for calculations.
    """
    data = calculate_pip_difference(symbol, current_price, start_price)
    direction = data['direction']

    # Debugging logs
    print(f"Debug: Evaluating price {current_price}, Direction: {direction}, Threshold Difference: {data['format_symbol_pip_difference']}")

    # Handle positive thresholds and hedging
    if not state.positive_threshold and data['format_symbol_pip_difference'] >= 1:
        state.update(positive_threshold=True, positive_threshold_price=current_price)
        print(f"Positive threshold reached for {data['symbol']} at {current_price}.")

    if state.positive_threshold and not state.positive_hedging and data['format_symbol_pip_difference'] <= 0.5:
        state.update(positive_hedging=True, positive_hedging_price=current_price)
        print(f"Positive hedging activated for {data['symbol']} at {current_price}.")

    # Handle negative thresholds and hedging
    if not state.negative_threshold and data['format_symbol_pip_difference'] <= -1:
        state.update(negative_threshold=True, negative_threshold_price=current_price)
        print(f"Negative threshold reached for {data['symbol']} at {current_price}.")

    if state.negative_threshold and not state.negative_hedging and data['format_symbol_pip_difference'] > -0.5:
        state.update(negative_hedging=True, negative_hedging_price=current_price)
        print(f"Negative hedging activated for {data['symbol']} at {current_price}.")

    # Final debug logs for each price
    print(
        f"symbol: {data['symbol']} | direction: {direction} | "
        f"threshold: {round(data['format_symbol_pip_difference'], 2)} | "
        f"current_price: {data['current_price']} | "
        f"positive_threshold_reached: {state.positive_threshold} | "
        f"positive_hedging_activated: {state.positive_hedging} | "
        f"negative_threshold_reached: {state.negative_threshold} | "
        f"negative_hedging_activated: {state.negative_hedging}"
    )



