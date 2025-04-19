from src.core.dispatcher import Dispatcher
from src.core.event import BarEvent, OrderEvent

class Strategy:
    """Base class for all strategies"""

    def __init__(self, symbol):
        self.symbol = symbol
        self.dispatcher = Dispatcher()
        self.dispatcher.subscribe(f"new_bar_{symbol}", self.on_new_bar)

    def on_new_bar(self, sender, bar_event: BarEvent):
        """Handle new bar event"""
        raise NotImplementedError("on_bar method must be implemented in subclasses")
    
    def emit_order(self, order_event: OrderEvent):
        self.dispatcher.publish("strategy_order", self, order_event)