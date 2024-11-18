start_price = 1.07130
initial_start_price = start_price  # Store the initial start price

symbol_data = {
    "symbol": "EURUSD",
    "pip_size": 0.0001,
    "lot_size": 1.0
}

prices = [
    1.07100,
    1.07110,
    1.07150,
    1.07180,
    1.07200,
    1.07210,
    1.07100,
    1.07050,
    1.07000,
]

trade_state = {
    "trade_open": False,
    "hedge_open": False,
    "initial_trade": None,
    "hedge_trades": [],
    # Removed 'start_price' from trade_state
}

def threshold_trigger(symbol, pip_data, trade_state, current_price):
    data = {
        'action': None,
        'hedge_started': False,
        'hedge_prices': []
    }

    initial_threshold = 5   # Adjusted for testing
    hedging_threshold = 15
    close_threshold = 20    # Thresholds in pips

    if not trade_state['trade_open']:
        if pip_data >= initial_threshold:
            print("Opening initial Buy trade")
            trade_state['trade_open'] = True
            trade_state['initial_trade'] = {
                'type': 'Buy',
                'entry_price': current_price
            }
            data['action'] = 'Buy'
    elif trade_state['trade_open'] and not trade_state['hedge_open']:
        if pip_data <= -hedging_threshold:
            print("Market moved against initial trade. Opening two Sell hedge trades.")
            trade_state['hedge_open'] = True
            trade_state['hedge_trades'].append({
                'type': 'Sell',
                'entry_price': current_price,
                'purpose': 'Compensate Loss'
            })
            trade_state['hedge_trades'].append({
                'type': 'Sell',
                'entry_price': current_price,
                'purpose': 'Profit'
            })
            data['hedge_started'] = True
            data['hedge_prices'] = [current_price, current_price]
    else:
        total_pnl = calculate_total_pnl(trade_state, current_price, symbol['pip_size'])
        if abs(total_pnl) >= close_threshold:
            print("Closing all trades.")
            trade_state['trade_open'] = False
            trade_state['hedge_open'] = False
            trade_state['initial_trade'] = None
            trade_state['hedge_trades'] = []
            data['action'] = 'Close All Trades'
    return data

def calculate_total_pnl(trade_state, current_price, pip_size):
    total_pnl = 0.0
    if trade_state['initial_trade']:
        entry_price = trade_state['initial_trade']['entry_price']
        if trade_state['initial_trade']['type'] == 'Buy':
            pnl = (current_price - entry_price) / pip_size
        else:
            pnl = (entry_price - current_price) / pip_size
        total_pnl += pnl

    for trade in trade_state['hedge_trades']:
        entry_price = trade['entry_price']
        if trade['type'] == 'Buy':
            pnl = (current_price - entry_price) / pip_size
        else:
            pnl = (entry_price - current_price) / pip_size
        total_pnl += pnl
    return total_pnl

for price in prices:
    if not trade_state['trade_open']:
        # No trades are open, use initial_start_price
        pip_difference = (price - initial_start_price) / symbol_data['pip_size']
    else:
        # Trades are open, use the initial trade's entry price
        pip_difference = (price - trade_state['initial_trade']['entry_price']) / symbol_data['pip_size']
    result = threshold_trigger(symbol_data, pip_difference, trade_state, price)
    if result['action']:
        print(f"Action: {result['action']} at price {price}")
    if result['hedge_started']:
        print(f"Hedging started at price {price} {result}")