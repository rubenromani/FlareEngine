"""Event system module for trading application.

This module defines the event classes used throughout the trading system.
Events are used to communicate between different components of the system,
such as the exchange, portfolio, and strategy.

The module implements a hierarchical event system with a base Event class
and specific event types like BarEvent, OrderEvent, and FillEvent.

"""
from datetime import datetime
from src.core.types import Bar


class Event:
    """Base class for the event system.
    
    This class serves as the parent class for all events in the trading system.
    All specific event types should inherit from this class.
    """

    _id = 0

    def __init__(self):
        self._id = Event._id
        Event._id += 1 

    @property
    def id(self):
        return self._id

class BarEvent(Event):
    """Event representing a new price bar.
    
    This event is triggered when a new price bar is available for a symbol.
    
    Attributes:
        bar (Bar): The price bar object.
        symbol (str): The financial instrument symbol.
        type (str): The event type identifier, always 'BAR'.
    """
    
    def __init__(self, bar: Bar, symbol: str):
        """Initialize a new bar event.
        
        Args:
            bar (Bar): The price bar object.
            symbol (str): The financial instrument symbol.
        """
        super.__init__(self)
        self._bar = bar
        self._symbol = symbol
        self._type = 'BAR'
    
    @property
    def bar(self) -> Bar:
        """Get the price bar.
        
        Returns:
            Bar: The price bar object.
        """
        return self._bar
    
    @property
    def symbol(self) -> str:
        """Get the symbol.
        
        Returns:
            str: The financial instrument symbol.
        """
        return self._symbol
    
    @property
    def type(self) -> str:
        """Get the event type.
        
        Returns:
            str: The event type identifier, always 'BAR'.
        """
        return self._type
    
    def __str__(self):
        """String representation of the bar event.
        
        Returns:
            str: A string containing all bar event details.
        """
        return (f"ID: {self._id},"
                f"Symbol: {self._symbol}, "
                f"Datetime: {datetime.fromtimestamp(self._bar.timestamp).strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Open: {self._bar.open}, "
                f"Hgh: {self._bar.high}, "
                f"Low: {self._bar.low}, "
                f"Close: {self._bar.close}, "
                f"Volume: {self._bar.volume}, "
                f"Event type: {self._type}")


class OrderEvent(Event):
    """Event for order generation.
    
    This event is triggered when a new order needs to be submitted.
    
    Attributes:
        symbol (str): The financial instrument symbol.
        order_type (str): The type of order ('LIMIT', 'MARKET', 'STOP').
        quantity (int): The number of units in the order.
        direction (str): The direction of the order ('BUY' or 'SELL').
        price (float, optional): The price for limit and stop orders. Defaults to None.
        type (str): The event type identifier, always 'ORDER'.
    """

    def __init__(self, symbol: str, order_type: str, quantity: int, direction: str, price: float=None):
        """Initialize a new order event.
        
        Args:
            symbol (str): The financial instrument symbol.
            order_type (str): The type of order ('LIMIT', 'MARKET', 'STOP').
            quantity (int): The number of units in the order.
            direction (str): The direction of the order ('BUY' or 'SELL').
            price (float, optional): The price for limit and stop orders. Defaults to None.
        """
        super.__init__(self)
        self._symbol = symbol
        self._order_type = order_type  # 'LIMIT', 'MARKET', 'STOP'
        self._quantity = quantity
        self._direction = direction  # 'BUY' or 'SELL'
        self._price = price
        self._type = 'ORDER'
    
    @property
    def symbol(self) -> str:
        """Get the symbol.
        
        Returns:
            str: The financial instrument symbol.
        """
        return self._symbol
    
    @property
    def order_type(self) -> str:
        """Get the order type.
        
        Returns:
            str: The type of order ('LIMIT', 'MARKET', 'STOP').
        """
        return self._order_type
    
    @property
    def quantity(self) -> int:
        """Get the quantity.
        
        Returns:
            int: The number of units in the order.
        """
        return self._quantity
    
    @property
    def direction(self) -> str:
        """Get the direction.
        
        Returns:
            str: The direction of the order ('BUY' or 'SELL').
        """
        return self._direction
    
    @property
    def price(self) -> float:
        """Get the price.
        
        Returns:
            float: The price for limit and stop orders.
        """
        return self._price
    
    @property
    def type(self) -> str:
        """Get the event type.
        
        Returns:
            str: The event type identifier, always 'ORDER'.
        """
        return self._type

    def __str__(self):
        """String representation of the order event.
        
        Returns:
            str: A string containing all order details.
        """
        return (f"ID: {self._id},"
                f"Symbol: {self._symbol}, "
                f"Order type: {self._order_type}, "
                f"Quantity: {self._quantity}, "
                f"Direction: {self._direction}, "
                f"Price: {self._price}, "
                f"Event type: {self._type}")


