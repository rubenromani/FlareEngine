from src.core.event import BarEvent, OrderEvent, FillEvent

def dispatch(obj, event):
    print(f"Dispatching event: {event.type} for object: {obj.__class__.__name__}")
    if isinstance(event, OrderEvent):
        # Handle order event
        print(f"Handling order event: {event.symbol}, {event.order_type}, {event.quantity}, {event.direction}")