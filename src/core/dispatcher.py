from src.core.event import BarEvent, OrderEvent, FillEvent
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    filename='app.log'
)

def dispatch(obj, event):
    if isinstance(event, OrderEvent):
        # Handle order event
        print(f"Handling order event: {event.symbol}, {event.order_type}, {event.quantity}, {event.direction}")


class Dispatcher:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Dispatcher, cls).__new__(cls)
            cls._instance.subscribers = {}
        return cls._instance
    
    def subscribe(self, event_type, callback):
     
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, sender, data=None):
        logging.info(f"Published: {event_type} event, sender {sender.__class__.__name__}, data {data}")
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(sender, data)