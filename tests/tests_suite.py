import unittest
import os
import numpy as np
import pandas as pd
from datetime import datetime
import time
import threading
import queue
import logging

from src.core.types import Bar, Transaction, Timeframe
from src.core.data_manager import DataManager, BacktestDataStream
from src.core.event import BarEvent, OrderEvent, FillEvent, Event
from src.core.dispatcher import Dispatcher
from src.core.shared_repository import SharedRepository
from src.core.portfolio import Portfolio
from src.core.risk_manager import RiskManager
from src.core.order_manager import OrderManager, BrokerInterfaceMock
from src.strategy.base_strategy import Strategy
from src.strategy.examples.moving_average_strategy import MovingAverageStrategy
from src.data.synthetic_data_generator import generate_financial_data
from src.logging.logger_provider import get_logger

script_dir = os.path.dirname(os.path.abspath(__file__))
spy_data_1d_path = os.path.join(script_dir, "..", "data", "spy.csv")
synth_data_1h_path = os.path.join(script_dir, "..", "data", "synth_data_1h.csv")

class TestBar(unittest.TestCase):
    """Tests for the Bar Class"""

    def test_bar_initialization(self):
        """Test correct initialization of a Bar object"""
        timestamp = int(time.time())
        open_price = 100.0
        high_price = 105.0
        low_price = 98.0
        close_price = 102.0
        volume = 1000.0
        
        bar = Bar(timestamp, open_price, high_price, low_price, close_price, volume)
        
        self.assertEqual(bar.timestamp, timestamp)
        self.assertEqual(bar.open, open_price)
        self.assertEqual(bar.high, high_price)
        self.assertEqual(bar.low, low_price)
        self.assertEqual(bar.close, close_price)
        self.assertEqual(bar.volume, volume)
        self.assertEqual(bar.additional_data, {})
        
    def test_bar_with_additional_data(self):
        """Test correct handling of additional data"""
        timestamp = int(time.time())
        open_price = 100.0
        high_price = 105.0
        low_price = 98.0
        close_price = 102.0
        volume = 1000.0
        additional_data = {"ema20": 101.5, "rsi": 65.0}
        
        bar = Bar(timestamp, open_price, high_price, low_price, close_price, volume, additional_data)
        
        self.assertEqual(bar.additional_data, additional_data)

class TestTimeframe(unittest.TestCase):
    """Tests for the Timeframe enum"""
    
    def test_timeframe_conversion(self):
        """Test correct conversion from string to Timeframe and vice versa"""
        self.assertEqual(str(Timeframe.MINUTE_1), "1m")
        self.assertEqual(str(Timeframe.HOUR_1), "1h")
        self.assertEqual(str(Timeframe.DAY_1), "1d")
        
        self.assertEqual(Timeframe.from_string("1m"), Timeframe.MINUTE_1)
        self.assertEqual(Timeframe.from_string("1h"), Timeframe.HOUR_1)
        self.assertEqual(Timeframe.from_string("1d"), Timeframe.DAY_1)
        
        with self.assertRaises(ValueError):
            Timeframe.from_string("invalid")
            
    def test_timeframe_to_minutes(self):
        """Test correct conversion from Timeframe to minutes"""
        self.assertEqual(Timeframe.MINUTE_1.to_minutes(), 1)
        self.assertEqual(Timeframe.MINUTE_5.to_minutes(), 5)
        self.assertEqual(Timeframe.MINUTE_15.to_minutes(), 15)
        self.assertEqual(Timeframe.MINUTE_30.to_minutes(), 30)
        self.assertEqual(Timeframe.HOUR_1.to_minutes(), 60)
        self.assertEqual(Timeframe.HOUR_4.to_minutes(), 240)
        self.assertEqual(Timeframe.DAY_1.to_minutes(), 1440)