class FillEvent(Event):
    """Event for order execution.
    
    This event is triggered when an order has been filled (executed).
    
    Attributes:
        timestamp (int): Unix timestamp when the order was filled.
        symbol (str): The financial instrument symbol.
        quantity (int): The number of units filled.
        direction (str): The direction of the fill ('BUY' or 'SELL').
        fill_price (float): The price at which the order was filled.
        commission (float): The commission charged for the transaction. Defaults to 0.0.
        type (str): The event type identifier, always 'FILL'.
    """

    def __init__(self, timestamp: int, symbol: str, quantity: int, direction: str, fill_price: float, commission: float=None, order_ref: int):
        """Initialize a new fill event.
        
        Args:
            timestamp (int): Unix timestamp when the order was filled.
            symbol (str): The financial instrument symbol.
            quantity (int): The number of units filled.
            direction (str): The direction of the fill ('BUY' or 'SELL').
            fill_price (float): The price at which the order was filled.
            commission (float, optional): The commission charged for the transaction. Defaults to None.
        """
        super.__init__(self)
        self._timestamp = timestamp
        self._symbol = symbol
        self._quantity = quantity
        self._direction = direction
        self._fill_price = fill_price
        self._commission = commission or 0.0
        self._order_ref = order_ref
        self._type = 'FILL'
    
    @property
    def timestamp(self) -> int:
        """Get the timestamp.
        
        Returns:
            int: Unix timestamp when the order was filled.
        """
        return self._timestamp
    
    @property
    def symbol(self) -> str:
        """Get the symbol.
        
        Returns:
            str: The financial instrument symbol.
        """
        return self._symbol
    
    @property
    def quantity(self) -> int:
        """Get the quantity.
        
        Returns:
            int: The number of units filled.
        """
        return self._quantity
    
    @property
    def direction(self) -> str:
        """Get the direction.
        
        Returns:
            str: The direction of the fill ('BUY' or 'SELL').
        """
        return self._direction
    
    @property
    def fill_price(self) -> float:
        """Get the fill price.
        
        Returns:
            float: The price at which the order was filled.
        """
        return self._fill_price
    
    @property
    def commission(self) -> float:
        """Get the commission.
        
        Returns:
            float: The commission charged for the transaction.
        """
        return self._commission
    
    @property
    def type(self) -> str:
        """Get the event type.
        
        Returns:
            str: The event type identifier, always 'FILL'.
        """
        return self._type
    
    @property
    def order_ref(self) -> int:
        """Get the related order reference id
        
        Returns:
            int: The related order reference id
        """
        return self._order_ref
    
    def __str__(self):
        """String representation of the fill event.
        
        Returns:
            str: A string containing all fill event details.
        """
        return (f"ID: {self._id},"
                f"Datetime: {datetime.fromtimestamp(self._bar.timestamp).strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Symbol: {self._symbol}, "
                f"Quantity: {self._quantity}, "
                f"Direction: {self._direction}, "
                f"Fill price: {self._fill_price}, "
                f"Commission: {self._commission}, "
                f"Event type: {self._type}")