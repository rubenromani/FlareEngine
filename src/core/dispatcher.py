"""Event dispatching system based on the Publisher-Subscriber pattern.

This module implements a thread-safe singleton Dispatcher that allows components
to communicate through events without direct coupling. It uses a queue-based
approach to process events asynchronously.

The Dispatcher follows the Singleton pattern to ensure a single event bus
exists throughout the application.

Available events:
    - new_data_stream : string
    - new_bar_symbol_timeframe : BarEvent
    - strategy_order : OrderEvent
    - risk_manager_orer : OrderEvent
    - order_manager_order : OrderEvent
    - broker_interface_fill : FillOrder
"""

import queue
import threading
from src.logging.logger_provider import get_logger

logger = get_logger(__name__, "DEBUG")

class Dispatcher:
    """Singleton event dispatcher that manages event publishing and subscription.
    
    This class implements the Publisher-Subscriber pattern, allowing components
    to communicate without direct coupling. It processes events asynchronously
    in a separate worker thread.
    
    Attributes:
        message_queue (queue.Queue): Queue for storing events to be processed.
        subscribers (dict): Dictionary mapping event types to callback functions.
        subscribers_lock (threading.Lock): Lock for thread-safe access to subscribers.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Ensure only one instance of Dispatcher exists (Singleton pattern).
        
        Returns:
            Dispatcher: The singleton instance of the Dispatcher.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Dispatcher, cls).__new__(cls)
                cls._instance.subscribers = {}
                cls._instance.subscribers_lock = threading.Lock()
                cls._instance.message_queue = queue.Queue()
                cls._instance.worker_thread = None
                cls._instance.running = False
        return cls._instance
    
    def __init__(self):
        """Initialize the message queue and start the worker thread."""        
        if not hasattr(self, '_running') or not self._running:
            self.message_queue = queue.Queue()
            self._running = True
            self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()
    
    def subscribe(self, event_type, callback):
        """Subscribe to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to.
            callback: Function to be called when the event occurs.
                      The callback should accept (sender, data) parameters.
        """
        logger.debug(f"Subscription: {event_type} event, subscriber {callback.__name__}")
        with self.subscribers_lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(callback)

    def publish(self, event_type, sender, data=None):
        """Publish an event to all subscribers.
        
        Args:
            event_type: The type of event being published.
            sender: The object that is publishing the event.
            data (optional): Additional data to be passed to subscribers.
        """
        logger.debug(f"Published: {event_type} event, sender {sender.__class__.__name__}, data {data}")
        self.message_queue.put((event_type, sender, data))

    def _process_queue(self):
        """Process events from the queue in a separate thread.
        
        This method runs in a separate daemon thread and processes
        events as they arrive in the queue. It invokes all subscribed
        callbacks for each event.
        """
        while True:
            event_type, sender, data = self.message_queue.get()
            
            try:
                if event_type in self.subscribers:
                    callbacks = self.subscribers[event_type].copy()
                else:
                    continue

                for callback in callbacks:
                    try:
                        callback(sender, data)
                    except Exception as e:
                        logger.error(f"Error in callback: {e}: callback: {callback}, sender: {sender}, data:{data}")
            finally:
                self.message_queue.task_done()