from enum import Enum

class Bar:
    """Represents a single price bar in financial markets.
   
    This class encapsulates OHLCV (Open, High, Low, Close, Volume) data for a specific 
    time period in financial market data, with optional additional data that can be stored.
    
    Attributes:
        timestamp (int): The timestamp representing when this bar occurred.
        open (float): The opening price for this time period.
        high (float): The highest price reached during this time period.
        low (float): The lowest price reached during this time period.
        close (float): The closing price for this time period.
        volume (float): The trading volume during this time period.
        additional_data (dict): Optional dictionary containing any additional data 
            associated with this bar. Defaults to an empty dictionary.
    """

    def __init__(self, timestamp: int, open: float, high: float, low: float, close: float, volume: float, additional_data: dict =None):
        """Initialize a new price bar.

        Args:
            timestamp (int): The timestamp representing when this bar occurred.
            open (float): The opening price for this time period.
            high (float): The highest price reached during this time period.
            low (float): The lowest price reached during this time period.
            close (float): The closing price for this time period.
            volume (float): The trading volume during this time period.
            additional_data (dict, optional): Dictionary containing any additional data
                associated with this bar. Defaults to None, which will be converted to an empty dict.
        """
        self._timestamp = timestamp
        self._open = open
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume
        self._additional_data = additional_data or {}
        

    @property
    def timestamp(self) -> int:
        """Get the timestamp of this bar.
        
        Returns:
            int: The timestamp when this bar occurred.
        """
        return self._timestamp
        
    @property
    def open(self) -> float:
        """Get the opening price of this bar.
        
        Returns:
            float: The opening price for this time period.
        """
        return self._open
        
    @property
    def high(self) -> float:
        """Get the highest price of this bar.
        
        Returns:
            float: The highest price reached during this time period.
        """
        return self._high
        
    @property
    def low(self) -> float:
        """Get the lowest price of this bar.
        
        Returns:
            float: The lowest price reached during this time period.
        """
        return self._low
        
    @property
    def close(self) -> float:
        """Get the closing price of this bar.
        
        Returns:
            float: The closing price for this time period.
        """
        return self._close
        
    @property
    def volume(self) -> float:
        """Get the trading volume of this bar.
        
        Returns:
            float: The trading volume during this time period.
        """
        return self._volume
        
    @property
    def additional_data(self) -> dict:
        """Get the additional data associated with this bar.
        
        Returns:
            dict: Dictionary containing any additional data associated with this bar.
        """
        return self._additional_data


class Transaction:
    """Represents a trading transaction.

    This class stores information about a single transaction including
    timestamp, symbol, quantity, direction, price, and commission.

    Attributes:
        timestamp (int): Unix timestamp representing when the transaction occurred.
        symbol (str): The ticker symbol or identifier of the financial instrument.
        quantity (int): The number of units traded.
        direction (str): The direction of the transaction (e.g., "buy", "sell").
        price (float): The price per unit of the financial instrument.
        commission (float): The fee charged for executing the transaction.
    """

    def __init__(self, timestamp : int, symbol: str, quantity: int, direction: str, price : float, commission : float):
        """Initialize a new transaction.
       
       Args:
           timestamp (int): Unix timestamp representing when the transaction occurred.
           symbol (str): The ticker symbol or identifier of the financial instrument.
           quantity (int): The number of units traded.
           direction (str): The direction of the transaction (e.g., "buy", "sell").
           price (float): The price per unit of the financial instrument.
           commission (float): The fee charged for executing the transaction.
       """
        self._timestamp = timestamp
        self._symbol = symbol
        self._quantity = quantity
        self._direction = direction
        self._price = price
        self._commission = commission


    @property
    def timestamp(self) -> int:
        """Get the timestamp of this transaction.
        
        Returns:
            int: The Unix timestamp representing when the transaction occurred.
        """
        return self._timestamp
    
    @property
    def symbol(self) -> str:
        """Get the symbol of this transaction.
        
        Returns:
            str: The ticker symbol or identifier of the financial instrument.
        """
        return self._symbol
    
    @property
    def quantity(self) -> int:
        """Get the quantity of this transaction.
        
        Returns:
            int: The number of units traded.
        """
        return self._quantity
    
    @property
    def direction(self) -> str:
        """Get the direction of this transaction.
        
        Returns:
            str: The direction of the transaction (e.g., "buy", "sell").
        """
        return self._direction
    
    @property
    def price(self) -> float:
        """Get the price of this transaction.
        
        Returns:
            float: The price per unit of the financial instrument.
        """
        return self._price
    
    @property
    def commission(self) -> float:
        """Get the commission of this transaction.
        
        Returns:
            float: The fee charged for executing the transaction.
        """
        return self._commission
    
    from enum import Enum

class Timeframe(Enum):
   """Enumeration of standard financial chart timeframes.

   This enum represents common chart timeframes used in financial market analysis,
   from 1-minute to daily intervals.

   Attributes:
       MINUTE_1: 1-minute timeframe
       MINUTE_5: 5-minute timeframe
       MINUTE_15: 15-minute timeframe
       MINUTE_30: 30-minute timeframe
       HOUR_1: 1-hour timeframe
       HOUR_4: 4-hour timeframe
       DAY_1: Daily timeframe
   """

   MINUTE_1 = "1m"
   MINUTE_5 = "5m"
   MINUTE_15 = "15m"
   MINUTE_30 = "30m"
   HOUR_1 = "1h"
   HOUR_4 = "4h"
   DAY_1 = "1d"

   def __str__(self):
        """Return the string value when the enum is printed."""
        return self.value

   @classmethod
   def from_string(cls, value):
       """Convert a string representation to the corresponding Timeframe enum.

       Args:
           value (str): String representation of the timeframe (e.g., "1m", "1h")

       Returns:
           Timeframe: The matching Timeframe enum value

       Raises:
           ValueError: If the provided string doesn't match any timeframe
       """
       for timeframe in cls:
           if timeframe.value == value:
               return timeframe
       raise ValueError(f"Invalid timeframe string: {value}")

   def to_minutes(self):
       """Convert the timeframe to equivalent minutes.

       Returns:
           int: The number of minutes represented by this timeframe
       """
       if self.value.endswith("m"):
           return int(self.value[:-1])
       elif self.value.endswith("h"):
           return int(self.value[:-1]) * 60
       elif self.value.endswith("d"):
           return 24 * 60
       else:
           raise ValueError(f"Cannot convert {self.value} to minutes")