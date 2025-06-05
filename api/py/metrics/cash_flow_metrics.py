"""
Cash Flow Metrics Module

This module contains functions for calculating cash flow related metrics.
Phase 1: Immediate Cash Flow Stabilization (0-90 Days)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import os
import httpx
import numpy as np
from dotenv import load_dotenv

# Import utils for consistent error handling
from ..utils import handle_error, Spinner, safe_divide

# Load environment variables
load_dotenv()

# Get Supabase URL and anon key from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

async def _call_supabase_rpc(function_name: str, params: Dict = None) -> Any:
    """Call a Supabase RPC function asynchronously"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError("Supabase credentials not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/rpc/{function_name}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=params or {}, headers=headers)
        if response.status_code >= 400:
            handle_error(f"API error: {response.text}", "cash_flow_metrics")
            raise RuntimeError(f"Supabase RPC failed: {response.status_code}")
        return response.json()

async def _execute_sql(query: str, params: Dict = None) -> List[Dict]:
    """Execute a SQL query against Supabase"""
    result = await _call_supabase_rpc("execute_sql", {"query": query, "params": params or {}})
    return result

def calculate_daily_cash_position(date: datetime = None) -> float:
    """
    Calculate the daily cash position for a specific date.
    
    Formula: Beginning Cash + Daily Collections - Daily Disbursements
    
    Args:
        date: The date to calculate the cash position for. Defaults to today.
        
    Returns:
        The calculated cash position for the specified date.
        
    Integration:
        - Add to dashboard as a daily cash position chart
        - Use in cash flow forecasting
        - Trigger alerts if below minimum threshold
    """
    with Spinner("Daily Cash Position"):
        try:
            # Default to today if no date provided
            if date is None:
                date = datetime.now().date()
            
            # SQL query to get beginning cash balance (most recent balance before the specified date)
            beginning_cash_query = """
            SELECT balance
            FROM cash_balances
            WHERE as_of_date <= $1
            ORDER BY as_of_date DESC, id DESC
            LIMIT 1
            """
            
            # SQL query to get daily collections (payments received on the specified date)
            collections_query = """
            SELECT COALESCE(SUM(amount), 0) as total_collections
            FROM collections
            WHERE actual_date = $1
            AND status = 'received'
            """
            
            # SQL query to get daily disbursements (expenses paid on the specified date)
            disbursements_query = """
            SELECT COALESCE(SUM(amount), 0) as total_disbursements
            FROM expenses
            WHERE paid_date = $1
            AND status = 'paid'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return a placeholder value
            return 45000.0
        
        except Exception as e:
            handle_error(f"Failed to calculate daily cash position: {str(e)}", "cash_flow_metrics")
            raise RuntimeError(f"Failed to calculate daily cash position: {str(e)}")

def get_dso() -> float:
    """
    Calculate Days Sales Outstanding (DSO).
    
    Formula: (Accounts Receivable ÷ Daily Revenue)
    
    Returns:
        The calculated DSO value in days.
        
    Integration:
        - Component of Cash Conversion Cycle
        - Add to financial dashboard
        - Use in collections optimization
    """
    with Spinner("DSO Calculation"):
        try:
            # SQL query to get total accounts receivable (unpaid collections)
            ar_query = """
            SELECT COALESCE(SUM(amount), 0) as total_ar
            FROM collections
            WHERE status = 'pending'
            """
            
            # SQL query to get total revenue in the last 90 days
            revenue_query = """
            SELECT COALESCE(SUM(amount), 0) as total_revenue
            FROM collections
            WHERE status = 'received'
            AND actual_date >= NOW() - INTERVAL '90 days'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return a placeholder value
            return 32.5  # 32.5 days
        
        except Exception as e:
            handle_error(f"Failed to calculate DSO: {str(e)}", "cash_flow_metrics")
            raise RuntimeError(f"Failed to calculate DSO: {str(e)}")

