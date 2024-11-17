class TradeState:
    def __init__(self):
        self.threshold = False
        self.trade_placed = False
        self.trade_direction = None
        self.trade_price = None
        self.hedging = False
        self.hedging_price = None

    def reset_threshold(self):
        self.threshold = False
        self.trade_placed = False
        self.trade_direction = None
        self.trade_price = None

    def activate_hedging(self, current_price):
        self.hedging = True
        self.hedging_price = current_price

    def deactivate_hedging(self):
        self.hedging = False
        self.hedging_price = None

    def set_trade(self, direction, current_price):
        self.trade_placed = True
        self.trade_direction = direction
        self.trade_price = current_price

    def clear_trade(self):
        self.trade_placed = False
        self.trade_direction = None
        self.trade_price = None

    def __repr__(self):
        return (f"TradeState(threshold={self.threshold}, trade_placed={self.trade_placed}, "
                f"trade_direction={self.trade_direction}, trade_price={self.trade_price}, "
                f"hedging={self.hedging}, hedging_price={self.hedging_price})")