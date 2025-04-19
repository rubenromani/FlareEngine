#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Synthetic Financial Data Generator

This script generates realistic synthetic financial market data with OHLCV 
(Open, High, Low, Close, Volume) values using a random walk approach.
"""

import argparse
import datetime
import random
import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Union


def parse_timeframe(timeframe: str) -> Tuple[int, str]:
    """
    Parse the timeframe string and convert it to minutes.
    
    Args:
        timeframe: String representing the timeframe (e.g., "1m", "1h", "1d")
        
    Returns:
        Tuple containing (minutes, unit)
    
    Raises:
        ValueError: If the timeframe format is invalid
    """
    valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    if timeframe not in valid_timeframes:
        raise ValueError(f"Invalid timeframe. Choose from: {', '.join(valid_timeframes)}")
    
    value = int(timeframe[:-1])
    unit = timeframe[-1]
    
    if unit == "m":
        return value, "minute"
    elif unit == "h":
        return value * 60, "hour"
    elif unit == "d":
        return value * 1440, "day"  # 1440 = 24 * 60 minutes in a day
    else:
        raise ValueError(f"Invalid unit in timeframe: {unit}")


def parse_date(date_str: str) -> datetime.datetime:
    """
    Parse date string in format YYYY-MM-DD HH:MM:SS.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If the date format is invalid
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date format should be 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")


def parse_market_hours(market_hours: str) -> Dict:
    """
    Parse market hours specification.
    
    Args:
        market_hours: String specification of market hours
            Format: "day1-day2 HH:MM-HH:MM" (e.g., "mon-fri 09:30-16:00")
            Special values: "24/7" for markets that are always open
            
    Returns:
        Dictionary with market hours configuration
        
    Raises:
        ValueError: If the market hours format is invalid
    """
    if market_hours.lower() == "24/7":
        return {
            "type": "continuous",
            "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
            "hours": None
        }
    
    try:
        days_part, hours_part = market_hours.split(" ")
        
        # Parse days
        day_map = {
            "mon": 0, "tue": 1, "wed": 2, "thu": 3, 
            "fri": 4, "sat": 5, "sun": 6
        }
        
        if "-" in days_part:
            start_day, end_day = days_part.lower().split("-")
            start_idx = day_map.get(start_day)
            end_idx = day_map.get(end_day)
            
            if start_idx is None or end_idx is None:
                raise ValueError(f"Invalid day specification: {days_part}")
                
            if end_idx < start_idx:
                days = list(day_map.keys())[start_idx:] + list(day_map.keys())[:end_idx+1]
            else:
                days = list(day_map.keys())[start_idx:end_idx+1]
        else:
            if days_part.lower() not in day_map:
                raise ValueError(f"Invalid day specification: {days_part}")
            days = [days_part.lower()]
        
        # Parse hours
        start_time, end_time = hours_part.split("-")
        start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.datetime.strptime(end_time, "%H:%M").time()
        
        # Handle overnight sessions
        overnight = end_time < start_time
        
        return {
            "type": "session",
            "days": days,
            "start_time": start_time,
            "end_time": end_time,
            "overnight": overnight
        }
        
    except Exception as e:
        raise ValueError(f"Invalid market hours format. Example: 'mon-fri 09:30-16:00' or '24/7'. Error: {str(e)}")