class TestEvent(unittest.TestCase):
    """Tests for event classes"""
    
    def test_bar_event(self):
        """Test correct initialization and properties of BarEvent"""
        timestamp = int(time.time())
        bar = Bar(timestamp, 100.0, 105.0, 98.0, 102.0, 1000.0)
        symbol = "AAPL"
        
        bar_event = BarEvent(bar, symbol)
        
        self.assertEqual(bar_event.bar, bar)
        self.assertEqual(bar_event.symbol, symbol)
        self.assertEqual(bar_event.type, "BAR")
        self.assertIn(symbol, str(bar_event))
        self.assertIn(str(bar.close), str(bar_event))
        
    def test_order_event(self):
        """Test correct initialization and properties of OrderEvent"""
        symbol = "AAPL"
        order_type = "MARKET"
        quantity = 10
        direction = "BUY"
        price = 150.0
        
        order_event = OrderEvent(symbol, order_type, quantity, direction, price)
        
        self.assertEqual(order_event.symbol, symbol)
        self.assertEqual(order_event.order_type, order_type)
        self.assertEqual(order_event.quantity, quantity)
        self.assertEqual(order_event.direction, direction)
        self.assertEqual(order_event.price, price)
        self.assertEqual(order_event.type, "ORDER")
        self.assertIn(symbol, str(order_event))
        self.assertIn(direction, str(order_event))
        
    def test_fill_event(self):
        """Test correct initialization and properties of FillEvent"""
        timestamp = int(time.time())
        symbol = "AAPL"
        quantity = 10
        direction = "BUY"
        fill_price = 150.0
        commission = 1.5
        order_ref = 123  # Aggiunto order_ref
        
        fill_event = FillEvent(timestamp, symbol, quantity, direction, fill_price, commission, order_ref)
        
        self.assertEqual(fill_event.timestamp, timestamp)
        self.assertEqual(fill_event.symbol, symbol)
        self.assertEqual(fill_event.quantity, quantity)
        self.assertEqual(fill_event.direction, direction)
        self.assertEqual(fill_event.fill_price, fill_price)
        self.assertEqual(fill_event.commission, commission)
        self.assertEqual(fill_event.order_ref, order_ref)  # Test del nuovo attributo
        self.assertEqual(fill_event.type, "FILL")
        self.assertIn(symbol, str(fill_event))
        self.assertIn(direction, str(fill_event))

class TestDispatcher(unittest.TestCase):
    """Tests for the Dispatcher class"""
    
    def setUp(self):
        """Initialize for Dispatcher tests"""
        # Reset singleton instance for isolated tests
        Dispatcher._instance = None
        self.dispatcher = Dispatcher()
        self.test_data = None
        
    def test_singleton_pattern(self):
        """Test that Dispatcher follows the Singleton pattern"""
        dispatcher1 = Dispatcher()
        dispatcher2 = Dispatcher()
        self.assertIs(dispatcher1, dispatcher2)
        
    def callback_function(self, sender, data):
        """Callback function for tests"""
        self.test_data = data
        
    def test_subscribe_and_publish(self):
        """Test subscription and publication of events"""
        event_type = "test_event"
        test_sender = "test_sender"
        test_data = "test_data"
        
        # Subscribe to the event
        self.dispatcher.subscribe(event_type, self.callback_function)
        
        # Publish the event
        self.dispatcher.publish(event_type, test_sender, test_data)
        
        # Since the dispatcher worker thread is blocking, we need to manually process the event
        # Manually get the event from the queue and process it
        event_type_received, sender_received, data_received = self.dispatcher.message_queue.get()
        
        # Call the subscriber directly
        callbacks = []
        with self.dispatcher.subscribers_lock:
            if event_type_received in self.dispatcher.subscribers:
                callbacks = self.dispatcher.subscribers[event_type_received].copy()
                
        for callback in callbacks:
            callback(sender_received, data_received)
            
        # Mark the task as done
        self.dispatcher.message_queue.task_done()
        
        # Verify the callback was called with the correct data
        self.assertEqual(self.test_data, test_data)

class TestSharedRepository(unittest.TestCase):
    """Tests for the SharedRepository class"""
    
    def setUp(self):
        """Initialize for SharedRepository tests"""
        # Reset singleton instance for isolated tests
        SharedRepository._instance = None
        self.repo = SharedRepository()
        
    def test_singleton_pattern(self):
        """Test that SharedRepository follows the Singleton pattern"""
        repo1 = SharedRepository()
        repo2 = SharedRepository()
        self.assertIs(repo1, repo2)
        
    def test_set_and_get(self):
        """Test correct functioning of set and get"""
        self.repo.set("test_key", "test_value")
        self.assertEqual(self.repo.get("test_key"), "test_value")
        
    def test_get_with_default(self):
        """Test correct functioning of get with default value"""
        self.assertEqual(self.repo.get("non_existent_key", "default_value"), "default_value")
        
    def test_delete(self):
        """Test correct functioning of delete"""
        self.repo.set("test_key", "test_value")
        self.repo.delete("test_key")
        self.assertIsNone(self.repo.get("test_key"))
        
    def test_contains(self):
        """Test correct functioning of contains"""
        self.repo.set("test_key", "test_value")
        self.assertTrue(self.repo.contains("test_key"))
        self.assertFalse(self.repo.contains("non_existent_key"))

