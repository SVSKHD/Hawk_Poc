class TradingState:
    _instances = {}

    def __init__(self):
        self.positive_hedging = False
        self.negative_hedging = False
        self.positive_threshold = False
        self.negative_threshold = False
        self.positive_hedging_price = None
        self.negative_hedging_price = None
        self.positive_threshold_price = None
        self.negative_threshold_price = None
        self.account = None  # Add account attribute
        self.stop_trades = False
        self.daily_profit = False

    @classmethod
    def get_instance(cls, symbol):
        if symbol not in cls._instances:
            cls._instances[symbol] = cls()
        return cls._instances[symbol]

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return (
            f"TradingState(positive_threshold={self.positive_threshold}, "
            f"positive_hedging={self.positive_hedging}, "
            f"positive_threshold_price={self.positive_threshold_price}, "
            f"positive_hedging_price={self.positive_hedging_price}, "
            f"negative_threshold={self.negative_threshold}, "
            f"negative_hedging={self.negative_hedging}, "
            f"negative_threshold_price={self.negative_threshold_price}, "
            f"negative_hedging_price={self.negative_hedging_price}, "
            f"account={self.account})"
        )