from src.core.dispatcher import Dispatcher
from src.core.shared_repository import SharedRepository
from src.core.event import OrderEvent

class RiskManager:

    def __init__(self):
        self.dispatcher = Dispatcher()
        self.repo = SharedRepository()

        self.dispatcher.subscribe(f"strategy_order", self._on_strategy_order)

    def _on_strategy_order(self, order_event: OrderEvent):
        self._emit_order(order_event)
        #raise NotImplementedError("_on_newstrategy_order method must be implemented in subclasses")
    
    def _emit_order(self, order_event: OrderEvent):
        self.dispatcher.publish(f"risk_manager_order", self, order_event)