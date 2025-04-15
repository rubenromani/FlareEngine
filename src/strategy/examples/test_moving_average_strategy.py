import unittest
import numpy as np
from src.strategy.examples.moving_average_strategy import MovingAverageStrategy
from src.main import DataManager, data_path
from src.core.event import BarEvent, OrderEvent, FillEvent

class TestMovingAverageStrategy(unittest.TestCase):
    def setUp(self):
        self.moving_average_strategy = MovingAverageStrategy()
        self.data_manager = DataManager(data_path)
        

    def test_on_bar(self):
        for i, bar in enumerate(self.data_manager.bars):
            self.moving_average_strategy.on_bar(BarEvent(symbol='XXX', bar=bar))

if __name__ == '__main__':
    unittest.main()