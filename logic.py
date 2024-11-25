from typing import Dict, List
from storage_state import save_symbol_data, get_symbol_data, update_symbol_data


# 1.check the data and fix the thresholds and hedging and save only when require
def analyze_pip_difference(symbol: Dict, start_price: float, current_price: float):
    symbol_name = symbol["symbol"]
    threshold_data = get_symbol_data(symbol_name)
    print("threshold_data", threshold_data)
    pip_size = symbol.get("pip_size", 0.0001)
    positive_pip_difference = symbol.get("positive_pip_difference", 1)
    pip_difference = (current_price - start_price) / pip_size
    check_thresholds = pip_difference / positive_pip_difference

    data = {'symbol': symbol_name,
            'pip_difference': pip_difference,
            'thresholds': check_thresholds,
            'lot_size': symbol.get("lot_size", 1.0),
            'positive_threshold': False,
            'positive_threshold_price': None,
            'positive_second_threshold': False,
            'positive_second_threshold_price': None,
            'positive_hedging': False,
            # negative-values
            'negative_threshold': False,
            'negative_threshold_price': None,
            'negative_second_threshold': False,
            'negative_second_threshold_price': None,
            'negative_hedging': False,
            'positive_hedging_price': 0,
            'negative_hedging_price': 0,
            'start_price': start_price,
            'current_price': current_price}

    # Check positive thresholds
    if check_thresholds >= 2:
        data['positive_second_threshold'] = True
        data['positive_second_threshold_price'] = current_price
        update_symbol_data(symbol_name, data)

    if check_thresholds >= 1:
        print("Positive threshold met")
        data['positive_threshold'] = True
        data['positive_threshold_price'] = current_price
        save_symbol_data(symbol_name, data)

    if threshold_data and threshold_data['positive_threshold'] and check_thresholds <= 0.5:
        data['positive_hedging'] = True
        data['positive_hedging_price'] = current_price
        update_symbol_data(symbol_name, data)

    # Check negative thresholds
    if check_thresholds <= -2:
        data['negative_second_threshold'] = True
        data['negative_threshold_price'] = current_price
        update_symbol_data(symbol_name, data)

    if check_thresholds <= -1:
        print("Negative threshold met")
        data['negative_threshold'] = True
        data['negative_threshold_price'] = current_price
        save_symbol_data(symbol_name, data)

    if threshold_data and threshold_data['negative_threshold'] and check_thresholds >= -0.5:
        data['negative_hedging'] = True
        data['negative_hedging_price'] = current_price
        update_symbol_data(symbol_name, data)

    print("---------------------------------------------------------------------")

    return data


# Symbol data and input values
# symbol_data = {
#     "symbol": "EURUSD",
#     "positive_pip_difference": 15,
#     "negative_pip_difference": -15,
#     "positive_pip_range": 17,
#     "negative_pip_range": -17,
#     "close_trade_at": 10,
#     "close_trade_at_opposite_direction": 8,
#     "pip_size": 0.0001,
#     "lot_size": 1.0
# }

# positive_values_with_hedging = [1.5015, 1.5031, 1.5008, 1.5007, 1.5006, 1.5005, 1.5004, 1.5002]
# negative_values_with_hedging = [1.4985, 1.4992, 1.4993, 1.4994, 1.4995, 1.4996, 1.4998]
#
# # Threshold dictionaries
# threshold = {'status': False}
# negative_threshold = {'status': False}
#
# # Process positive values
# print("Processing positive values:")
# for price in positive_values_with_hedging:
#     negative_data = analyze_pip_difference(symbol_data, 1.5000, price, threshold, negative_threshold)
#
# # Reset thresholds for negative values
# threshold['status'] = False
# negative_threshold['status'] = False
# print("=======================================================================================")
# # Process negative values
# print("Processing negative values:")
# for price in negative_values_with_hedging:
#     postive_data = analyze_pip_difference(symbol_data, 1.5000, price, threshold, negative_threshold)

#
# data = delete_symbol_data('EURUSD')
# print(data)
