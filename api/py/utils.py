"""
Utility functions for Restoration-Intel API Bridge

This module provides common utility functions used throughout the application.
"""

import time
import logging
import sys
from datetime import datetime
from typing import Optional, Any, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def handle_error(msg: str, module: str) -> None:
    """
    Handle and log errors with module context
    
    Args:
        msg: Error message
        module: Module name where the error occurred
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_log = f"[{timestamp}] ERROR in {module}: {msg}"
    
    # Log the error
    logging.error(error_log)
    
    # Send alert (stub - in production would send to Slack or monitoring system)
    print(f"ALERT: {error_log}")
    
    # In a production environment, you might add:
    # - Error metrics tracking
    # - Slack/Teams notification
    # - Error logging to a service like Sentry

class Spinner:
    """
    Context manager for tracking operation duration and showing a spinner for long operations
    
    Usage:
        with Spinner("module_name"):
            # perform heavy operation
    """
    
    def __init__(self, module: str):
        """
        Initialize the spinner
        
        Args:
            module: Name of the module using the spinner
        """
        self.module = module
        self.start_time = None
        
    def __enter__(self) -> 'Spinner':
        """Start the timer when entering the context"""
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        When exiting the context, calculate elapsed time and log if over threshold
        """
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            if elapsed > 0.3:  # Only log operations taking more than 0.3 seconds
                print(f"Spinner: {self.module} took {elapsed:.3f}s")
                
                # In a production environment, you might:
                # - Track this metric for performance monitoring
                # - Log to a performance tracking system
                # - Alert on consistently slow operations

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default value if denominator is zero
    
    Args:
        numerator: The division numerator
        denominator: The division denominator
        default: Default value to return if denominator is zero
        
    Returns:
        Result of division or default value
    """
    return numerator / denominator if denominator != 0 else default

def format_currency(amount: float) -> str:
    """
    Format a number as currency
    
    Args:
        amount: The monetary amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: The original value
        new_value: The new value
        
    Returns:
        Percentage change as a float
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / abs(old_value)) * 100.0