import pandas as pd
import numpy as np
from numba import njit
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "..", "data", "spy.csv")


def load_market_data(filepath):
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

def create_optimized_arrays(dates_epoch, opens, highs, lows, closes, volumes):
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


def convert_to_optimized_structure(df):
    """Convert DataFrame to optimized structure."""
    
    dates_epoch = (df['Date'].astype(np.int64) // 10**9).to_numpy(dtype=np.int64)
    opens = df['Open'].to_numpy(dtype=np.float32)
    highs = df['High'].to_numpy(dtype=np.float32)
    lows = df['Low'].to_numpy(dtype=np.float32)
    closes = df['Close'].to_numpy(dtype=np.float32)
    volumes = df['Volume'].to_numpy(dtype=np.float64)

    data = create_optimized_arrays(dates_epoch, opens, highs, lows, closes, volumes)
    return data

class DataManager:
    def __init__ (self, csv_filepath=None):
        self.raw_data = None
        self.optimized_data = None
        self.date_mapping = {}

        if csv_filepath:
            self.load_from_csv(csv_filepath)

    def load_from_csv(self, csv_filepath):

        self.raw_data = load_market_data(csv_filepath)
        self.optimized_data = convert_to_optimized_structure(self.raw_data)

        for i, date in enumerate(self.raw_data['Date']):
            self.date_mapping[i] = date

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
    

data_manager = DataManager(data_path)