from src.logging.logger_provider import get_logger
from src.core.dispatcher import Dispatcher
from src.core.shared_repository import SharedRepository

logger = get_logger(__name__, "DEBUG")

class Portfolio:

    def __init__(self):
        self._balance = 100000.0 # Hardcoded in this moment
        self._available_balance = self._balance # balance - balance frozen for pending orders
        self._equity = self._balance
        self._last_prices = {}
        self._positions = {}
        self._pending_orders = {}
        self._transaction = []
        self._dispatcher = Dispatcher()
        self._repo = SharedRepository()

        self._data_streams_subscription()
        self._dispatcher.subscribe("new_data_stream", self._on_new_data_stream) 
        self._repo.set("available_balance", self._available_balance);
    
    def _data_streams_subscription(self):
        data_streams = self._repo.get("data_streams")
        for data_stream in data_streams:
            self._dispatcher.subscribe(data_stream, self._on_new_bar)

    def _on_new_data_stream(self, sender, new_data_stream):
        self._dispatcher.subscribe(new_data_stream, self._on_new_bar)

    def _on_new_bar(self, sender, bar):
        pass

    def _on_new_order_manager_order(self, seder, order_event):
        pass

    def _update_equity(self):
        pass

    def _update_available_balance(self, order_event):
        pass

        
