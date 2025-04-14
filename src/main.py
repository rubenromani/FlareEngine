import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
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

    print(df.head())

load_market_data(data_path)
