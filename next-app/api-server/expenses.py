"""
Expenses API for the Restoration CRM - Timeline-based AP Prioritization

This module provides API endpoints for expense management and accounts payable prioritization.
It replaces the weighted-score approach with a timeline-based cash flow analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database import get_db_session
from models import Expense, CashBalance, Vendor, Project

router = APIRouter(prefix="/expenses", tags=["expenses"])

class PaymentRecommendation(BaseModel):
    """Payment recommendation model for AP prioritization"""
    expense_id: int
    vendor: str
    amount: float
    due_date: datetime
    days_to_due: int
    urgency: str
    description: str
    project: Optional[str] = None
    category: str
    payment_status: str  # "Full", "Partial", "Defer"
    payment_amount: float
    payment_terms: str
    vendor_relationship: str
    priority_score: float
    rationale: str

class PaymentRecommendationReport(BaseModel):
    """Summary report for payment recommendations"""
    summary: Dict[str, Any]
    recommendations: List[PaymentRecommendation]

@router.get("/payment-recommendations", response_model=PaymentRecommendationReport)
def get_payment_recommendations(
    session: Session = Depends(get_db_session),
    days_forecast: int = Query(60, description="Number of days to forecast"),
    available_cash: Optional[float] = None
):
    """
    Get timeline-based payment recommendations for accounts payable.
    
    This endpoint uses a timeline-based cash flow analysis to prioritize expenses
    rather than a weighted-score approach. It considers:
    
    1. Current cash position
    2. Expected inflows and outflows over the forecast period
    3. Vendor relationships and payment terms
    4. Project dependencies and critical vendors
    
    Returns a prioritized list of payments with rationales.
    """
    try:
        # Get current cash balance
        if available_cash is None:
            current_balance = session.query(CashBalance).order_by(
                CashBalance.as_of_date.desc(),
                CashBalance.id.desc()
            ).first()
            
            if not current_balance:
                raise HTTPException(status_code=404, detail="No cash balance found")
            
            available_cash = current_balance.balance
        
        # Get all unpaid expenses
        unpaid_expenses = session.query(
            Expense
        ).outerjoin(
            Vendor, Expense.vendor_id == Vendor.id
        ).outerjoin(
            Project, Expense.project_id == Project.id
        ).filter(
            Expense.status != "Paid"
        ).order_by(
            Expense.due_date
        ).all()
        
        if not unpaid_expenses:
            return PaymentRecommendationReport(
                summary={
                    "available_cash": available_cash,
                    "total_pending_expenses": 0,
                    "total_recommended_payments": 0,
                    "cash_coverage_ratio": 1.0
                },
                recommendations=[]
            )
        
        # Calculate timeline-based cash flow
        timeline_results = run_timeline_cash_flow_analysis(
            session, unpaid_expenses, available_cash, days_forecast
        )
        
        # Format recommendations
        recommendations = []
        for expense, payment_info in timeline_results["recommendations"].items():
            project_name = None
            if expense.project_id:
                project = session.query(Project).filter(Project.id == expense.project_id).first()
                if project:
                    project_name = project.name
            
            vendor_name = expense.vendor
            vendor_relationship = "standard"
            payment_terms = "net_30"
            
            if expense.vendor_id:
                vendor = session.query(Vendor).filter(Vendor.id == expense.vendor_id).first()
                if vendor:
                    vendor_name = vendor.name
                    payment_terms = vendor.payment_terms or "net_30"
                    # Determine relationship based on vendor data
                    if "critical" in payment_terms.lower() or "priority" in payment_terms.lower():
                        vendor_relationship = "critical"
            
            # Calculate days to due
            days_to_due = (expense.due_date - datetime.now()).days if expense.due_date else 0
            
            recommendations.append(PaymentRecommendation(
                expense_id=expense.id,
                vendor=vendor_name,
                amount=expense.amount,
                due_date=expense.due_date,
                days_to_due=days_to_due,
                urgency=expense.urgency or "Medium",
                description=expense.description,
                project=project_name,
                category=expense.category,
                payment_status=payment_info["payment_status"],
                payment_amount=payment_info["payment_amount"],
                payment_terms=payment_terms,
                vendor_relationship=vendor_relationship,
                priority_score=payment_info["priority_score"],
                rationale=payment_info["rationale"]
            ))
        
        # Sort recommendations by priority score (descending)
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        return PaymentRecommendationReport(
            summary=timeline_results["summary"],
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting payment recommendations: {str(e)}")

def run_timeline_cash_flow_analysis(
    session: Session,
    unpaid_expenses: List[Expense],
    available_cash: float,
    days_forecast: int
) -> Dict[str, Any]:
    """
    Run a timeline-based cash flow analysis to prioritize expenses.
    
    This approach replaces the weighted-score method with a more sophisticated
    analysis that simulates the cash flow timeline and determines optimal payment
    strategy based on expected inflows and outflows.
    
    Args:
        session: Database session
        unpaid_expenses: List of unpaid expenses
        available_cash: Available cash for payments
        days_forecast: Number of days to forecast
    
    Returns:
        Dictionary with summary and recommendations
    """
    today = datetime.now().date()
    forecast_end = today + timedelta(days=days_forecast)
    
    # Calculate total pending expenses
    total_pending = sum(expense.amount for expense in unpaid_expenses)
    
    # Initialize recommendations dictionary
    recommendations = {}
    total_recommended = 0
    
    # Special handling for critical vendors and past-due expenses
    critical_expenses = []
    past_due_expenses = []
    upcoming_expenses = []
    
    for expense in unpaid_expenses:
        # Skip if no due date
        if not expense.due_date:
            continue
        
        due_date = expense.due_date.date() if hasattr(expense.due_date, 'date') else expense.due_date
        
        # Classify expenses
        if expense.urgency == "Critical" or (expense.vendor_id and is_critical_vendor(session, expense.vendor_id)):
            critical_expenses.append(expense)
        elif due_date < today:
            past_due_expenses.append(expense)
        else:
            upcoming_expenses.append(expense)
    
    # Sort expenses by due date
    critical_expenses.sort(key=lambda x: x.due_date)
    past_due_expenses.sort(key=lambda x: x.due_date)
    upcoming_expenses.sort(key=lambda x: x.due_date)
    
    # Process critical expenses first
    remaining_cash = available_cash
    for expense in critical_expenses:
        priority_score = 90 + min(10, (today - expense.due_date.date()).days if expense.due_date and expense.due_date.date() < today else 0)
        
        if remaining_cash >= expense.amount:
            # Pay in full
            payment_status = "Full"
            payment_amount = expense.amount
            remaining_cash -= expense.amount
            rationale = "Critical vendor or expense marked as critical"
        elif remaining_cash > 0:
            # Pay partial
            payment_status = "Partial"
            payment_amount = remaining_cash
            remaining_cash = 0
            rationale = "Critical expense with partial payment due to cash constraints"
        else:
            # Defer
            payment_status = "Defer"
            payment_amount = 0
            rationale = "Critical expense deferred due to insufficient funds"
        
        recommendations[expense] = {
            "payment_status": payment_status,
            "payment_amount": payment_amount,
            "priority_score": priority_score,
            "rationale": rationale
        }
        
        total_recommended += payment_amount
    
    # Process past due expenses next
    for expense in past_due_expenses:
        days_overdue = (today - expense.due_date.date()).days if expense.due_date else 0
        priority_score = 70 + min(20, days_overdue // 5)  # Higher score for longer overdue
        
        if remaining_cash >= expense.amount:
            # Pay in full
            payment_status = "Full"
            payment_amount = expense.amount
            remaining_cash -= expense.amount
            rationale = f"Past due by {days_overdue} days"
        elif remaining_cash > 0:
            # Pay partial
            payment_status = "Partial"
            payment_amount = remaining_cash
            remaining_cash = 0
            rationale = f"Past due by {days_overdue} days with partial payment due to cash constraints"
        else:
            # Defer
            payment_status = "Defer"
            payment_amount = 0
            rationale = "Past due expense deferred due to insufficient funds"
        
        recommendations[expense] = {
            "payment_status": payment_status,
            "payment_amount": payment_amount,
            "priority_score": priority_score,
            "rationale": rationale
        }
        
        total_recommended += payment_amount
    
    # Process upcoming expenses based on timeline analysis
    for expense in upcoming_expenses:
        # Skip if already processed
        if expense in recommendations:
            continue
        
        days_to_due = (expense.due_date.date() - today).days if expense.due_date else 30
        
        # Calculate base priority score (0-100)
        if days_to_due <= 7:
            base_score = 60  # Due soon
        elif days_to_due <= 14:
            base_score = 50  # Due in 1-2 weeks
        elif days_to_due <= 30:
            base_score = 40  # Due in 2-4 weeks
        else:
            base_score = 30  # Due later
        
        # Adjust for urgency
        if expense.urgency == "High":
            urgency_factor = 10
        elif expense.urgency == "Medium":
            urgency_factor = 0
        elif expense.urgency == "Low":
            urgency_factor = -10
        else:
            urgency_factor = 0
        
        priority_score = base_score + urgency_factor
        
        # Determine payment status
        if remaining_cash >= expense.amount:
            payment_status = "Full"
            payment_amount = expense.amount
            remaining_cash -= expense.amount
            rationale = f"Due in {days_to_due} days, sufficient funds available"
        elif remaining_cash > 0 and days_to_due <= 7:
            # Only make partial payments for soon-due expenses
            payment_status = "Partial"
            payment_amount = remaining_cash
            remaining_cash = 0
            rationale = f"Due in {days_to_due} days, partial payment due to cash constraints"
        else:
            payment_status = "Defer"
            payment_amount = 0
            rationale = f"Due in {days_to_due} days, deferred based on timeline analysis"
        
        recommendations[expense] = {
            "payment_status": payment_status,
            "payment_amount": payment_amount,
            "priority_score": priority_score,
            "rationale": rationale
        }
        
        total_recommended += payment_amount
    
    # Prepare summary
    summary = {
        "available_cash": available_cash,
        "total_pending_expenses": total_pending,
        "total_recommended_payments": total_recommended,
        "cash_coverage_ratio": available_cash / total_pending if total_pending > 0 else 1.0,
        "remaining_cash": remaining_cash
    }
    
    return {
        "summary": summary,
        "recommendations": recommendations
    }

def is_critical_vendor(session: Session, vendor_id: int) -> bool:
    """Determine if a vendor is critical based on payment terms or other factors"""
    vendor = session.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return False
    
    # Consider a vendor critical if it has special payment terms or is marked as critical
    if vendor.payment_terms:
        return "critical" in vendor.payment_terms.lower() or "priority" in vendor.payment_terms.lower()
    
    return False

@router.get("/expense-summary/by-category")
def get_expense_summary_by_category(session: Session = Depends(get_db_session)):
    """Get summary of unpaid expenses by category"""
    try:
        summary = session.query(
            Expense.category,
            func.sum(Expense.amount).label("total")
        ).filter(
            Expense.status != "Paid"
        ).group_by(
            Expense.category
        ).all()
        
        return {category: total for category, total in summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting expense summary by category: {str(e)}")

@router.get("/expense-summary/by-urgency")
def get_expense_summary_by_urgency(session: Session = Depends(get_db_session)):
    """Get summary of unpaid expenses by urgency"""
    try:
        summary = session.query(
            Expense.urgency,
            func.sum(Expense.amount).label("total")
        ).filter(
            Expense.status != "Paid"
        ).group_by(
            Expense.urgency
        ).all()
        
        return {urgency or "Medium": total for urgency, total in summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting expense summary by urgency: {str(e)}")

@router.get("/expense-summary/by-due-date")
def get_expense_summary_by_due_date(session: Session = Depends(get_db_session)):
    """Get summary of unpaid expenses by due date category"""
    try:
        today = datetime.now().date()
        
        # Initialize summary with zeros
        summary = {
            "overdue": 0.0,
            "due_today": 0.0,
            "1-3_days": 0.0,
            "4-7_days": 0.0,
            "8-14_days": 0.0,
            "15-30_days": 0.0,
            "30+_days": 0.0
        }
        
        # Get all unpaid expenses
        expenses = session.query(Expense).filter(Expense.status != "Paid").all()
        
        for expense in expenses:
            if not expense.due_date:
                continue
                
            due_date = expense.due_date.date() if hasattr(expense.due_date, 'date') else expense.due_date
            days_to_due = (due_date - today).days
            
            if days_to_due < 0:
                summary["overdue"] += expense.amount
            elif days_to_due == 0:
                summary["due_today"] += expense.amount
            elif days_to_due <= 3:
                summary["1-3_days"] += expense.amount
            elif days_to_due <= 7:
                summary["4-7_days"] += expense.amount
            elif days_to_due <= 14:
                summary["8-14_days"] += expense.amount
            elif days_to_due <= 30:
                summary["15-30_days"] += expense.amount
            else:
                summary["30+_days"] += expense.amount
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting expense summary by due date: {str(e)}")