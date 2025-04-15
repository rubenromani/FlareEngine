import pandas as pd
import numpy as np
from numba import njit
import os
from core.bar import Bar

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "spy.csv")


class DataManager:
    def __init__ (self, csv_filepath=None):
        self.raw_data = None
        self.optimized_data = None
        self.date_mapping = {}

        if csv_filepath:
            self.load_from_csv(csv_filepath)

    def load_from_csv(self, csv_filepath):

        self.raw_data = self._load_market_data(csv_filepath)
        self.optimized_data = self._convert_to_optimized_structure(self.raw_data)

        self.bars = self._create_bars()
        

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

        self.bars = np.array(bars, dtype=Bar)
    

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
        return self.bars
    

data_manager = DataManager(data_path)