def generate_timestamps(
    start_date: datetime.datetime,
    timeframe_minutes: int,
    market_hours: Dict,
    num_bars: Optional[int] = None,
    end_date: Optional[datetime.datetime] = None
) -> List[datetime.datetime]:
    """
    Generate timestamps for the given parameters.
    
    Args:
        start_date: Start date
        timeframe_minutes: Timeframe in minutes
        market_hours: Market hours configuration
        num_bars: Number of bars to generate
        end_date: End date (optional if num_bars is specified)
        
    Returns:
        List of datetime objects representing bar timestamps
        
    Raises:
        ValueError: If neither num_bars nor end_date is specified
    """
    if num_bars is None and end_date is None:
        raise ValueError("Either num_bars or end_date must be specified")
    
    timestamps = []
    current_date = start_date
    timeframe_delta = datetime.timedelta(minutes=timeframe_minutes)
    day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    
    # For 24/7 markets like crypto
    if market_hours["type"] == "continuous":
        if num_bars is not None:
            for _ in range(num_bars):
                timestamps.append(current_date)
                current_date += timeframe_delta
        else:
            while current_date <= end_date:
                timestamps.append(current_date)
                current_date += timeframe_delta
                
    # For session-based markets like stocks
    else:
        days = market_hours["days"]
        start_time = market_hours["start_time"]
        end_time = market_hours["end_time"]
        overnight = market_hours["overnight"]
        
        while (num_bars is None and current_date <= end_date) or (num_bars is not None and len(timestamps) < num_bars):
            day_name = day_names[current_date.weekday()]
            
            if day_name in days:
                # Create session start and end datetime objects
                session_start = datetime.datetime.combine(current_date.date(), start_time)
                
                if overnight:
                    next_day = current_date.date() + datetime.timedelta(days=1)
                    session_end = datetime.datetime.combine(next_day, end_time)
                else:
                    session_end = datetime.datetime.combine(current_date.date(), end_time)
                
                # If current_date is before session start, move to session start
                if current_date < session_start:
                    current_date = session_start
                
                # Generate timestamps within the session
                while current_date <= session_end and ((num_bars is None and current_date <= end_date) or (num_bars is not None and len(timestamps) < num_bars)):
                    timestamps.append(current_date)
                    current_date += timeframe_delta
                    
                    if num_bars is not None and len(timestamps) >= num_bars:
                        break
                
                # If we've reached session end, move to next day's session start
                if current_date > session_end:
                    next_day = current_date.date() + datetime.timedelta(days=1)
                    current_date = datetime.datetime.combine(next_day, start_time)
            else:
                # Skip to next day if current day is not a trading day
                next_day = current_date.date() + datetime.timedelta(days=1)
                current_date = datetime.datetime.combine(next_day, datetime.time(0, 0))
    
    return timestamps


def generate_price_data(
    num_bars: int,
    initial_price: float = 100.0,
    volatility: float = 0.01,
    drift: float = 0.0001,
    volume_base: int = 10000,
    volume_volatility: float = 0.3
) -> List[Dict]:
    """
    Generate synthetic OHLCV data using a random walk model.
    
    Args:
        num_bars: Number of bars to generate
        initial_price: Initial price to start from
        volatility: Price volatility parameter
        drift: Price drift parameter
        volume_base: Base volume
        volume_volatility: Volume volatility parameter
        
    Returns:
        List of dictionaries with OHLCV data
    """
    ohlcv_data = []
    current_price = initial_price
    
    for _ in range(num_bars):
        # Generate open price (close of previous bar or initial price)
        open_price = current_price
        
        # Generate random price movement for this bar
        price_change = np.random.normal(drift, volatility) * open_price
        close_price = open_price + price_change
        
        # Generate intrabar movements
        intrabar_volatility = volatility * open_price * np.random.uniform(0.5, 1.5)
        
        # Calculate potential high and low based on volatility
        potential_high = max(open_price, close_price) + abs(np.random.normal(0, intrabar_volatility))
        potential_low = min(open_price, close_price) - abs(np.random.normal(0, intrabar_volatility))
        
        # Ensure high is the highest price and low is the lowest price
        high_price = max(potential_high, open_price, close_price)
        low_price = min(potential_low, open_price, close_price)
        
        # Ensure low price is positive
        low_price = max(low_price, 0.01)
        
        # Generate random volume
        volume_factor = np.random.lognormal(0, volume_volatility)
        volume = int(volume_base * volume_factor * (1 + 2 * abs(price_change) / open_price))
        
        # Round prices to 2 decimal places
        open_price = round(open_price, 2)
        high_price = round(high_price, 2)
        low_price = round(low_price, 2)
        close_price = round(close_price, 2)
        
        ohlcv_data.append({
            "Open": open_price,
            "High": high_price,
            "Low": low_price,
            "Close": close_price,
            "Volume": volume
        })
        
        # Update current price for next iteration
        current_price = close_price
    
    return ohlcv_data


