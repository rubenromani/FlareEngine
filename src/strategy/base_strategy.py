class Strategy:
    """Base class for all strategies"""

    def __init__(self):
        self.current_positions = {}
        self.initialize()

    def initialize(self):
        """Initialize strategy parameters"""
        pass

    def on_bar(self, bar_event):
        """Handle new bar event"""
        raise NotImplementedError("on_bar method must be implemented in subclasses")