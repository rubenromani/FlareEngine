from src.logging.logger_provider import get_logger
from src.core.dispatcher import Dispatcher
from src.core.shared_repository import SharedRepository

logger = get_logger(__name__, "DEBUG")

class Portfolio:

    def __init__(self):
        self.balance = 100000.0 # Hardcoded in this moment
        self.available_balance = self.balance # balance - balance frozen for pending orders
        self.equity = self.balance
        self.last_prices = {}
        self.positions = {}
        self.transaction = []

        self.dispatcher = Dispatcher()
        self.repo = SharedRepository()
        
        self.repo.set("available_balance", self.available_balance);


        