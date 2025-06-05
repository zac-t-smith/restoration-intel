"""
Cashflow Module

This module handles cash flow forecasting, cash balance tracking,
and cash position analysis for the Restoration CRM.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import engines and utils
from ..utils import handle_error, Spinner, format_currency, safe_divide

def get_current_cash_balance():
    """
    Get the most recent cash balance entry with proper ordering
    
    Returns:
        Float representing the current cash balance
    """
    with Spinner("Cash Balance"):
        try:
            # In a real implementation, this would query the database
            # Always order by date DESC, id DESC to get the most recent entry
            # For now, we'll just return sample data
            return 45000.00
        except Exception as e:
            handle_error(f"Failed to get current cash balance: {str(e)}", "cashflow_module")
            return 0.0

def get_cash_balance_history(days: int = 90) -> List[Dict]:
    """
    Get cash balance history for the specified number of days
    
    Args:
        days: Number of days of history to retrieve
        
    Returns:
        List of cash balance entries with date and amount
    """
    with Spinner("Cash History"):
        try:
            # In a real implementation, this would query the database
            # Always order by date DESC, id DESC for consistency
            # For now, we'll just return sample data
            
            history = []
            now = datetime.now()
            
            # Generate some sample data points
            for i in range(0, days, 7):  # Weekly data points
                date = now - timedelta(days=i)
                
                # Generate a somewhat realistic balance that trends upward
                base = 30000
                growth = 15000 * (1 - (i / days))
                fluctuation = (i % 5) * 1000
                
                balance = base + growth + fluctuation
                
                history.append({
                    "date": date,
                    "balance": balance,
                    "notes": "Historical balance"
                })
            
            # Return in chronological order
            return sorted(history, key=lambda x: x["date"])
        
        except Exception as e:
            handle_error(f"Failed to get cash balance history: {str(e)}", "cashflow_module")
            return []

def add_cash_balance_entry(amount: float, date: datetime, notes: str = "") -> Dict:
    """
    Add a new cash balance entry
    
    Args:
        amount: The cash balance amount
        date: The date of the cash balance
        notes: Optional notes about the entry
        
    Returns:
        Dictionary with status and message
    """
    try:
        # In a real implementation, this would insert into the database
        return {
            "status": "success",
            "message": "Cash balance entry added successfully",
            "id": 123  # Mock ID
        }
    except Exception as e:
        handle_error(f"Failed to add cash balance entry: {str(e)}", "cashflow_module")
        return {
            "status": "error",
            "message": f"Failed to add cash balance entry: {str(e)}"
        }

def get_cash_flow_forecast(weeks: int = 8) -> Dict:
    """
    Generate a cash flow forecast for the specified number of weeks
    
    Args:
        weeks: Number of weeks to forecast
        
    Returns:
        Dictionary with forecast data
    """
    with Spinner("Cash Flow Forecast"):
        try:
            # Get current cash balance
            current_balance = get_current_cash_balance()
            
            # In a real implementation, this would query pending collections and expenses
            # from the database with consistent date+id ordering
            # For now, we'll just generate sample data
            
            # Generate weekly forecast data
            forecast = []
            running_balance = current_balance
            now = datetime.now()
            
            for i in range(weeks):
                week_start = now + timedelta(weeks=i)
                week_end = week_start + timedelta(days=6)
                
                # Generate some sample inflows and outflows
                inflows = 15000 + (i * 500) + ((i % 3) * 2000)
                outflows = 12000 + (i * 300) + ((i % 4) * 1500)
                
                # Calculate net and running balance
                net = inflows - outflows
                running_balance += net
                
                forecast.append({
                    "week": f"Week {i+1}",
                    "week_start": week_start,
                    "week_end": week_end,
                    "inflows": inflows,
                    "outflows": outflows,
                    "net": net,
                    "balance": running_balance
                })
            
            return {
                "current_balance": current_balance,
                "forecast": forecast,
                "weeks": weeks
            }
        
        except Exception as e:
            handle_error(f"Failed to generate cash flow forecast: {str(e)}", "cashflow_module")
            return {
                "current_balance": 0,
                "forecast": [],
                "weeks": weeks
            }

def get_cash_flow_waterfall(days: int = 30) -> Dict:
    """
    Generate a cash flow waterfall for the specified number of days
    
    Args:
        days: Number of days for the waterfall
        
    Returns:
        Dictionary with waterfall data
    """
    with Spinner("Cash Flow Waterfall"):
        try:
            # Get current cash balance
            current_balance = get_current_cash_balance()
            
            # In a real implementation, this would query pending collections and expenses
            # from the database with consistent date+id ordering by due date
            # For now, we'll just generate sample data
            
            # Generate collections data
            collections = []
            for i in range(5):
                due_day = (i * 5) + 3  # Spread throughout the period
                collections.append({
                    "id": i + 1,
                    "description": f"Collection {i+1}",
                    "amount": 5000 + (i * 1000),
                    "due_date": datetime.now() + timedelta(days=due_day),
                    "probability": 0.9 - (i * 0.1)  # Decreasing probability over time
                })
            
            # Generate expenses data
            expenses = []
            for i in range(7):
                due_day = (i * 4) + 2  # Spread throughout the period
                expenses.append({
                    "id": i + 1,
                    "description": f"Expense {i+1}",
                    "amount": 3000 + (i * 800),
                    "due_date": datetime.now() + timedelta(days=due_day),
                    "urgency": "high" if i < 2 else ("medium" if i < 5 else "low")
                })
            
            # Calculate waterfall points
            waterfall = []
            running_balance = current_balance
            
            # Add starting point
            waterfall.append({
                "name": "Starting Balance",
                "value": running_balance,
                "type": "current"
            })
            
            # Add expected inflows (collections)
            total_inflows = 0
            for collection in collections:
                expected_value = collection["amount"] * collection["probability"]
                total_inflows += expected_value
            
            waterfall.append({
                "name": "Expected Inflows",
                "value": total_inflows,
                "type": "inflow"
            })
            
            running_balance += total_inflows
            
            # Add expected outflows (expenses)
            total_outflows = sum(expense["amount"] for expense in expenses)
            
            waterfall.append({
                "name": "Expected Outflows",
                "value": -total_outflows,  # Negative value for outflows
                "type": "outflow"
            })
            
            running_balance -= total_outflows
            
            # Add ending balance
            waterfall.append({
                "name": "Projected Balance",
                "value": running_balance,
                "type": "projected"
            })
            
            return {
                "current_balance": current_balance,
                "waterfall": waterfall,
                "collections": collections,
                "expenses": expenses,
                "days": days
            }
        
        except Exception as e:
            handle_error(f"Failed to generate cash flow waterfall: {str(e)}", "cashflow_module")
            return {
                "current_balance": 0,
                "waterfall": [],
                "collections": [],
                "expenses": [],
                "days": days
            }

def calculate_runway(cash_balance: float, burn_rate: float) -> float:
    """
    Calculate cash runway in weeks
    
    Args:
        cash_balance: Current cash balance
        burn_rate: Weekly cash burn rate
        
    Returns:
        Number of weeks of runway
    """
    try:
        if burn_rate <= 0:
            return float('inf')  # Infinite runway if burn rate is zero or negative
        
        return cash_balance / burn_rate
    except Exception as e:
        handle_error(f"Failed to calculate runway: {str(e)}", "cashflow_module")
        return 0.0

def get_cash_position_summary() -> Dict:
    """
    Get a summary of the current cash position
    
    Returns:
        Dictionary with cash position summary data
    """
    with Spinner("Cash Position Summary"):
        try:
            # Get current cash balance with proper ordering
            current_balance = get_current_cash_balance()
            
            # In a real implementation, this would query the database
            # For now, we'll just return sample data
            
            # Calculate cash metrics
            avg_weekly_burn = 12500
            runway_weeks = calculate_runway(current_balance, avg_weekly_burn)
            
            # Get pending inflows and outflows
            pending_inflows = 25000
            pending_outflows = 18000
            
            # Calculate projected balance
            projected_balance = current_balance + pending_inflows - pending_outflows
            
            return {
                "current_balance": current_balance,
                "avg_weekly_burn": avg_weekly_burn,
                "runway_weeks": runway_weeks,
                "pending_inflows": pending_inflows,
                "pending_outflows": pending_outflows,
                "projected_balance": projected_balance,
                "cash_status": "healthy" if runway_weeks > 8 else ("warning" if runway_weeks > 4 else "critical")
            }
        
        except Exception as e:
            handle_error(f"Failed to get cash position summary: {str(e)}", "cashflow_module")
            return {}

# Main function to render the cashflow module
def render_cashflow(context=None):
    """Main function to render the cashflow module in a web context"""
    try:
        # Get cash position summary
        summary = get_cash_position_summary()
        
        # Get cash flow forecast
        forecast = get_cash_flow_forecast()
        
        # Get cash flow waterfall
        waterfall = get_cash_flow_waterfall()
        
        # Get cash balance history
        history = get_cash_balance_history()
        
        return {
            "summary": summary,
            "forecast": forecast,
            "waterfall": waterfall,
            "history": history
        }
    except Exception as e:
        handle_error(f"Failed to render cashflow module: {str(e)}", "cashflow_module")
        return {"error": str(e)}