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
from src.core.shared_repository import SharedRepository
from src.core.event import BarEvent

logger = get_logger(__name__, "CRITICAL")  

class DataManager:
    """Class to manages data streams"""
    def __init__(self, data_streams):
        self.lock = threading.Lock()

        if not isinstance(data_streams, list):
            raise ValueError("data_streams should be a list of DataStream objects")
        
        self._data_streams = {}
        self._bars = {}
        self._threads = {}
        self.dispatcher = Dispatcher()
        self.repo = SharedRepository()

        for i in range(len(data_streams)):
            self._data_streams[data_streams[i].symbol] = data_streams[i]

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
        """Get the newt bar"""

        for symbol, data_stream in self._data_streams.items():
            key = f"{symbol}_{data_stream.timeframe}"
            if key not in self._bars:
                if data_stream.type == 'backtest':
                    bar = data_stream.get_next_bar()
                    if bar is not None:
                        self._bars[key] = bar
                
                """
                else:
                    with self.lock:
                        try:
                            logger.info(f"Getting next bar for {symbol}: {self._bars[symbol][0]}")
                            bar = self._bars[symbol].popleft()
                            if bar is not None:
                                self._bars[key] = bar
                        except IndexError:
                            logger.info(f"No bars available for {symbol}")
                """

        if not self._bars: 
            return False

        nearest_key = None
        nearest_time = float('inf')

        for key, bar in self._bars.items():
            if bar.timestamp < nearest_time:
                nearest_time = bar.timestamp
                nearest_key = key

        if nearest_key:
            bar_to_publish = self._bars[nearest_key]
            symbol = nearest_key.split('_')[0]

            # update the price in the repository
            last_prices = self.repo.get("last_prices", default={})
            last_prices[symbol] = bar_to_publish
            self.repo.set("last_prices", last_prices)

            self.dispatcher.publish(f"new_bar_{nearest_key}", self, 
                                   BarEvent(bar_to_publish, symbol))
            del self._bars[nearest_key]
            return True

        return False
        
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

    def __init__(self, symbol, timeframe):
        self._symbol = symbol
        self._timeframe = timeframe
        self._dispatcher = Dispatcher()
        self._repo = SharedRepository()

        data_streams = self._repo.get("data_streams") or []
        new_data_stream = f"symbol_{symbol}_{timeframe}"
        data_streams.append(new_data_stream)
        self._repo.set("data_streams", data_streams)
        self._dispatcher.publish("new_data_stream", self, new_data_stream)
    
    @property
    def symbol(self):
        """Get symbol"""
        return self._symbol
    
    @property
    def timeframe(self):
        """Get the timeframe"""
        return self._timeframe

class BacktestDataStream(DataStream):
    def __init__ (self, symbol, timeframe, csv_filepath=None):
        super().__init__(symbol, timeframe)
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
                         parse_dates=['Datetime'],
                         usecols=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'])


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

        dates_epoch = (df['Datetime'].astype(np.int64) // 10**9).to_numpy(dtype=np.int64)
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