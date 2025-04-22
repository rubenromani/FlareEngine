"""
Available data fields:
    - last_prices: Dict[]
    - available_balance : float
    - data_streams : List[str]
"""

import threading

class SharedRepository:
    _instance = None
 
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedRepository, cls).__new__(cls)
            cls._instance.data = {}
            cls._instance.lock = threading.Lock()
        return cls._instance
    
    def set(self, key, value):
        with self.lock:
            self.data[key] = value

    def get(self, key, default=None):
        with self.lock:
            return self.data.get(key, default)
        
    def delete(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]

    def contains(self, key):
        with self.lock:
            return key in self.data
        
        
    