class TestBacktestDataStream(unittest.TestCase):
    """Tests for the BacktestDataStream class"""
    
    def setUp(self):
        """Initialize for BacktestDataStream tests"""
        # Use the generated test data file
        self.data_file = synth_data_1h_path
        self.symbol = "XXX"
        self.timeframe = Timeframe.HOUR_1
        self.data_stream = BacktestDataStream(self.symbol, self.timeframe, self.data_file)
        
    def test_initialization(self):
        """Test correct initialization of BacktestDataStream"""
        self.assertEqual(self.data_stream.symbol, self.symbol)
        self.assertEqual(self.data_stream.timeframe, self.timeframe)
        self.assertEqual(self.data_stream.type, "backtest")
        self.assertIsNotNone(self.data_stream.raw_data)
        self.assertIsNotNone(self.data_stream.optimized_data)
        self.assertIsNotNone(self.data_stream._bars)
        
    def test_data_loading(self):
        """Test correct loading of data from CSV file"""
        # Verify that data was loaded correctly
        self.assertGreater(len(self.data_stream.raw_data), 0)
        self.assertEqual(len(self.data_stream.raw_data), len(self.data_stream.optimized_data))
        self.assertEqual(len(self.data_stream.raw_data), len(self.data_stream._bars))
        
    def test_get_next_bar(self):
        """Test correct functioning of get_next_bar"""
        # Get the first bar
        first_bar = self.data_stream.get_next_bar()
        self.assertIsNotNone(first_bar)
        self.assertIsInstance(first_bar, Bar)
        
        # Verify that the second bar is different from the first
        second_bar = self.data_stream.get_next_bar()
        self.assertIsNotNone(second_bar)
        self.assertNotEqual(first_bar.timestamp, second_bar.timestamp)
        
        # Verify that all bars are returned
        for _ in range(len(self.data_stream._bars) - 2):
            bar = self.data_stream.get_next_bar()
            self.assertIsNotNone(bar)
            
        # Verify that after all bars, None is returned
        last_bar = self.data_stream.get_next_bar()
        if last_bar is not None:  # there might be one last bar
            self.assertIsNone(self.data_stream.get_next_bar())

class TestDataManager(unittest.TestCase):
    """Tests for the DataManager class"""
    
    def setUp(self):
        """Initialize for DataManager tests"""
        # Reset singleton instances for isolated tests
        SharedRepository._instance = None
        Dispatcher._instance = None
        
        # Use the generated test data file
        self.data_file = synth_data_1h_path
        self.symbol = "XXX"
        self.timeframe = Timeframe.HOUR_1
        self.data_stream = BacktestDataStream(self.symbol, self.timeframe, self.data_file)
        self.data_manager = DataManager([self.data_stream])
        
        # Repository and Dispatcher for tests
        self.repo = SharedRepository()
        self.dispatcher = Dispatcher()
        self.published_bars = []
        
        # Subscribe to new bar events
        self.event_key = f"new_bar_{self.symbol}_{self.timeframe}"
        self.dispatcher.subscribe(self.event_key, self.on_new_bar)
        
    def on_new_bar(self, sender, bar_event):
        """Callback for new bar events"""
        self.published_bars.append(bar_event.bar)
        
    def process_event(self):
        """Process a single event from the Dispatcher queue"""
        try:
            event_type, sender, data = self.dispatcher.message_queue.get_nowait()
            with self.dispatcher.subscribers_lock:
                if event_type in self.dispatcher.subscribers:
                    callbacks = self.dispatcher.subscribers[event_type].copy()
                    for callback in callbacks:
                        callback(sender, data)
            self.dispatcher.message_queue.task_done()
            return True
        except queue.Empty:
            return False
            
    def process_all_events(self):
        """Process all events in the Dispatcher queue"""
        while self.process_event():
            pass
        
    def test_get_next_bars(self):
        """Test correct functioning of get_next_bars"""
        # Call get_next_bars multiple times and verify that bars are published
        count = 0
        max_bars = 10  # Limit the number of bars to speed up the test
        
        while self.data_manager.get_next_bars() and count < max_bars:
            count += 1
            # Process all pending events after each bar
            self.process_all_events()
            
        # Verify that bars were published
        self.assertEqual(len(self.published_bars), count)
        
        # Verify that last_prices was updated in the repo
        last_prices = self.repo.get("last_prices")
        self.assertIsNotNone(last_prices)
        self.assertIn(self.symbol, last_prices)

