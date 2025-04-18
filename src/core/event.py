from src.core.types import Bar

class Event:
    """Base class for events system"""
    pass

class BarEvent(Event):
    """On new bar event"""
    
    def __init__(self, bar, symbol):
        self.bar = bar
        self.symbol = symbol
        self.type = 'BAR'

class OrderEvent(Event):
    """Orger generation evet"""

    def __init__(self, symbol, order_type, quantity, direction, price=None):
        self.symbol = symbol
        self.order_type = order_type # 'LIMIT', 'MARKET', 'STOP'
        self.quantity = quantity
        self.direction = direction # 'BUY' or 'SELL'
        self.price = price
        self.type = 'ORDER'

    def __str__(self):
        return (f"{self.symbol}, "
                f"{self.order_type}, "
                f"{self.quantity}, "
                f"{self.direction}, "
                f"{self.price}, "
                f"{self.type}")

class FillEvent(Event):
    """Order execution event"""

    def __init__(self, timestamp, symbol, quantity, direction, fill_price, commission=None):
        self.timestamp = timestamp
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.fill_price = fill_price
        self.commission = commission or 0.0
        self.type = 'FILL'
        