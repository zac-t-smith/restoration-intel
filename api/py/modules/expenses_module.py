"""
Expenses Module

This module handles expense management, accounts payable prioritization,
and expense analytics for the Restoration CRM.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import httpx
import asyncio

# Import utils
from api.py.utils import handle_error, Spinner, format_currency, safe_divide

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

async def get_expenses(client: httpx.AsyncClient, filters: Dict = None) -> List[Dict]:
    """
    Get expenses from Supabase with optional filtering
    
    Args:
        client: AsyncClient instance for Supabase
        filters: Optional dictionary of filter criteria
        
    Returns:
        List of expense objects with complete vendor information
    """
    try:
        # Query expenses with vendor information
        query = {
            "select": "*, vendors(name, payment_terms, preferred_payment_method)",
            "order": "due_date.asc"
        }
        if filters:
            query.update(filters)
            
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/expenses",
            params=query
        )
        response.raise_for_status()
        expenses = response.json()
        
        # Ensure vendor info is properly structured
        for expense in expenses:
            vendor_info = expense.pop("vendors", {})
            expense["vendor"] = {
                "id": expense.get("vendor_id"),
                "name": vendor_info.get("name", "Unknown Vendor"),
                "payment_terms": vendor_info.get("payment_terms", 30),
                "preferred_payment_method": vendor_info.get("preferred_payment_method", "check")
            }
            
        return expenses
        
    except Exception as e:
        handle_error(f"Error fetching expenses: {str(e)}")
        return []

async def get_vendor_recommendations(client: httpx.AsyncClient) -> List[Dict]:
    """
    Get vendor payment recommendations
    
    Args:
        client: An initialized httpx.AsyncClient
        
    Returns:
        List of vendor payment recommendations
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/rpc/get_vendor_recommendations"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        
        response = await client.post(url, headers=headers)
        if response.status_code >= 400:
            handle_error(f"API error: {response.text}")
            return []
            
        recommendations = response.json()
        return recommendations
    except Exception as e:
        handle_error(f"Error getting vendor recommendations: {str(e)}")
        return []

def calculate_priority(expense: Dict) -> float:
    """Calculate payment priority score"""
    days_until_due = (expense.get("due_date", datetime.now()) - datetime.now()).days
    amount = expense.get("amount", 0)
    urgency = {"high": 3, "medium": 2, "low": 1}.get(expense.get("urgency", "low"), 1)
    
    # Higher score = higher priority
    priority_score = (
        (1 / max(days_until_due, 1)) * 100 +  # Due date factor
        (amount / 10000) * 50 +                # Amount factor
        urgency * 25                           # Urgency factor
    )
    
    return round(priority_score, 2)

async def get_payment_recommendations() -> List[Dict]:
    """
    Get payment recommendations using the vendor payment recommendation engine
    
    Returns:
        List of payment recommendations
    """
    async with httpx.AsyncClient() as client:
        try:
            # Use the vendor recommendation function to get recommendations
            recommendations = await get_vendor_recommendations(client)
            
            # Enhance recommendations with additional business context
            enhanced_recommendations = []
            for rec in recommendations:
                # Add any business-specific context or formatting
                enhanced_rec = {
                    **rec,
                    "formatted_amount": format_currency(rec["amount"]),
                    "days_text": f"{abs(rec['days_until_due'])} days {'overdue' if rec['days_until_due'] < 0 else 'until due'}"
                }
                enhanced_recommendations.append(enhanced_rec)
            
            return enhanced_recommendations
        except Exception as e:
            handle_error(f"Error in payment recommendations: {str(e)}")
            return []

