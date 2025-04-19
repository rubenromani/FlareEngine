import pandas as pd
import numpy as np
import os
import time
import threading
from collections import deque
from datetime import datetime
from src.logging.logger_provider import get_logger
from src.core.types import Bar
from src.core.dispatcher import Dispatcher
from src.core.event import BarEvent

logger = get_logger(__name__, "CRITICAL")  

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "..", "data", "spy.csv")

class DataManager:
    """Class to manages data streams"""
    def __init__(self, data_streams):
        self.lock = threading.Lock()

        if not isinstance(data_streams, list):
            raise ValueError("data_streams should be a list of DataStream objects")
        
        self.dispatcher = Dispatcher()
        self._data_streams = {}
        self._bars = {}
        self._threads = {}

        for i in range(len(data_streams)):
            self._data_streams[data_streams[i].symbol] = data_streams[i]
            self._bars[data_streams[i].symbol] = deque()

    '''
    def _backtest_data_stream_callback(self, symbol, bar):
        """Callback function for backtest data stream"""
        #logger.info(f"Backtest data stream callback for {symbol}: {bar}")
        with self.lock:
            self._bars[symbol].append(bar)
    '''

    def _live_data_stream_callback(self, symbol, bar):
        """Callback function for live data stream"""
        pass

    def get_next_bars(self):
        """Get next bar for a specific symbol"""
        valid = False
        for symbol, data_stream in self._data_streams.items():
            bar = None
            if data_stream.type == 'backtest':
                bar = data_stream.get_next_bar()

            """
            else:
                with self.lock:
                    try:
                        logger.info(f"Getting next bar for {symbol}: {self._bars[symbol][0]}")
                        bar = self._bars[symbol].popleft()
                    except IndexError:
                        logger.info(f"No bars available for {symbol}")
                        return None
            """
            if bar is not None:
                self.dispatcher.publish(f"new_bar_{symbol}", self, BarEvent(bar, symbol ))
                valid = True
        
        return valid;
        
    def is_data_stream_working(self, symbol):
        """Check if the data stream is working"""
        if self._data_streams[symbol].type == 'backtest':
            return False

        return self._threads[symbol].is_alive() or len(self._bars[symbol]) != 0

    def start_data_live_streams(self):
        """Start all data streams"""
        logger.info("Starting data streams")
        for key, value in self._data_streams.items():
            if value.type == 'backtest':
                continue
            logger.info(f"Starting data stream for {key}")
            self._threads[key] = threading.Thread(
                target=value.run, 
                args=(
                    None if value.type == "backtest" else self._live_data_stream_callback, ),
                    )
            self._threads[key].start()

    def stop_data_live_streams(self):
        """Stop all data streams"""
        for i in range(len(self._data_streams)):
            self._threads[self._data_streams[i].symbol].join()


class DataStream():

    def __init__(self, symbol):
        self._symbol = symbol
        pass
    
    @property
    def symbol(self):
        """Get symbol"""
        return self._symbol

class BacktestDataStream(DataStream):
    def __init__ (self, symbol, csv_filepath=None):
        super().__init__(symbol)
        self.raw_data = None
        self.optimized_data = None
        self._bar_index = 0
        self._type = "backtest"

        if csv_filepath:
            self.load_from_csv(csv_filepath)

    def load_from_csv(self, csv_filepath):

        self.raw_data = self._load_market_data(csv_filepath)
        self.optimized_data = self._convert_to_optimized_structure(self.raw_data)
        self._bars = self._create_bars()
        

    def _load_market_data(self, filepath):
        """Load OHLCV market data from a CSV file into a pandas DataFrame."""

        dtypes = {
            'Open': 'float32', 
            'High': 'float32', 
            'Low': 'float32', 
            'Close': 'float32',
            'Volume': 'float64'
        }


        df = pd.read_csv(filepath, 
                         dtype=dtypes, 
                         parse_dates=['Date'],
                         usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])


        return df

    def _create_optimized_arrays(self, dates_epoch, opens, highs, lows, closes, volumes):
        """Create optimized arrays for OHLCV data."""

        n = len(dates_epoch)
        data = np.zeros(n, dtype=[
            ('date', np.int64),
            ('open', np.float32),
            ('high', np.float32),
            ('low', np.float32),
            ('close', np.float32),
            ('volume', np.float64),
        ])


        data['date'] = dates_epoch
        data['open'] = opens
        data['high'] = highs
        data['low'] = lows
        data['close'] = closes
        data['volume'] = volumes

        return data

    def _convert_to_optimized_structure(self, df):
        """Convert DataFrame to optimized structure."""

        dates_epoch = (df['Date'].astype(np.int64) // 10**9).to_numpy(dtype=np.int64)
        opens = df['Open'].to_numpy(dtype=np.float32)
        highs = df['High'].to_numpy(dtype=np.float32)
        lows = df['Low'].to_numpy(dtype=np.float32)
        closes = df['Close'].to_numpy(dtype=np.float32)
        volumes = df['Volume'].to_numpy(dtype=np.float64)

        data = self._create_optimized_arrays(dates_epoch, opens, highs, lows, closes, volumes)
        return data
    
    def _create_bars(self):
        
        bars = []
        for i in range(len(self.optimized_data)):
            bar = Bar(
                timestamp=self.optimized_data['date'][i],
                open=self.optimized_data['open'][i],
                high=self.optimized_data['high'][i],
                low=self.optimized_data['low'][i],
                close=self.optimized_data['close'][i],
                volume=self.optimized_data['volume'][i]
            )
            bars.append(bar)

        return np.array(bars, dtype=Bar)
    
    def get_next_bar(self):
        """Get next bar for backtesting"""

        try:
            bar = self._bars[self._bar_index]
            logger.info(f"Date: {datetime.fromtimestamp(bar.timestamp)}")
            self._bar_index += 1
            return bar
        except IndexError:
            return None

    @property  
    def dates(self):
        return self.optimized_data['date']
    
    @property
    def opens(self):
        return self.optimized_data['open']
    
    @property
    def highs(self):
        return self.optimized_data['high']
    
    @property
    def lows(self):
        return self.optimized_data['low']
    
    @property
    def closes(self):
        return self.optimized_data['close']
    
    @property
    def volumes(self):
        return self.optimized_data['volume']
    
    @property
    def bars(self):
        return self._bars
    
    @property
    def type(self):
        return self._type
    
class LiveDataStream(DataStream):
    pass