class TestRiskManager(unittest.TestCase):
    """Tests for the RiskManager class"""
    
    def setUp(self):
        """Initialize for RiskManager tests"""
        # Reset singleton instances for isolated tests
        SharedRepository._instance = None
        Dispatcher._instance = None
        
        self.risk_manager = RiskManager()
        self.dispatcher = Dispatcher()
        
        # For capturing orders emitted by the risk manager
        self.received_orders = []
        self.dispatcher.subscribe("risk_manager_order", self.on_risk_manager_order)
        
    def on_risk_manager_order(self, sender, order_event):
        """Callback for risk manager order events"""
        self.received_orders.append(order_event)
        
    def test_order_processing(self):
        """Test that the risk manager processes orders correctly"""
        # Create a test order
        test_order = OrderEvent("TEST", "MARKET", 1, "BUY", 100.0)
        
        # Publish the order as if it came from a strategy
        self.dispatcher.publish("strategy_order", self, test_order)

        time.sleep(0.1)
        
        # Debug information
        print(f"Dispatcher subscribers: {self.dispatcher.subscribers}")
        print(f"Received orders: {len(self.received_orders)}")
        
        # Verify that the risk manager emitted the order
        self.assertEqual(len(self.received_orders), 1)
        
        if len(self.received_orders) > 0:
            received_order = self.received_orders[0]
            
            # Verify that the order details were preserved
            self.assertEqual(received_order.symbol, test_order.symbol)
            self.assertEqual(received_order.order_type, test_order.order_type)
            self.assertEqual(received_order.quantity, test_order.quantity)
            self.assertEqual(received_order.direction, test_order.direction)
            self.assertEqual(received_order.price, test_order.price)

class TestOrderManager(unittest.TestCase):
    """Tests for the OrderManager class"""
    
    def setUp(self):
        """Initialize for OrderManager tests"""
        # Reset singleton instances for isolated tests
        SharedRepository._instance = None
        Dispatcher._instance = None
        
        self.order_manager = OrderManager()
        self.dispatcher = Dispatcher()
        
        # For capturing orders emitted by the order manager
        self.received_orders = []
        self.dispatcher.subscribe("order_manager_order", self.on_order_manager_order)
        
    def on_order_manager_order(self, sender, order_event):
        """Callback for order manager order events"""
        self.received_orders.append(order_event)
        
    def test_order_processing(self):
        """Test that the order manager processes orders correctly"""
        # Create a test order
        test_order = OrderEvent("TEST", "MARKET", 1, "BUY", 100.0)
        
        # Publish the order as if it came from the risk manager
        self.dispatcher.publish("risk_manager_order", self, test_order)
        
        time.sleep(0.1)
        
        # Verify that the order manager emitted the order
        self.assertEqual(len(self.received_orders), 1)
        
        if len(self.received_orders) > 0:
            received_order = self.received_orders[0]
            
            # Verify that the order details were preserved
            self.assertEqual(received_order.symbol, test_order.symbol)
            self.assertEqual(received_order.order_type, test_order.order_type)
            self.assertEqual(received_order.quantity, test_order.quantity)
            self.assertEqual(received_order.direction, test_order.direction)
            self.assertEqual(received_order.price, test_order.price)

class TestBrokerInterfaceMock(unittest.TestCase):
    """Tests for the BrokerInterfaceMock class"""
    
    def setUp(self):
        """Initialize for BrokerInterfaceMock tests"""
        # Reset singleton instances for isolated tests
        SharedRepository._instance = None
        Dispatcher._instance = None
        
        self.broker_interface = BrokerInterfaceMock()
        self.dispatcher = Dispatcher()
        
        # Configure last_prices in the repo
        self.repo = SharedRepository()
        timestamp = int(time.time())
        test_bar = Bar(timestamp, 100.0, 105.0, 98.0, 102.0, 1000.0)
        self.repo.set("last_prices", {"XXX": test_bar})
        
        # For capturing fills emitted by the broker
        self.received_fills = []
        self.dispatcher.subscribe("broker_interface_fill", self.on_broker_fill)
        
    def on_broker_fill(self, sender, fill_event):
        """Callback for broker fill events"""
        self.received_fills.append(fill_event)
        
    def test_order_filling(self):
        """Test that the broker mock executes orders correctly"""
        # Create a test order
        test_order = OrderEvent("XXX", "LIMIT", 1, "BUY", 100.0)
        
        # Publish the order as if it came from the order manager
        self.dispatcher.publish("order_manager_order", self, test_order)
        
        time.sleep(0.2)
        
        # Verify that the broker emitted a fill
        self.assertEqual(len(self.received_fills), 1)
        
        if len(self.received_fills) > 0:
            received_fill = self.received_fills[0]
            
            # Verify that the fill details are correct
            self.assertEqual(received_fill.symbol, test_order.symbol)
            self.assertEqual(received_fill.quantity, test_order.quantity)
            self.assertEqual(received_fill.direction, test_order.direction)
            self.assertEqual(received_fill.order_ref, test_order.id)  # Verifica order_ref
            
            # For a LIMIT order, the fill_price should equal the order's price
            self.assertEqual(received_fill.fill_price, test_order.price)

