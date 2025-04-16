from src.core.event import BarEvent, OrderEvent, FillEvent

def dispatch(obj, event):
    if isinstance(event, OrderEvent):
        # Handle order event
        print(f"Handling order event: {event.symbol}, {event.order_type}, {event.quantity}, {event.direction}")