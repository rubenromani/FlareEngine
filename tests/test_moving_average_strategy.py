import unittest
import os
from src.core.types import Timeframe
from src.strategy.examples.moving_average_strategy import MovingAverageStrategy
from src.core.data_manager import DataManager, BacktestDataStream

script_dir = os.path.dirname(os.path.abspath(__file__))
spy_data_1d_path = os.path.join(script_dir, "..", "data", "spy.csv")
synth_data_1h_path = os.path.join(script_dir, "..", "data", "synth_data_1h.csv")

class TestMovingAverageStrategy(unittest.TestCase):
    def setUp(self):
        self.symbol_spy = "SPY"
        self.spy_timeframe = Timeframe.DAY_1
        self.moving_average_strategy = MovingAverageStrategy(symbol=self.symbol_spy, timeframe=self.spy_timeframe)
        self.data_stream_spy = BacktestDataStream(symbol=self.symbol_spy, timeframe=Timeframe.DAY_1 ,csv_filepath=spy_data_1d_path)
        self.symbol_synth = "XXX"
        self.synth_timeframe = Timeframe.HOUR_1
        self.moving_average_strategy = MovingAverageStrategy(symbol=self.symbol_synth, timeframe=self.synth_timeframe)
        self.data_stream_synth = BacktestDataStream(symbol=self.symbol_synth, timeframe=self.synth_timeframe, csv_filepath=synth_data_1h_path)
        self.data_manager = DataManager([self.data_stream_spy, self.data_stream_synth])
        

    def test_on_bar(self):
        """Test the on_bar method of the MovingAverageStrategy"""

        while self.data_manager.get_next_bars():
            pass

if __name__ == '__main__':
    unittest.main()