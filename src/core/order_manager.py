from src.core.dispatcher import Dispatcher
from src.core.shared_repository import SharedRepository
from src.core.event import OrderEvent, FillEvent

class OrderManager:

    def __init__(self):
        self._dispatcher = Dispatcher()
        self._repo = SharedRepository()
        self._dispatcher.subscribe(f"risk_manager_order", self._on_risk_manager_order)

    def _on_risk_manager_order(self, order_event: OrderEvent):
        self._emit_order(order_event)
    
    def _emit_order(self, order_event: OrderEvent):
        self._dispatcher.publish(f"order_manager_order", self, order_event)


import time

class BrokerInterfaceMock:

    def __init__(self):
        self._dispatcher = Dispatcher()
        self._repo = SharedRepository()
        self._dispatcher.subscribe(f"order_manager_order", self._on_order_manager_order)

    def _on_order_manager_order(self, order_event: OrderEvent):
        self._fill(order_event)

    def _fill(self, order_event: OrderEvent):
        fill_event = FillEvent(
            timestamp=time.time(),
            symbol=order_event.symbol,
            quantity=order_event.quantity,
            direction=order_event.direction,
            fill_price=order_event.price if order_event.type == 'MARKET' else self._repo.get("last_prices")["XXX"].close,
            commission=0.0
        )
        self._dispatcher.publish(f"broker_interface_fill", self, fill_event)