def get_expense_summary() -> Dict:
    """
    Get a summary of expenses by category, status, and urgency
    
    Returns:
        Dictionary with expense summary data
    """
    with Spinner("Expense Summary"):
        try:
            expenses = get_expenses()
            
            # Calculate summary metrics
            total_amount = sum(expense["amount"] for expense in expenses)
            pending_amount = sum(expense["amount"] for expense in expenses if expense["status"] == "pending")
            overdue_amount = sum(expense["amount"] for expense in expenses 
                               if expense["status"] == "pending" and expense["due_date"] < datetime.now())
            
            # Group by category
            categories = {}
            for expense in expenses:
                category = expense["category"]
                if category not in categories:
                    categories[category] = 0
                categories[category] += expense["amount"]
            
            # Group by urgency
            urgency = {}
            for expense in expenses:
                u = expense["urgency"]
                if u not in urgency:
                    urgency[u] = 0
                urgency[u] += expense["amount"]
            
            return {
                "total_amount": total_amount,
                "pending_amount": pending_amount,
                "overdue_amount": overdue_amount,
                "categories": categories,
                "urgency": urgency
            }
        
        except Exception as e:
            handle_error(f"Failed to get expense summary: {str(e)}", "expenses_module")
            return {}

def get_expense_by_vendor(vendor_id: int) -> List[Dict]:
    """
    Get expenses for a specific vendor
    
    Args:
        vendor_id: ID of the vendor
        
    Returns:
        List of expense objects
    """
    try:
        return get_expenses({"vendor_id": vendor_id})
    except Exception as e:
        handle_error(f"Failed to get expenses for vendor {vendor_id}: {str(e)}", "expenses_module")
        return []

def get_expense_trends(months: int = 6) -> Dict:
    """
    Get expense trends over time
    
    Args:
        months: Number of months to include in the trend analysis
        
    Returns:
        Dictionary with trend data
    """
    with Spinner("Expense Trends"):
        try:
            # In a real implementation, this would query the database
            # For now, we'll just return sample data
            months_data = []
            now = datetime.now()
            
            for i in range(months):
                month = now.replace(day=1) - timedelta(days=30 * i)
                month_name = month.strftime("%b %Y")
                
                # Generate some sample data
                months_data.append({
                    "month": month_name,
                    "materials": 5000 - (i * 200) + (100 * (i % 3)),
                    "labor": 3500 - (i * 100) + (150 * (i % 2)),
                    "services": 2000 - (i * 50) + (75 * (i % 4)),
                    "overhead": 1500
                })
            
            # Reverse to get chronological order
            months_data.reverse()
            
            return {
                "trends": months_data,
                "categories": ["materials", "labor", "services", "overhead"]
            }
        
        except Exception as e:
            handle_error(f"Failed to get expense trends: {str(e)}", "expenses_module")
            return {"trends": [], "categories": []}

def get_vendor_payment_history(vendor_id: int) -> Dict:
    """
    Get payment history for a specific vendor
    
    Args:
        vendor_id: ID of the vendor
        
    Returns:
        Dictionary with payment history data
    """
    with Spinner("Vendor Payment History"):
        try:
            # In a real implementation, this would query the database
            # For now, we'll just return sample data
            
            # Calculate on-time payment percentage
            total_payments = 10
            on_time_payments = 8
            on_time_percentage = (on_time_payments / total_payments) * 100
            
            # Calculate average days to pay
            avg_days_to_pay = 12.5
            
            # Generate payment history
            history = []
            now = datetime.now()
            
            for i in range(total_payments):
                payment_date = now - timedelta(days=30 * i)
                due_date = payment_date - timedelta(days=15 if i % 3 == 0 else 0)
                
                history.append({
                    "invoice_number": f"INV-{2023000 + i}",
                    "amount": 1500 + (i * 100),
                    "due_date": due_date,
                    "payment_date": payment_date,
                    "days_to_pay": (payment_date - due_date).days,
                    "on_time": payment_date <= due_date
                })
            
            return {
                "vendor_id": vendor_id,
                "on_time_percentage": on_time_percentage,
                "avg_days_to_pay": avg_days_to_pay,
                "history": history
            }
        
        except Exception as e:
            handle_error(f"Failed to get vendor payment history: {str(e)}", "expenses_module")
            return {}

# Main function to render the expenses module
def render_expenses(context=None):
    """Main function to render the expenses module in a web context"""
    try:
        # Get payment recommendations
        recommendations = get_payment_recommendations()
        
        # Get expense summary
        summary = get_expense_summary()
        
        return {
            "recommendations": recommendations,
            "summary": summary,
            "expenses": get_expenses()
        }
    except Exception as e:
        handle_error(f"Failed to render expenses module: {str(e)}", "expenses_module")
        return {"error": str(e)}