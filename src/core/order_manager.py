from src.core.dispatcher import Dispatcher
from src.core.shared_repository import SharedRepository
from src.core.event import OrderEvent, FillEvent
from src.logging.logger_provider import get_logger

logger = get_logger(__name__, "ERROR")

class OrderManager:

    def __init__(self):
        self._dispatcher = Dispatcher()
        self._repo = SharedRepository()
        self._dispatcher.subscribe("risk_manager_order", self._on_risk_manager_order)

    def _on_risk_manager_order(self, sender,  order_event: OrderEvent):
        self._emit_order(order_event)
    
    def _emit_order(self, order_event: OrderEvent):
        self._dispatcher.publish("order_manager_order", self, order_event)


import time

class BrokerInterfaceMock:

    def __init__(self):
        self._dispatcher = Dispatcher()
        self._repo = SharedRepository()
        self._dispatcher.subscribe("order_manager_order", self._on_order_manager_order)

    def _on_order_manager_order(self, sender, order_event: OrderEvent):
        self._fill(order_event)

    def _fill(self, order_event: OrderEvent):
        try:
            fill_event = FillEvent(
                timestamp=time.time(),
                symbol=order_event.symbol,
                quantity=order_event.quantity,
                direction=order_event.direction,
                fill_price=order_event.price if order_event.type != 'MARKET' else self._repo.get("last_prices")[order_event.symbol].close,
                commission=0.0,
                order_ref=order_event.id
            )
            self._dispatcher.publish("broker_interface_fill", self, fill_event)
        except Exception as e:
            logger.error(e)
