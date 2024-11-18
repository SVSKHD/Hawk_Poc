from state import TradeState

# state = TradeState()
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


def print_data(symbol, state: TradeState, current_price, start_price):
    symbol_name = symbol['symbol']
    symbol_pip = symbol['pip_size']
    symbol_positive = symbol['positive_pip_difference']
    difference = current_price - start_price
    result = difference / symbol_pip
    threshold_result = result / symbol_positive

    # Determine the direction of the price movement
    direction = "Up" if difference > 0 else "Down"

    # Check if the threshold is reached and place the first trade
    if not state.trade_placed and abs(threshold_result) >= 1:
        state.threshold = True
        state.set_trade(direction, current_price)
        print(f"Trade placed ({direction}) for {symbol_name} at {current_price}")
        return  # Exit early after placing the trade

    # Check if hedging conditions are met
    if state.trade_placed:
        trade_difference = abs(current_price - state.trade_price) / symbol_pip
        trade_threshold = trade_difference / symbol_positive

        if direction != state.trade_direction and trade_threshold <= 0.5 and not state.hedging:
            state.activate_hedging(current_price)
            hedging_direction = "Buy" if state.trade_direction == "Down" else "Sell"
            print(f"Hedging activated ({hedging_direction}) for {symbol_name} at {current_price}")
            return  # Exit early after activating hedging

    # Reset the threshold and trade state if conditions are no longer valid
    if state.trade_placed and abs(threshold_result) < 1 and not state.hedging:
        print(f"Threshold condition reset for {symbol_name} at {current_price}")
        state.reset_threshold()

    # Deactivate hedging if conditions change
    if state.hedging and abs(threshold_result) > 0.5:
        print(f"Hedging deactivated for {symbol_name} at {current_price}")
        state.deactivate_hedging()


# Initialize state
# state = {
#     'trade_placed': False,
#     'trade_direction': None,
#     'trade_price': None,
#     'hedging': False,
#     'hedging_price': None
# }

# Test prices
prices = [
    1.07010,  # Threshold reached, trade placed (Up)
    1.06740,  # Opposite movement, hedging activated (Down)
    1.06650,  # Hedging remains active
    1.06630,  # Hedging continues
    1.07005,  # No new threshold, existing logic holds
    1.06600  # No threshold, no hedging
]

# Run the test
for current in prices:
    print_data(symbol_data, TradeState, current, 1.06590)
