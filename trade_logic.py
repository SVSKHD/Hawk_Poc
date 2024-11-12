def calculate_pip_difference(symbol, current_price, start_price):

    result = current_price - start_price
    formatted_difference = result / symbol['pip_size']
    threshold_reached = formatted_difference/symbol[""]
    data = {'symbol': symbol["symbol"], 'pip_difference': result, 'format_difference': formatted_difference, 'thresholds':threshold_reached}