def get_dio() -> float:
    """
    Calculate Days Inventory Outstanding (DIO).
    
    Formula: (Inventory ÷ Daily COGS)
    
    Returns:
        The calculated DIO value in days.
        
    Integration:
        - Component of Cash Conversion Cycle
        - Add to inventory management dashboard
        - Use in material ordering optimization
    """
    with Spinner("DIO Calculation"):
        try:
            # SQL query to get total inventory value
            # Note: This assumes an inventory table exists. If not, this would need to be modified.
            inventory_query = """
            SELECT COALESCE(SUM(value), 0) as total_inventory
            FROM inventory
            WHERE status = 'active'
            """
            
            # SQL query to get total COGS in the last 90 days
            # Note: Using expenses with category 'materials' as a proxy for COGS
            cogs_query = """
            SELECT COALESCE(SUM(amount), 0) as total_cogs
            FROM expenses
            WHERE category = 'materials'
            AND created_at >= NOW() - INTERVAL '90 days'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return a placeholder value
            return 15.2  # 15.2 days
        
        except Exception as e:
            handle_error(f"Failed to calculate DIO: {str(e)}", "cash_flow_metrics")
            raise RuntimeError(f"Failed to calculate DIO: {str(e)}")

def get_dpo() -> float:
    """
    Calculate Days Payable Outstanding (DPO).
    
    Formula: (Accounts Payable ÷ Daily Expenses)
    
    Returns:
        The calculated DPO value in days.
        
    Integration:
        - Component of Cash Conversion Cycle
        - Add to vendor management dashboard
        - Use in payment optimization
    """
    with Spinner("DPO Calculation"):
        try:
            # SQL query to get total accounts payable (unpaid expenses)
            ap_query = """
            SELECT COALESCE(SUM(amount), 0) as total_ap
            FROM expenses
            WHERE status = 'pending'
            """
            
            # SQL query to get total expenses in the last 90 days
            expenses_query = """
            SELECT COALESCE(SUM(amount), 0) as total_expenses
            FROM expenses
            WHERE status = 'paid'
            AND paid_date >= NOW() - INTERVAL '90 days'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return a placeholder value
            return 28.7  # 28.7 days
        
        except Exception as e:
            handle_error(f"Failed to calculate DPO: {str(e)}", "cash_flow_metrics")
            raise RuntimeError(f"Failed to calculate DPO: {str(e)}")

def calculate_ccc() -> float:
    """
    Calculate Cash Conversion Cycle (CCC).
    
    Formula: DSO + DIO - DPO
    
    Returns:
        The calculated CCC value in days.
        
    Integration:
        - Add to financial dashboard as key performance indicator
        - Use in working capital optimization
        - Include in investor reports
    """
    with Spinner("CCC Calculation"):
        try:
            # Get component metrics
            dso = get_dso()
            dio = get_dio()
            dpo = get_dpo()
            
            # Calculate CCC
            ccc = dso + dio - dpo
            
            return ccc
        
        except Exception as e:
            handle_error(f"Failed to calculate CCC: {str(e)}", "cash_flow_metrics")
            raise RuntimeError(f"Failed to calculate CCC: {str(e)}")

