class Bar:
    """Sigle price bar"""

    def __init__(self, timestamp, open, high, low, close, volume, additional_data=None):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.additional_data = additional_data or {}