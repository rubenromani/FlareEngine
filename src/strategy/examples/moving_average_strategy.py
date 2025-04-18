import numpy as np
from datetime import datetime
from src.strategy.base_strategy import Strategy
from src.core.event import BarEvent, OrderEvent, FillEvent

class MovingAverageStrategy(Strategy):
    def __init__(self, old_data=None):
        super().__init__()
        self.short_window = 50
        self.long_window = 200
        self.short_ma = 0.0
        self.long_ma = 0.0
        self.position = 0
        self.data_buffer = old_data or np.array([], dtype=np.float32)
        
        if self.data_buffer.size >= self.long_window:
            self.data_buffer = self.data_buffer[-self.long_window:]
            self.short_ma = np.mean(self.data_buffer[-self.short_window:])
            self.long_ma = np.mean(self.data_buffer[-self.long_window:])

        

    def on_new_bar(self, sender, bar_event):
        """Handle new bar event"""
        self.data_buffer = np.append(self.data_buffer, bar_event.bar.close)

        order_event = None
        if len(self.data_buffer) > self.long_window:
            self.short_ma = np.mean(self.data_buffer[-self.short_window:])
            self.long_ma = np.mean(self.data_buffer[-self.long_window:])
            order_event = self._check_signals(bar_event)

        if self.data_buffer.size >= 2*self.long_window:
            self.data_buffer = self.data_buffer[-self.long_window:]

        if order_event is not None:
            self.emit_order(order_event)

    def _check_signals(self, bar_event):
        """Check for buy/sell signals"""
        if self.position < 1 and self.short_ma > self.long_ma:
            self.position = 1
            return OrderEvent(bar_event.symbol, 'MARKET', 1, 'BUY')
        elif self.position > -1 and self.short_ma < self.long_ma:
            self.position = -1
            return OrderEvent(bar_event.symbol, 'MARKET', 1, 'SELL')
        
        # TODO: replace position with a request from portfolio