def generate_financial_data(
    timeframe: str,
    start_date: str,
    market_hours: str,
    end_date: Optional[str] = None,
    num_bars: Optional[int] = None,
    initial_price: float = 100.0,
    volatility: float = 0.01,
    drift: float = 0.0001,
    volume_base: int = 10000,
    output_file: Optional[str] = None
) -> pd.DataFrame:
    """
    Generate synthetic financial market data.
    
    Args:
        timeframe: Time interval for each candle (e.g., "1m", "1h", "1d")
        start_date: Start date in format "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS"
        market_hours: Market hours specification (e.g., "mon-fri 09:30-16:00" or "24/7")
        end_date: End date (optional if num_bars is specified)
        num_bars: Number of bars to generate (optional if end_date is specified)
        initial_price: Initial price for the first bar
        volatility: Price volatility parameter
        drift: Price drift parameter
        volume_base: Base volume for volume generation
        output_file: Path to output CSV file (optional)
        
    Returns:
        Pandas DataFrame with generated data
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Parse input parameters
    timeframe_minutes, _ = parse_timeframe(timeframe)
    start_datetime = parse_date(start_date)
    market_hours_config = parse_market_hours(market_hours)
    end_datetime = parse_date(end_date) if end_date else None
    
    # Validate parameters
    if num_bars is None and end_datetime is None:
        raise ValueError("Either num_bars or end_date must be specified")
    
    # Generate timestamps
    timestamps = generate_timestamps(
        start_datetime, 
        timeframe_minutes, 
        market_hours_config, 
        num_bars, 
        end_datetime
    )
    
    # Generate price data
    actual_num_bars = len(timestamps)
    ohlcv_data = generate_price_data(
        actual_num_bars,
        initial_price,
        volatility,
        drift,
        volume_base
    )
    
    # Create DataFrame
    data = []
    for i, ts in enumerate(timestamps):
        entry = {
            "Datetime": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "Open": ohlcv_data[i]["Open"],
            "High": ohlcv_data[i]["High"],
            "Low": ohlcv_data[i]["Low"],
            "Close": ohlcv_data[i]["Close"],
            "Volume": ohlcv_data[i]["Volume"]
        }
        data.append(entry)
    
    df = pd.DataFrame(data)
    
    # Save to file if output_file is specified
    if output_file:
        df.to_csv(output_file, index=False)
    
    return df


def main():
    """
    Main function to run the script from command line.
    """
    parser = argparse.ArgumentParser(description="Generate synthetic financial market data")
    
    parser.add_argument("--timeframe", type=str, required=True, 
                        help="Time interval for each candle (1m, 5m, 15m, 30m, 1h, 4h, 1d)")
    
    parser.add_argument("--start-date", type=str, required=True,
                        help="Start date in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")
    
    parser.add_argument("--market-hours", type=str, required=True,
                        help="Market hours specification (e.g., 'mon-fri 09:30-16:00' or '24/7')")
    
    parser.add_argument("--end-date", type=str, default=None,
                        help="End date (optional if num_bars is specified)")
    
    parser.add_argument("--num-bars", type=int, default=None,
                        help="Number of bars to generate (optional if end_date is specified)")
    
    parser.add_argument("--initial-price", type=float, default=100.0,
                        help="Initial price for the first bar (default: 100.0)")
    
    parser.add_argument("--volatility", type=float, default=0.01,
                        help="Price volatility parameter (default: 0.01)")
    
    parser.add_argument("--drift", type=float, default=0.0001,
                        help="Price drift parameter (default: 0.0001)")
    
    parser.add_argument("--volume-base", type=int, default=10000,
                        help="Base volume for volume generation (default: 10000)")
    
    parser.add_argument("--output-file", type=str, default="synthetic_market_data.csv",
                        help="Path to output CSV file (default: synthetic_market_data.csv)")
    
    args = parser.parse_args()
    
    try:
        df = generate_financial_data(
            timeframe=args.timeframe,
            start_date=args.start_date,
            market_hours=args.market_hours,
            end_date=args.end_date,
            num_bars=args.num_bars,
            initial_price=args.initial_price,
            volatility=args.volatility,
            drift=args.drift,
            volume_base=args.volume_base,
            output_file=args.output_file
        )
        
        print(f"Generated {len(df)} bars of synthetic market data")
        print(f"Output saved to: {args.output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())