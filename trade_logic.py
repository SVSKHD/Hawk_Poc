
def calculate_pip_difference(symbol, current_price, start_price):
    pip_size = symbol['pip_size']
    print(pip_size)
    result = current_price - start_price
    formatted_difference = result / pip_size
    threshold_reached = result / symbol["positive_pip_range"]
    data = {
        'symbol': symbol["symbol"],
        'pip_difference': result,
        'format_difference': formatted_difference,
        'thresholds': threshold_reached
    }
    return data


def threshold_detector(symbol, threshold):
    print("threshold", symbol["symbol"], threshold)

def execute_trade(symbol, start_price, current_price):
    threshold = calculate_pip_difference(symbol, start_price, current_price)
    dat a =threshold_detector(symbol, threshold)
    print("execute" ,data)
    return data




# def threshold_trigger(symbol, pip_data):
#     if pip_data>1:
#         print("positive direction ^")
#     elif pip_data<0:
#         print("negative direction >")

# def execute_logic(symbol, current_price, start_price):
#     result = calculate_pip_difference(symbol, current_price, start_price)
#     threshold = result['thresholds']
#     threshold_trigger(symbol,threshold)


start_price = 1.07130

symbol_data = {
    "symbol": "EURUSD",
    "positive_pip_difference": 0.0015,
    "negative_pip_difference": -15,
    "positive_pip_range": 17,
    "negative_pip_range": -17,
    "close_trade_at": 10,
    "close_trade_at_opposite_direction": 8,
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
]

execute_trade(symbol_data, start_price, start_price)

# for price in prices:
#     calculate = execute_logic(symbol_data, price, start_price)
#     print(calculate)
