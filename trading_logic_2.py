from state2 import TradingState


def calculate_pip_difference(symbol, current_price, start_price):
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


def evaluate_threshold_and_hedging(
        state,
        threshold_key,
        hedging_key,
        current_price,
        threshold_condition,
        hedging_condition,
        threshold_price_key,
        hedging_price_key
):
    """
    Evaluates thresholds and activates hedging based on given conditions.

    :param state: The trading state object.
    :param threshold_key: The attribute name for the threshold flag (e.g., 'positive_threshold').
    :param hedging_key: The attribute name for the hedging flag (e.g., 'positive_hedging').
    :param current_price: The current price to evaluate.
    :param threshold_condition: Condition to check for threshold activation.
    :param hedging_condition: Condition to check for hedging activation.
    :param threshold_price_key: The attribute name for storing the threshold price.
    :param hedging_price_key: The attribute name for storing the hedging price.
    """
    if not getattr(state, threshold_key) and threshold_condition:
        state.update(**{threshold_key: True, threshold_price_key: current_price})
    if getattr(state, threshold_key) and not getattr(state, hedging_key) and hedging_condition:
        state.update(**{hedging_key: True, hedging_price_key: current_price})


def process_prices_with_hedging(symbol, current_price, start_price):
    state = TradingState.get_instance(symbol['symbol'])
    data = calculate_pip_difference(symbol, current_price, start_price)
    direction = data['direction']

    # Evaluate positive threshold and hedging
    evaluate_threshold_and_hedging(
        state=state,
        threshold_key='positive_threshold',
        hedging_key='positive_hedging',
        current_price=current_price,
        threshold_condition=data['format_symbol_pip_difference'] >= 1,
        hedging_condition=data['format_symbol_pip_difference'] <= 0.5,
        threshold_price_key='positive_threshold_price',
        hedging_price_key='positive_hedging_price'
    )

    # Evaluate negative threshold and hedging
    evaluate_threshold_and_hedging(
        state=state,
        threshold_key='negative_threshold',
        hedging_key='negative_hedging',
        current_price=current_price,
        threshold_condition=data['format_symbol_pip_difference'] <= -1,
        hedging_condition=data['format_symbol_pip_difference'] > -0.5,
        threshold_price_key='negative_threshold_price',
        hedging_price_key='negative_hedging_price'
    )

    message = f"symbol: {symbol['symbol']} | direction: {direction} | threshold: {round(data['format_symbol_pip_difference'], 2)} | current_price: {data['current_price']} | positive_threshold_reached: {state.positive_threshold} | positive_hedging_activated: {state.positive_hedging} | negative_threshold_reached: {state.negative_threshold} | negative_hedging_activated: {state.negative_hedging}"

    data = {
        'symbol': symbol['symbol'],
        'direction': direction,
        'threshold': round(data['format_symbol_pip_difference'], 2),
        'current_price': data['current_price'],
        'positive_threshold_reached': state.positive_threshold,
        'positive_hedging_activated': state.positive_hedging,
        'negative_threshold_reached': state.negative_threshold,
        'negative_hedging_activated': state.negative_hedging
    }
    # print(message)
    return data