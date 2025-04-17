from src.core.dispatcher import Dispatcher

class Strategy:
    """Base class for all strategies"""

    def __init__(self):
        self.current_positions = {}
        self.dispatcher = Dispatcher()

    def on_bar(self, bar_event):
        """Handle new bar event"""
        raise NotImplementedError("on_bar method must be implemented in subclasses")
    
    def emit_order(self, order_event):
        self.dispatcher.publish("strategy_order", self, order_event)