class TestPortfolio(unittest.TestCase):
    """Tests for the Portfolio class"""
    
    def setUp(self):
        """Initialize for Portfolio tests"""
        # Reset singleton instances for isolated tests
        SharedRepository._instance = None
        Dispatcher._instance = None
        
        self.portfolio = Portfolio()
        self.repo = SharedRepository()
        self.dispatcher = Dispatcher()
        
        # Creare dati di mercato simulati
        timestamp = int(time.time())
        self.test_bar_aapl = Bar(timestamp, 150.0, 155.0, 148.0, 152.0, 1000.0)
        self.test_bar_msft = Bar(timestamp, 250.0, 255.0, 248.0, 252.0, 1000.0)
        
        # Aggiungere i prezzi di mercato al portfolio
        self.portfolio._last_prices = {
            "AAPL": self.test_bar_aapl,
            "MSFT": self.test_bar_msft
        }
        
    def test_initialization(self):
        """Test correct initialization of the Portfolio"""
        # Verify that the portfolio correctly initializes the balance
        self.assertEqual(self.portfolio._balance, 100000.0)
        self.assertEqual(self.portfolio._available_balance, 100000.0)
        self.assertEqual(self.portfolio._equity, 100000.0)
        
        # Verify that the available balance was saved in the repository
        self.assertEqual(self.repo.get("available_balance"), 100000.0)
    
    def test_update_balance_buy(self):
        """Test balance update with a BUY order fill"""
        # Simulate a BUY fill
        fill_event = FillEvent(
            timestamp=int(time.time()),
            symbol="AAPL",
            quantity=10,
            direction="BUY",
            fill_price=150.0,
            commission=5.0,
            order_ref=1
        )
        
        initial_balance = self.portfolio._balance
        self.portfolio._update_balance(fill_event)
        
        expected_balance = initial_balance - (10 * 150.0) - 5.0
        self.assertEqual(self.portfolio._balance, expected_balance)
    
    def test_update_balance_sell(self):
        """Test balance update with a SELL order fill"""
        # Simulate a SELL fill
        fill_event = FillEvent(
            timestamp=int(time.time()),
            symbol="AAPL",
            quantity=10,
            direction="SELL",
            fill_price=150.0,
            commission=5.0,
            order_ref=1
        )
        
        initial_balance = self.portfolio._balance
        self.portfolio._update_balance(fill_event)
        
        expected_balance = initial_balance + (10 * 150.0) - 5.0
        self.assertEqual(self.portfolio._balance, expected_balance)
    
    def test_update_positions(self):
        """Test position update with BUY and SELL fills"""
        # Simulate a BUY fill
        buy_fill = FillEvent(
            timestamp=int(time.time()),
            symbol="AAPL",
            quantity=10,
            direction="BUY",
            fill_price=150.0,
            commission=5.0,
            order_ref=1
        )
        
        self.portfolio._update_positions(buy_fill)
        self.assertEqual(self.portfolio._positions.get("AAPL"), 10)
        
        # Simulate a partial SELL fill
        sell_fill = FillEvent(
            timestamp=int(time.time()),
            symbol="AAPL",
            quantity=5,
            direction="SELL",
            fill_price=155.0,
            commission=5.0,
            order_ref=2
        )
        
        self.portfolio._update_positions(sell_fill)
        self.assertEqual(self.portfolio._positions.get("AAPL"), 5)
        
        # Simulate a SELL that creates a short position
        sell_fill = FillEvent(
            timestamp=int(time.time()),
            symbol="MSFT",
            quantity=10,
            direction="SELL",
            fill_price=250.0,
            commission=5.0,
            order_ref=3
        )
        
        self.portfolio._update_positions(sell_fill)
        self.assertEqual(self.portfolio._positions.get("MSFT"), -10)
    
    def test_update_equity(self):
        """Test equity calculation with long and short positions"""
        # Add a long position
        self.portfolio._positions["AAPL"] = 10
        
        # Add a short position
        self.portfolio._positions["MSFT"] = -5
        
        # Calculate expected equity: 
        # balance + (AAPL quantity * price) + (MSFT quantity * price)
        expected_equity = 100000.0 + (10 * 152.0) + (-5 * 252.0)
        
        self.portfolio._update_equity()
        self.assertEqual(self.portfolio._equity, expected_equity)
    
    def test_update_available_balance(self):
        """Test available balance with pending orders"""
        # Add a pending order
        order = OrderEvent(
            symbol="AAPL",
            order_type="LIMIT",
            quantity=10,
            direction="BUY",
            price=150.0
        )
        
        # Set an arbitrary ID for the test
        order._id = 1
        
        self.portfolio._pending_orders.append(order)
        
        initial_available = self.portfolio._available_balance
        self.portfolio._update_available_balance()
        
        # Available balance should be reduced by the order value
        expected_available = initial_available - (10 * 150.0)
        self.assertEqual(self.portfolio._available_balance, expected_available)
        
        # Verify repository update
        self.assertEqual(self.repo.get("available_balance"), expected_available)
    
    def test_order_execution_flow(self):
        """Test the complete flow from order to fill"""
        # Create an order event
        order = OrderEvent(
            symbol="AAPL",
            order_type="MARKET",
            quantity=10,
            direction="BUY",
            price=None
        )
        
        # Set ID for testing
        order._id = 123
        
        # Simulate order manager publishing the order
        self.portfolio._on_order_manager_order(None, order)
        
        # Verify pending orders
        self.assertEqual(len(self.portfolio._pending_orders), 1)
        
        # Create a fill event with the correct order_ref
        fill = FillEvent(
            timestamp=int(time.time()),
            symbol="AAPL",
            quantity=10,
            direction="BUY",
            fill_price=152.0,
            commission=5.0,
            order_ref=123  # Collegamento all'ordine originale
        )
        
        # Initial values for comparison
        initial_balance = self.portfolio._balance
        
        # Simulate broker interface publishing the fill
        self.portfolio._on_broker_interface_fill(None, fill)
        
        # Verify results
        self.assertEqual(len(self.portfolio._pending_orders), 0)  # Order removed
        self.assertEqual(self.portfolio._positions.get("AAPL"), 10)  # Position updated
        
        # Balance reduced by order value + commission
        expected_balance = initial_balance - (10 * 152.0) - 5.0
        self.assertEqual(self.portfolio._balance, expected_balance)
        
        # Equity should be balance + positions
        expected_equity = expected_balance + (10 * 152.0)
        self.assertEqual(self.portfolio._equity, expected_equity)
    
    def test_check_margin_requirements(self):
        """Test margin call detection"""
        # Set up a large short position
        self.portfolio._positions["MSFT"] = -500
        
        # Update equity
        self.portfolio._update_equity()
        
        # Position value would be -500 * 252 = -126,000
        # This should trigger a margin call because equity < position value
        margin_call = self.portfolio._check_margin_requirements()
        
        # Should detect a margin call
        self.assertTrue(margin_call)
        
        # Test with a small short position that doesn't trigger margin call
        self.portfolio._positions.clear()
        self.portfolio._positions["MSFT"] = -5
        self.portfolio._update_equity()
        
        margin_call = self.portfolio._check_margin_requirements()
        self.assertFalse(margin_call)
    
    def test_new_bar_processing(self):
        """Test processing of new bar events"""
        # Create a bar event
        bar_event = BarEvent(self.test_bar_aapl, "AAPL")
        
        # Add a spy to check if methods are called
        original_update_equity = self.portfolio._update_equity
        original_check_margin = self.portfolio._check_margin_requirements
        
        call_counts = {"equity": 0, "margin": 0}
        
        def mock_update_equity():
            call_counts["equity"] += 1
            original_update_equity()
            
        def mock_check_margin():
            call_counts["margin"] += 1
            return original_check_margin()
        
        self.portfolio._update_equity = mock_update_equity
        self.portfolio._check_margin_requirements = mock_check_margin
        
        # Simulate new bar event
        self.portfolio._on_new_bar(None, bar_event)
        
        # Verify both methods were called
        self.assertEqual(call_counts["equity"], 1)
        self.assertEqual(call_counts["margin"], 1)


if __name__ == '__main__':
    unittest.main()