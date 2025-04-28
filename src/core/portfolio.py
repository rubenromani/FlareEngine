from src.logging.logger_provider import get_logger
from src.core.dispatcher import Dispatcher
from src.core.shared_repository import SharedRepository
from src.core.event import OrderEvent, FillEvent, BarEvent

logger = get_logger(__name__, "DEBUG")

class Portfolio:
    """Portfolio management class for trading system.
    
    This class manages the trading portfolio, tracking balance, positions,
    equity, and processing orders and fills. It handles margin requirements
    for short positions and maintains records of all transactions.
    
    Attributes:
        _balance (float): Current cash balance.
        _available_balance (float): Balance available for new orders.
        _equity (float): Total portfolio value (balance + positions).
        _last_prices (dict): Dictionary of latest prices for symbols.
        _positions (dict): Dictionary of current positions by symbol.
        _pending_orders (list): List of pending orders.
        _transaction (list): List of transaction records.
    """

    def __init__(self):
        self._balance = 100000.0 # Hardcoded in this moment
        self._available_balance = self._balance # balance - balance frozen for pending orders
        self._equity = self._balance # balance + position_value
        self._last_prices = {}
        self._positions = {}
        self._pending_orders = []
        self._transaction = []
        self._dispatcher = Dispatcher()
        self._repo = SharedRepository()

        self._data_streams_subscription()
        self._dispatcher.subscribe("new_data_stream", self._on_new_data_stream)
        self._dispatcher.subscribe("order_manager_order", self._on_order_manager_order)
        self._dispatcher.subscribe("broker_interface_fill", self._on_broker_interface_fill)

        self._repo.set("available_balance", self._available_balance);
    
    def _data_streams_subscription(self):
        """Subscribe to existing data streams.
        
        Retrieves all registered data streams from the shared repository
        and subscribes to their events to receive price updates.
        """
        data_streams = self._repo.get("data_streams", default=[])
        for data_stream in data_streams:
            self._dispatcher.subscribe(data_stream, self._on_new_bar)

    def _on_new_data_stream(self, sender, new_data_stream: str):
        """Handle new data stream registration.
        
        Args:
            sender: The object that published the event.
            new_data_stream (str): The identifier for the new data stream.
        """
        self._dispatcher.subscribe(new_data_stream, self._on_new_bar)

    def _on_new_bar(self, sender, bar: BarEvent):
        """Process new price bar event.
        
        Updates portfolio equity based on new prices and checks
        margin requirements for short positions.
        
        Args:
            sender: The object that published the event.
            bar (BarEvent): The bar event containing new price data.
        """
        self._check_margin_requirements()
        self._update_equity()

    def _on_order_manager_order(self, seder, order_event: OrderEvent):
        """Handle new order event from order manager.
        
        Records the new order in pending orders and updates
        the available balance to reserve funds.
        
        Args:
            seder: The object that published the event.
            order_event (OrderEvent): The order event to process.
        """
        self._pending_orders.append(order_event)
        self._update_available_balance()

    def _on_broker_interface_fill(self, sender, fill_event: FillEvent):
        """Process fill event from broker.
        
        Removes the filled order from pending orders, updates positions,
        balance, available balance, and equity based on the fill.
        
        Args:
            sender: The object that published the event.
            fill_event (FillEvent): The fill event to process.
        """
        self._pending_orders = [x for x in self._pending_orders if x.id != fill_event.order_ref]
        # self._transaction -> update
        self._update_positions(fill_event)
        self._update_balance(fill_event)
        self._update_available_balance()
        self._update_equity()
        
    
    def _update_equity(self):
        """Update portfolio equity value.
        
        Calculates the total portfolio value by adding the current value
        of all positions to the cash balance.
        """
        self._equity = self._balance

        for symbol, quantity in self._positions.items():
            if symbol in self._last_prices:
                current_price = self._last_prices[symbol].close
                position_value = quantity * current_price  
                self._equity += position_value

    def _update_balance(self, fill_event: FillEvent):
        """Update cash balance based on a fill event.
        
        Adds or subtracts cash based on the direction of the order,
        accounting for the transaction value and commission.
        
        Args:
            fill_event (FillEvent): The fill event that triggered the balance update.
            
        Raises:
            AssertionError: If balance becomes negative after the update.
        """
        transaction_value = fill_event.quantity * fill_event.fill_price

        if fill_event.direction == "BUY":
            self._balance -= transaction_value
        else:  # "SELL"
            self._balance += transaction_value

        self._balance -= fill_event.commission

        if self._balance < 0:
            logger.critical("Balance cannot be negative")
            assert(self._balance >= 0), "Balance cannot be negative"

    def _update_available_balance(self):
        """Update available balance for new orders.
        
        Calculates the balance available for new orders by subtracting
        the value of all pending orders from the total balance.
        Updates the shared repository with the new value.
        """
        self._available_balance = self._balance
    
        for order in self._pending_orders:
            if order.order_type == "MARKET":
                if order.symbol in self._last_prices:
                    price = self._last_prices[order.symbol].close
                else:
                    logger.warning(f"No price data available for {order.symbol}")
                    continue
            else:
                price = order.price

            reserved_value = order.quantity * price
            self._available_balance -= reserved_value

        self._repo.set("available_balance", self._available_balance)

    def _update_positions(self, fill_event: FillEvent):
        """Update portfolio positions based on a fill event.
        
        Increases or decreases position size based on the fill direction.
        Creates new position entries if needed.
        
        Args:
            fill_event (FillEvent): The fill event that triggered the position update.
        """
        if fill_event.direction == "BUY":
            if fill_event.symbol in self._positions:
                self._positions[fill_event.symbol] += fill_event.quantity
            else: 
                self._positions[fill_event.symbol] = fill_event.quantity
        else:
            if fill_event.symbol in self._positions:
                self._positions[fill_event.symbol] -= fill_event.quantity
            else:
                self._positions[fill_event.symbol] = -fill_event.quantity

    def _check_margin_requirements(self):
        """Check if margin requirements are met for short positions.
        
        Verifies that the portfolio has sufficient equity to maintain
        all short positions according to the margin requirements.
        Logs critical warnings if margin calls are triggered.
        
        Returns:
            bool: True if a margin call was triggered, False otherwise.
        """
        margin_call = False

        for symbol, quantity in self._positions.items():
            if quantity < 0:  # Posizione short
                current_price = self._last_prices[symbol].close
                position_value = abs(quantity) * current_price

                # margin requirements (100% for now)
                maintenance_margin = position_value * 1

                if self._equity < maintenance_margin:
                    margin_call = True
                    logger.critical(f"Margin call on {symbol}: equity {self._equity} below maintenance margin {maintenance_margin}")
                    # margin call logic

        return margin_call