# Define symbol data correctly without the trailing comma
symbol_data = {
    "symbol": "EURUSD",
    "positive_pip_difference": 15,
    "negative_pip_difference": -15,
    "positive_pip_range": 17,
    "negative_pip_range": -17,
    "close_trade_at": 10,
    "close_trade_at_opposite_direction": 8,
    "pip_size": 0.0001,
    "lot_size": 1.0
}


def calculate_pip_difference_and_threshold(symbol, current_price, start_price, state):
    pip = symbol["pip_size"]
    pip_difference = symbol['positive_pip_difference']
    difference = current_price - start_price
    formatted_difference = difference / pip
    threshold = None
    direction = None
    hedging = None

    # Check for threshold without a trade being placed
    if not state['threshold']:
        if formatted_difference < 0:
            threshold = formatted_difference / pip_difference
            if abs(threshold) >= 1:
                state['threshold'] = True
                state['trade_placed'] = True
                state['threshold_price'] = current_price
            direction = "down"

        elif formatted_difference > 0:
            threshold = formatted_difference / pip_difference
            if threshold >= 1:
                state['threshold'] = True
                state['trade_placed'] = True
                state['threshold_price'] = current_price
            direction = "up"

    # Print "Trade Placed" and check for hedging logic after threshold is hit
    if state['threshold'] and not state['trade_placed']:
        print(f"Trade Placed at {current_price}")
        state['trade_placed'] = True  # Set trade placed to prevent re-execution

    # Additional hedging check (example placeholder logic)
    if state['trade_placed'] and state['hedging']:
        # Implement hedging logic here, for example:
        print(f"Hedging check triggered at {current_price}")

    data = {
        'symbol': symbol["symbol"],
        'pip_difference': formatted_difference,
        'format_difference': formatted_difference,
        'thresholds': threshold,
        'direction': direction,
        'hedging': hedging,
    }
    return data


# Initial state
state = {'threshold': False, 'threshold_price': None, 'hedging': False, 'hedging_price': None, 'trade_placed': False,
         'hedging_trade_placed_at': None}

# Sample price list
current_prices = [
    1.07010,
    1.07110,
    1.07120,
    1.07130,
    1.07140,
    1.07150,
    1.07160,
    1.07170
]

for price in current_prices:
    print("current_price", price)
    result = calculate_pip_difference_and_threshold(symbol_data, price, 1.0686, state)
    print(result)
