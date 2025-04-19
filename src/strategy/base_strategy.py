from src.core.dispatcher import Dispatcher
from src.core.event import BarEvent, OrderEvent

class Strategy:
    """Base class for all strategies"""

    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.dispatcher = Dispatcher()
        self.dispatcher.subscribe(f"new_bar_{self.symbol}_{self.timeframe}", self.on_new_bar)

    def _on_new_bar(self, sender, bar_event: BarEvent):
        """Handle new bar event"""
        raise NotImplementedError("on_bar method must be implemented in subclasses")
    
    def _emit_order(self, order_event: OrderEvent):
        self.dispatcher.publish(f"strategy_order", self, order_event)