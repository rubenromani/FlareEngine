import numpy as np
from strategy.base_strategy import Strategy
from core.event import BarEvent, OrderEvent, FillEvent
from core.dispatcher import dispatch

class MovingAverageStrategy(Strategy):
    def __init__(self, old_data=None):
        super().__init__()
        self.short_window = 50
        self.long_window = 200
        self.short_ma = 0.0
        self.long_ma = 0.0
        self.data_buffer = old_data or np.array([], dtype=np.float32)
        
        if self.data_buffer and len(self.data_buffer) >= self.long_window:
            self.data_buffer = self.data_buffer[-self.long_window:]
            self.short_ma = np.mean(self.data_buffer[-self.short_window:])
            self.long_ma = np.mean(self.data_buffer[-self.long_window:])

        

    def on_bar(self, bar_event):
        """Handle new bar event"""
        self.data_buffer = np.append(self.data_buffer, bar_event.bar.close)

        order_event = None
        if len(self.data_buffer) > self.long_window:
            self.short_ma = np.mean(self.data_buffer[-self.short_window:])
            self.long_ma = np.mean(self.data_buffer[-self.long_window:])
            order_event = self._check_signals(bar_event)

        if order_event is not None:
            dispatch(self, order_event)

    def _check_signals(self, bar_event):
        """Check for buy/sell signals"""
        if self.short_ma > self.long_ma:
            return OrderEvent(bar_event.symbol, 'MARKET', 1, 'BUY')
        elif self.short_ma < self.long_ma:
            return OrderEvent(bar_event.symbol, 'MARKET', 1, 'SELL')