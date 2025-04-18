from src.logging.logger_provider import get_logger

logger = get_logger(__name__, "DEBUG")

class Portfolio:

    def __init__(self):
        self.balance = 100000 # Hardcoded in this moment
        self.equity = self.balance
        self.last_prices = {}
        self.positions = {}
        self.transaction = []
        


        