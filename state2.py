class TradingState:
    _instance = None

    def __init__(self):
        self.positive_hedging = False  # For buy direction hedging
        self.negative_hedging = False  # For sell direction hedging
        self.positive_threshold = False  # Indicates positive threshold reached
        self.negative_threshold = False  # Indicates negative threshold reached
        self.positive_hedging_price = None  # Price for buy direction hedging
        self.negative_hedging_price = None  # Price for sell direction hedging
        self.positive_threshold_price = None  # Price for positive threshold
        self.negative_threshold_price = None  # Price for negative threshold

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TradingState, cls).__new__(cls)
        return cls._instance

    def update(self, **kwargs):
        """
        Update the state with the provided keyword arguments.
        """
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
            f"negative_hedging_price={self.negative_hedging_price})"
        )