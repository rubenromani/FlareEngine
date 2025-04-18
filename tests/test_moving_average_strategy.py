import unittest
import numpy as np
import logging
import time
from src.strategy.examples.moving_average_strategy import MovingAverageStrategy
from src.core.data_manager import DataManager, BacktestDataStream, data_path
from src.core.event import BarEvent, OrderEvent, FillEvent

class TestMovingAverageStrategy(unittest.TestCase):
    def setUp(self):
        self.symbol = "XXX"
        self.moving_average_strategy = MovingAverageStrategy()
        self.data_stream = BacktestDataStream(symbol=self.symbol, csv_filepath=data_path)
        self.data_manager = DataManager([self.data_stream])
        

    def test_on_bar(self):
        """Test the on_bar method of the MovingAverageStrategy"""

        while True:
            bar = self.data_manager.get_next_bar(self.symbol)
            if bar is None:
                break

            self.moving_average_strategy.on_bar(BarEvent(symbol='XXX', bar=bar))

if __name__ == '__main__':
    unittest.main()