def get_ar_aging_buckets() -> Dict[str, float]:
    """
    Calculate Accounts Receivable aging buckets.
    
    Buckets: 0-30, 31-60, 61-90, 90+ days
    
    Returns:
        Dictionary with AR amounts in each aging bucket and percentages.
        
    Integration:
        - Add to collections dashboard as aging chart
        - Use in collections prioritization
        - Include in risk assessment
    """
    with Spinner("AR Aging"):
        try:
            # SQL query to get AR in each aging bucket
            ar_aging_query = """
            SELECT
                CASE
                    WHEN NOW()::date - expected_date <= 30 THEN '0-30'
                    WHEN NOW()::date - expected_date <= 60 THEN '31-60'
                    WHEN NOW()::date - expected_date <= 90 THEN '61-90'
                    ELSE '90+'
                END as bucket,
                SUM(amount) as amount
            FROM collections
            WHERE status = 'pending'
            GROUP BY bucket
            ORDER BY bucket
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            result = {
                "0-30": 25000.0,
                "31-60": 15000.0,
                "61-90": 8000.0,
                "90+": 4000.0
            }
            
            # Calculate total AR
            total_ar = sum(result.values())
            
            # Calculate percentages
            percentages = {}
            for bucket, amount in result.items():
                percentages[f"{bucket}_pct"] = (amount / total_ar * 100) if total_ar > 0 else 0
            
            # Combine results
            result.update(percentages)
            
            return result
        
        except Exception as e:
            handle_error(f"Failed to calculate AR aging buckets: {str(e)}", "cash_flow_metrics")
            raise RuntimeError(f"Failed to calculate AR aging buckets: {str(e)}")

def get_weekly_cashflow_forecast(start_date: datetime = None, weeks: int = 13) -> List[Dict]:
    """
    Generate a 13-week rolling cash flow forecast.
    
    Formula: Weekly: Collections + Other Income - Fixed Costs - Variable Costs
    
    Args:
        start_date: The start date for the forecast. Defaults to today.
        weeks: Number of weeks to forecast. Defaults to 13.
        
    Returns:
        List of dictionaries with weekly forecasts containing:
        - week_start: Start date of the week
        - week_end: End date of the week
        - collections: Expected collections
        - other_income: Expected other income
        - fixed_costs: Expected fixed costs
        - variable_costs: Expected variable costs
        - net_cash_flow: Net cash flow for the week
        - ending_balance: Ending cash balance for the week
        
    Integration:
        - Add to cash flow dashboard as weekly forecast chart
        - Use in payment prioritization
        - Include in cash management strategy
    """
    with Spinner("Weekly Cash Flow Forecast"):
        try:
            # Default to today if no start date provided
            if start_date is None:
                start_date = datetime.now().date()
            
            # SQL query to get expected collections by week
            collections_query = """
            SELECT
                date_trunc('week', expected_date) as week_start,
                SUM(amount * (confidence_percentage / 100)) as expected_amount
            FROM collections
            WHERE status = 'pending'
            AND expected_date BETWEEN $1 AND $1 + INTERVAL '$2 weeks'
            GROUP BY week_start
            ORDER BY week_start
            """
            
            # SQL query to get expected expenses by week
            expenses_query = """
            SELECT
                date_trunc('week', due_date) as week_start,
                SUM(CASE WHEN category IN ('rent', 'utilities', 'insurance', 'salaries') THEN amount ELSE 0 END) as fixed_costs,
                SUM(CASE WHEN category NOT IN ('rent', 'utilities', 'insurance', 'salaries') THEN amount ELSE 0 END) as variable_costs
            FROM expenses
            WHERE status = 'pending'
            AND due_date BETWEEN $1 AND $1 + INTERVAL '$2 weeks'
            GROUP BY week_start
            ORDER BY week_start
            """
            
            # SQL query to get current cash balance
            balance_query = """
            SELECT balance
            FROM cash_balances
            ORDER BY as_of_date DESC, id DESC
            LIMIT 1
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            
            forecast = []
            current_balance = 45000.0  # Placeholder for current balance
            
            for i in range(weeks):
                week_start = start_date + timedelta(days=i*7)
                week_end = week_start + timedelta(days=6)
                
                # Generate some sample data with slight randomness
                collections = 15000.0 + (np.random.random() - 0.5) * 3000
                other_income = 500.0 + (np.random.random() - 0.5) * 200
                fixed_costs = 8000.0 + (np.random.random() - 0.5) * 500
                variable_costs = 5000.0 + (np.random.random() - 0.5) * 2000
                
                # Calculate net cash flow
                net_cash_flow = collections + other_income - fixed_costs - variable_costs
                
                # Update balance
                ending_balance = current_balance + net_cash_flow
                current_balance = ending_balance
                
                # Add to forecast
                forecast.append({
                    "week_start": week_start.strftime("%Y-%m-%d"),
                    "week_end": week_end.strftime("%Y-%m-%d"),
                    "collections": round(collections, 2),
                    "other_income": round(other_income, 2),
                    "fixed_costs": round(fixed_costs, 2),
                    "variable_costs": round(variable_costs, 2),
                    "net_cash_flow": round(net_cash_flow, 2),
                    "ending_balance": round(ending_balance, 2)
                })
            
            return forecast
        
        except Exception as e:
            handle_error(f"Failed to generate weekly cash flow forecast: {str(e)}", "cash_flow_metrics")
            raise RuntimeError(f"Failed to generate weekly cash flow forecast: {str(e)}")