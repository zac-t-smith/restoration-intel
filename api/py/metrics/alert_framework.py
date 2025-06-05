"""
Alert Framework and Decision Matrices Module

This module contains functions for detecting issues, prioritizing payments,
identifying revenue leaks, and generating smart alerts for business operations.
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
            handle_error(f"API error: {response.text}", "alert_framework")
            raise RuntimeError(f"Supabase RPC failed: {response.status_code}")
        return response.json()

async def _execute_sql(query: str, params: Dict = None) -> List[Dict]:
    """Execute a SQL query against Supabase"""
    result = await _call_supabase_rpc("execute_sql", {"query": query, "params": params or {}})
    return result

# ---------------------- Red Alerts & Yellow Warnings ----------------------

def check_red_alerts() -> List[Dict[str, Any]]:
    """
    Check for Red Alert conditions that require immediate attention.
    
    Red Alert conditions:
    - Daily Cash Balance < 10-day runway
    - Collection Rate < 85% of monthly billings
    - Job Completion Rate < 90%
    - Gross Margin < 40% for 2+ weeks
    
    Returns:
        List of red alert dictionaries with details.
        
    Integration:
        - Add to dashboard alert banner
        - Send to Slack/email notifications
        - Include in daily management report
    """
    with Spinner("Red Alerts Check"):
        try:
            alerts = []
            
            # Check cash balance runway
            cash_query = """
            SELECT 
                b.balance as current_balance,
                (
                    SELECT AVG(amount)
                    FROM expenses
                    WHERE status = 'pending'
                    AND due_date <= (NOW() + INTERVAL '10 days')
                ) as ten_day_expenses
            FROM cash_balances b
            ORDER BY b.as_of_date DESC, b.id DESC
            LIMIT 1
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            current_balance = 32000       # $32K current cash
            ten_day_expenses = 35000      # $35K in expenses due in next 10 days
            
            if current_balance < ten_day_expenses:
                alerts.append({
                    "type": "red",
                    "code": "low_cash_runway",
                    "message": f"Cash balance ({current_balance}) below 10-day expense needs ({ten_day_expenses})",
                    "severity": 10,
                    "action": "Accelerate collections, delay non-critical payments",
                    "details": {
                        "current_balance": current_balance,
                        "ten_day_expenses": ten_day_expenses,
                        "deficit": ten_day_expenses - current_balance
                    }
                })
            
            # Check collection rate
            collection_query = """
            WITH monthly_billings AS (
                SELECT 
                    SUM(amount) as billed_amount
                FROM collections
                WHERE created_at >= NOW() - INTERVAL '30 days'
            ),
            collected AS (
                SELECT 
                    SUM(amount) as collected_amount
                FROM collections
                WHERE status = 'received'
                AND created_at >= NOW() - INTERVAL '30 days'
            )
            SELECT 
                mb.billed_amount,
                c.collected_amount,
                (c.collected_amount / NULLIF(mb.billed_amount, 0) * 100) as collection_rate
            FROM monthly_billings mb, collected c
            """
            
            # Placeholder values
            billed_amount = 120000      # $120K billed
            collected_amount = 96000    # $96K collected
            collection_rate = (collected_amount / billed_amount * 100) if billed_amount > 0 else 0
            
            if collection_rate < 85:
                alerts.append({
                    "type": "red",
                    "code": "low_collection_rate",
                    "message": f"Collection rate ({collection_rate:.1f}%) below 85% threshold",
                    "severity": 9,
                    "action": "Launch aggressive collection effort on overdue accounts",
                    "details": {
                        "billed_amount": billed_amount,
                        "collected_amount": collected_amount,
                        "collection_rate": collection_rate,
                        "target_rate": 85
                    }
                })
            
            # Check job completion rate
            completion_query = """
            WITH job_stats AS (
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs
                FROM projects
                WHERE start_date >= NOW() - INTERVAL '30 days'
            )
            SELECT 
                total_jobs,
                completed_jobs,
                (completed_jobs * 100.0 / NULLIF(total_jobs, 0)) as completion_rate
            FROM job_stats
            """
            
            # Placeholder values
            total_jobs = 45            # 45 jobs started
            completed_jobs = 38        # 38 jobs completed
            completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            if completion_rate < 90:
                alerts.append({
                    "type": "red",
                    "code": "low_completion_rate",
                    "message": f"Job completion rate ({completion_rate:.1f}%) below 90% threshold",
                    "severity": 8,
                    "action": "Identify bottlenecks in job completion process",
                    "details": {
                        "total_jobs": total_jobs,
                        "completed_jobs": completed_jobs,
                        "completion_rate": completion_rate,
                        "target_rate": 90
                    }
                })
            
            # Check gross margin
            margin_query = """
            WITH weekly_margins AS (
                SELECT 
                    date_trunc('week', created_at) as week,
                    (
                        SUM(total_revenue) - SUM(total_expenses) - SUM(allocated_lead_cost)
                    ) / NULLIF(SUM(total_revenue), 0) * 100 as gross_margin
                FROM projects
                WHERE created_at >= NOW() - INTERVAL '4 weeks'
                GROUP BY date_trunc('week', created_at)
            )
            SELECT 
                week,
                gross_margin,
                COUNT(*) OVER (ORDER BY week ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) as consecutive_low_weeks
            FROM weekly_margins
            WHERE gross_margin < 40
            ORDER BY week DESC
            """
            
            # Placeholder values
            recent_margins = [
                {"week": "2023-05-22", "margin": 42.5},
                {"week": "2023-05-15", "margin": 38.2},
                {"week": "2023-05-08", "margin": 37.5},
                {"week": "2023-05-01", "margin": 41.3}
            ]
            
            # Check if we have 2+ consecutive weeks below 40%
            low_margin_weeks = [w for w in recent_margins if w["margin"] < 40]
            
            if len(low_margin_weeks) >= 2:
                alerts.append({
                    "type": "red",
                    "code": "sustained_low_margin",
                    "message": f"Gross margin below 40% for {len(low_margin_weeks)} consecutive weeks",
                    "severity": 9,
                    "action": "Review pricing and cost structure immediately",
                    "details": {
                        "recent_margins": recent_margins,
                        "low_margin_weeks": low_margin_weeks,
                        "threshold": 40
                    }
                })
            
            return alerts
        
        except Exception as e:
            handle_error(f"Failed to check red alerts: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to check red alerts: {str(e)}")

def check_yellow_warnings() -> List[Dict[str, Any]]:
    """
    Check for Yellow Warning conditions that require attention.
    
    Yellow Warning conditions:
    - DSO increases > 5 days MoM
    - CAC rises > 20% without CLV gain
    - Technician Utilization < 65%
    - Insurance Carrier Payment Delays up > 10 days
    
    Returns:
        List of yellow warning dictionaries with details.
        
    Integration:
        - Add to dashboard warnings section
        - Include in weekly management report
        - Use in operations planning
    """
    with Spinner("Yellow Warnings Check"):
        try:
            warnings = []
            
            # Check DSO increase
            dso_query = """
            WITH monthly_dso AS (
                SELECT 
                    date_trunc('month', created_at) as month,
                    AVG(actual_date - expected_date) as avg_dso_days
                FROM collections
                WHERE status = 'received'
                AND created_at >= NOW() - INTERVAL '2 months'
                GROUP BY date_trunc('month', created_at)
            )
            SELECT 
                m1.month as current_month,
                m1.avg_dso_days as current_dso,
                m2.month as previous_month,
                m2.avg_dso_days as previous_dso,
                (m1.avg_dso_days - m2.avg_dso_days) as dso_change
            FROM monthly_dso m1
            JOIN monthly_dso m2 ON m1.month = (m2.month + INTERVAL '1 month')
            WHERE m1.month = date_trunc('month', NOW())
            """
            
            # Placeholder values
            current_dso = 28.5         # 28.5 days current month
            previous_dso = 22.8        # 22.8 days previous month
            dso_change = current_dso - previous_dso
            
            if dso_change > 5:
                warnings.append({
                    "type": "yellow",
                    "code": "increasing_dso",
                    "message": f"DSO increased by {dso_change:.1f} days month-over-month",
                    "severity": 7,
                    "action": "Review collection process and largest outstanding receivables",
                    "details": {
                        "current_dso": current_dso,
                        "previous_dso": previous_dso,
                        "dso_change": dso_change,
                        "threshold": 5
                    }
                })
            
            # Check CAC increase without CLV gain
            cac_clv_query = """
            WITH current_period AS (
                SELECT 
                    AVG(lead_cost) as avg_cac,
                    (
                        AVG(total_revenue) * 
                        (SUM(total_revenue) - SUM(total_expenses) - SUM(allocated_lead_cost)) / 
                        NULLIF(SUM(total_revenue), 0) * 
                        3  -- assuming 3 year customer relationship
                    ) as avg_clv
                FROM leads l
                LEFT JOIN projects p ON l.id = p.lead_id
                WHERE l.created_at >= NOW() - INTERVAL '3 months'
            ),
            previous_period AS (
                SELECT 
                    AVG(lead_cost) as avg_cac,
                    (
                        AVG(total_revenue) * 
                        (SUM(total_revenue) - SUM(total_expenses) - SUM(allocated_lead_cost)) / 
                        NULLIF(SUM(total_revenue), 0) * 
                        3  -- assuming 3 year customer relationship
                    ) as avg_clv
                FROM leads l
                LEFT JOIN projects p ON l.id = p.lead_id
                WHERE l.created_at BETWEEN NOW() - INTERVAL '6 months' AND NOW() - INTERVAL '3 months'
            )
            SELECT 
                cp.avg_cac as current_cac,
                cp.avg_clv as current_clv,
                pp.avg_cac as previous_cac,
                pp.avg_clv as previous_clv,
                (cp.avg_cac - pp.avg_cac) / NULLIF(pp.avg_cac, 0) * 100 as cac_change_pct,
                (cp.avg_clv - pp.avg_clv) / NULLIF(pp.avg_clv, 0) * 100 as clv_change_pct
            FROM current_period cp, previous_period pp
            """
            
            # Placeholder values
            current_cac = 350          # $350 current CAC
            previous_cac = 280         # $280 previous CAC
            current_clv = 3200         # $3200 current CLV
            previous_clv = 3150        # $3150 previous CLV
            
            cac_change_pct = ((current_cac - previous_cac) / previous_cac * 100) if previous_cac > 0 else 0
            clv_change_pct = ((current_clv - previous_clv) / previous_clv * 100) if previous_clv > 0 else 0
            
            if cac_change_pct > 20 and clv_change_pct < cac_change_pct:
                warnings.append({
                    "type": "yellow",
                    "code": "cac_outpacing_clv",
                    "message": f"CAC increased by {cac_change_pct:.1f}% without proportional CLV gain ({clv_change_pct:.1f}%)",
                    "severity": 7,
                    "action": "Review marketing spend efficiency and lead qualification process",
                    "details": {
                        "current_cac": current_cac,
                        "previous_cac": previous_cac,
                        "cac_change_pct": cac_change_pct,
                        "current_clv": current_clv,
                        "previous_clv": previous_clv,
                        "clv_change_pct": clv_change_pct,
                        "cac_threshold": 20
                    }
                })
            
            # Check technician utilization
            utilization_query = """
            WITH tech_hours AS (
                SELECT 
                    tech_id,
                    SUM(billable_hours) as total_billable,
                    SUM(available_hours) as total_available,
                    SUM(billable_hours) / NULLIF(SUM(available_hours), 0) * 100 as utilization_rate
                FROM technician_hours
                WHERE date >= NOW() - INTERVAL '30 days'
                GROUP BY tech_id
            )
            SELECT 
                AVG(utilization_rate) as avg_utilization,
                COUNT(*) as total_techs,
                COUNT(CASE WHEN utilization_rate < 65 THEN 1 END) as underutilized_techs
            FROM tech_hours
            """
            
            # Placeholder values
            avg_utilization = 68       # 68% average utilization
            total_techs = 15           # 15 technicians
            underutilized_techs = 6    # 6 technicians below 65%
            
            if avg_utilization < 65 or (underutilized_techs / total_techs > 0.3):
                warnings.append({
                    "type": "yellow",
                    "code": "low_tech_utilization",
                    "message": f"Technician utilization at {avg_utilization:.1f}% (threshold: 65%); {underutilized_techs} of {total_techs} techs underutilized",
                    "severity": 6,
                    "action": "Review scheduling efficiency and crew assignments",
                    "details": {
                        "avg_utilization": avg_utilization,
                        "total_techs": total_techs,
                        "underutilized_techs": underutilized_techs,
                        "underutilized_percentage": (underutilized_techs / total_techs * 100) if total_techs > 0 else 0,
                        "threshold": 65
                    }
                })
            
            # Check insurance carrier payment delays
            carrier_delays_query = """
            WITH carrier_payment_times AS (
                SELECT 
                    insurance_carrier,
                    AVG(actual_date - expected_date) as avg_delay_days
                FROM collections c
                JOIN projects p ON c.project_id = p.id
                WHERE c.status = 'received'
                AND p.insurance_carrier IS NOT NULL
                AND c.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY insurance_carrier
            ),
            previous_carrier_times AS (
                SELECT 
                    insurance_carrier,
                    AVG(actual_date - expected_date) as avg_delay_days
                FROM collections c
                JOIN projects p ON c.project_id = p.id
                WHERE c.status = 'received'
                AND p.insurance_carrier IS NOT NULL
                AND c.created_at BETWEEN NOW() - INTERVAL '60 days' AND NOW() - INTERVAL '30 days'
                GROUP BY insurance_carrier
            )
            SELECT 
                c.insurance_carrier,
                c.avg_delay_days as current_delay,
                p.avg_delay_days as previous_delay,
                (c.avg_delay_days - p.avg_delay_days) as delay_change
            FROM carrier_payment_times c
            JOIN previous_carrier_times p ON c.insurance_carrier = p.insurance_carrier
            WHERE (c.avg_delay_days - p.avg_delay_days) > 10
            """
            
            # Placeholder values
            carrier_delays = [
                {"carrier": "State Farm", "current_delay": 22, "previous_delay": 11, "delay_change": 11},
                {"carrier": "Progressive", "current_delay": 28, "previous_delay": 15, "delay_change": 13}
            ]
            
            if carrier_delays:
                for delay in carrier_delays:
                    warnings.append({
                        "type": "yellow",
                        "code": "carrier_payment_delays",
                        "message": f"{delay['carrier']} payment delays increased by {delay['delay_change']} days",
                        "severity": 6,
                        "action": f"Contact {delay['carrier']} representative to resolve payment delays",
                        "details": delay
                    })
            
            return warnings
        
        except Exception as e:
            handle_error(f"Failed to check yellow warnings: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to check yellow warnings: {str(e)}")

# ---------------------- Priority Payment Decision Matrix ----------------------

def calculate_payment_priority(expense_id: int = None, vendor: str = None, 
                              urgency: str = None, impact_score: int = None,
                              days_until_due: int = None) -> Dict[str, Any]:
    """
    Calculate payment priority score for expenses.
    
    Priority levels:
    - Must Pay (Score 10/10) – payroll, insurance, equipment financing
    - Should Pay (Score 7-9/10) – key suppliers, rent, critical maintenance
    - Can Defer (Score 4-6/10) – non-critical vendors
    - Low Priority (Score 1-3/10) – discretionary expenses
    
    Args:
        expense_id: Optional ID of a specific expense to score
        vendor: Optional vendor name to filter expenses
        urgency: Optional urgency level to filter expenses
        impact_score: Optional impact score to use in calculation
        days_until_due: Optional days until due to use in calculation
        
    Returns:
        Dictionary with payment priority details.
        
    Integration:
        - Add to accounts payable dashboard
        - Use in cash flow management
        - Include in vendor relationship management
    """
    with Spinner("Payment Priority Calculation"):
        try:
            # If expense_id is provided, get the details for that expense
            if expense_id:
                query = f"""
                SELECT 
                    e.id,
                    e.vendor,
                    e.amount,
                    e.category,
                    e.urgency,
                    e.due_date,
                    (e.due_date - NOW()::date) as days_until_due,
                    v.name as vendor_name,
                    v.sla_days
                FROM expenses e
                LEFT JOIN vendors v ON e.vendor_id = v.id
                WHERE e.id = {expense_id}
                AND e.status = 'pending'
                """
                
                # TODO: Implement the actual database call
                # For now, we'll use placeholder values
                expense = {
                    "id": expense_id,
                    "vendor": "Quality Materials Inc",
                    "amount": 5800,
                    "category": "materials",
                    "urgency": "medium",
                    "due_date": "2023-06-15",
                    "days_until_due": 8,
                    "vendor_name": "Quality Materials Inc",
                    "sla_days": 30
                }
                
                # Calculate the payment priority score
                score = _calculate_score(expense, impact_score)
                
                # Determine the priority level
                priority_level = _get_priority_level(score)
                
                return {
                    "expense_id": expense_id,
                    "score": score,
                    "priority_level": priority_level,
                    "rationale": _get_payment_rationale(expense, score),
                    "expense_details": expense
                }
            
            # If filtering by vendor, urgency, etc.
            elif vendor or urgency:
                where_clauses = []
                if vendor:
                    where_clauses.append(f"(e.vendor = '{vendor}' OR v.name = '{vendor}')")
                if urgency:
                    where_clauses.append(f"e.urgency = '{urgency}'")
                
                where_sql = " AND ".join(where_clauses)
                
                query = f"""
                SELECT 
                    e.id,
                    e.vendor,
                    e.amount,
                    e.category,
                    e.urgency,
                    e.due_date,
                    (e.due_date - NOW()::date) as days_until_due,
                    v.name as vendor_name,
                    v.sla_days
                FROM expenses e
                LEFT JOIN vendors v ON e.vendor_id = v.id
                WHERE e.status = 'pending'
                AND {where_sql}
                """
                
                # TODO: Implement the actual database call
                # For now, we'll use placeholder values
                expenses = [
                    {
                        "id": 101,
                        "vendor": "Premier Contractors",
                        "amount": 12500,
                        "category": "services",
                        "urgency": "high",
                        "due_date": "2023-06-10",
                        "days_until_due": 3,
                        "vendor_name": "Premier Contractors",
                        "sla_days": 15
                    },
                    {
                        "id": 102,
                        "vendor": "Premier Contractors",
                        "amount": 8750,
                        "category": "materials",
                        "urgency": "medium",
                        "due_date": "2023-06-18",
                        "days_until_due": 11,
                        "vendor_name": "Premier Contractors",
                        "sla_days": 15
                    }
                ]
                
                # Calculate scores for each expense
                scored_expenses = []
                for exp in expenses:
                    score = _calculate_score(exp, impact_score)
                    priority_level = _get_priority_level(score)
                    
                    scored_expenses.append({
                        "expense_id": exp["id"],
                        "score": score,
                        "priority_level": priority_level,
                        "rationale": _get_payment_rationale(exp, score),
                        "expense_details": exp
                    })
                
                # Sort by score descending
                scored_expenses.sort(key=lambda x: x["score"], reverse=True)
                
                return {
                    "expenses": scored_expenses,
                    "count": len(scored_expenses),
                    "filter_criteria": {
                        "vendor": vendor,
                        "urgency": urgency
                    }
                }
            
            # If no specific filters, calculate scores for all pending expenses
            else:
                # TODO: Implement the actual database call
                # For now, we'll use placeholder values and a simulated calculation
                # In a real implementation, this would fetch all pending expenses and calculate scores
                
                # Return simulated direct calculation
                return {
                    "message": "Direct calculation",
                    "score": _direct_score_calculation(urgency, impact_score, days_until_due),
                    "priority_level": _get_priority_level(_direct_score_calculation(urgency, impact_score, days_until_due)),
                    "parameters": {
                        "urgency": urgency,
                        "impact_score": impact_score,
                        "days_until_due": days_until_due
                    }
                }
        
        except Exception as e:
            handle_error(f"Failed to calculate payment priority: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to calculate payment priority: {str(e)}")

def _calculate_score(expense: Dict[str, Any], impact_score: int = None) -> float:
    """Calculate payment priority score based on expense details"""
    # Base score components
    urgency_scores = {"high": 4, "medium": 2.5, "low": 1}
    category_scores = {
        "payroll": 5, "insurance": 5, "equipment_financing": 5,  # Must pay
        "rent": 4, "key_supplier": 4, "critical_maintenance": 4,  # Should pay
        "materials": 3, "services": 3,  # Depends on context
        "utilities": 3, "maintenance": 2.5,  # Can defer if needed
        "marketing": 2, "office_supplies": 1.5,  # Low priority
        "discretionary": 1  # Lowest priority
    }
    
    # Get base scores
    urgency_score = urgency_scores.get(expense["urgency"], 2)
    category_score = category_scores.get(expense["category"], 2)
    
    # Due date factor (higher score for more urgent due dates)
    days_until_due = expense.get("days_until_due", 30)
    due_date_factor = max(0, 1 - (days_until_due / 30))  # 0 to 1 scale, higher for closer due dates
    
    # SLA factor (higher score if close to vendor SLA)
    sla_days = expense.get("sla_days", 30)
    sla_factor = 0
    if days_until_due <= 0:  # Already overdue
        sla_factor = 1
    elif sla_days > 0:
        sla_factor = max(0, 1 - (days_until_due / sla_days))
    
    # Impact score (if provided, otherwise use category as proxy)
    impact = impact_score if impact_score is not None else category_score
    
    # Calculate final score (0-10 scale)
    score = (urgency_score * 0.3) + (impact * 0.3) + (due_date_factor * 0.2) + (sla_factor * 0.2)
    score = min(10, score * 2)  # Scale to 0-10 and cap at 10
    
    return round(score, 1)

def _direct_score_calculation(urgency: str, impact_score: int, days_until_due: int) -> float:
    """Calculate payment priority score directly from parameters"""
    if not urgency or impact_score is None or days_until_due is None:
        return 5.0  # Default middle score
    
    # Base scores
    urgency_scores = {"high": 4, "medium": 2.5, "low": 1}
    urgency_score = urgency_scores.get(urgency, 2)
    
    # Due date factor (higher score for more urgent due dates)
    due_date_factor = max(0, 1 - (days_until_due / 30))
    
    # Calculate final score (0-10 scale)
    score = (urgency_score * 0.4) + (impact_score * 0.4) + (due_date_factor * 0.2)
    score = min(10, score * 2)
    
    return round(score, 1)

def _get_priority_level(score: float) -> str:
    """Convert score to priority level"""
    if score >= 10:
        return "Must Pay"
    elif 7 <= score < 10:
        return "Should Pay"
    elif 4 <= score < 7:
        return "Can Defer"
    else:
        return "Low Priority"

def _get_payment_rationale(expense: Dict[str, Any], score: float) -> str:
    """Generate rationale text for payment priority"""
    priority_level = _get_priority_level(score)
    
    if priority_level == "Must Pay":
        return f"Critical payment for {expense['category']} with high business impact; {expense.get('days_until_due', 0)} days until due"
    elif priority_level == "Should Pay":
        return f"Important vendor relationship; {expense.get('urgency', 'medium')} urgency with {expense.get('days_until_due', 0)} days until due"
    elif priority_level == "Can Defer":
        return f"Non-critical expense that can be deferred if needed; {expense.get('days_until_due', 0)} days until due"
    else:
        return f"Low priority discretionary expense; consider deferring payment"

# ---------------------- Revenue Leak Detection ----------------------

def detect_revenue_leaks() -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect revenue leaks across multiple business areas.
    
    Leak detection areas:
    - Pricing Gaps vs. market
    - Scope Creep: jobs > estimates without change orders
    - Collection Leakage: uncollected deductibles
    - Technician Productivity: low billable hours
    - Equipment Downtime
    - Rework Costs
    
    Returns:
        Dictionary with revenue leak categories and details.
        
    Integration:
        - Add to revenue optimization dashboard
        - Use in financial planning
        - Include in management reports
    """
    with Spinner("Revenue Leak Detection"):
        try:
            leaks = {}
            
            # Pricing Gaps vs. market
            pricing_query = """
            WITH market_rates AS (
                SELECT 
                    job_type,
                    AVG(price_per_sqft) as market_avg_price
                FROM market_rates
                WHERE region = 'current_region'
                GROUP BY job_type
            ),
            company_rates AS (
                SELECT 
                    job_type,
                    AVG(total_revenue / square_footage) as company_avg_price
                FROM projects
                WHERE created_at >= NOW() - INTERVAL '90 days'
                AND square_footage > 0
                GROUP BY job_type
            )
            SELECT 
                c.job_type,
                c.company_avg_price,
                m.market_avg_price,
                (c.company_avg_price - m.market_avg_price) as price_gap,
                (c.company_avg_price - m.market_avg_price) / m.market_avg_price * 100 as price_gap_pct
            FROM company_rates c
            JOIN market_rates m ON c.job_type = m.job_type
            WHERE (c.company_avg_price - m.market_avg_price) / m.market_avg_price * 100 < -5
            """
            
            # Placeholder values
            pricing_gaps = [
                {"job_type": "water", "company_avg_price": 3.75, "market_avg_price": 4.25, "price_gap": -0.50, "price_gap_pct": -11.8},
                {"job_type": "mold", "company_avg_price": 8.50, "market_avg_price": 9.25, "price_gap": -0.75, "price_gap_pct": -8.1}
            ]
            
            if pricing_gaps:
                leaks["pricing_gaps"] = {
                    "leaks": pricing_gaps,
                    "total_impact": sum(pg["price_gap"] * 1000 for pg in pricing_gaps),  # Assuming 1000 sqft average job
                    "action": "Review pricing strategy for underpriced job types"
                }
            
            # Scope Creep
            scope_query = """
            SELECT 
                p.id as project_id,
                p.name as project_name,
                p.total_revenue as current_revenue,
                e.estimated_amount as original_estimate,
                (p.total_revenue - e.estimated_amount) as scope_diff,
                (p.total_revenue - e.estimated_amount) / e.estimated_amount * 100 as scope_diff_pct,
                COUNT(co.id) as change_order_count,
                SUM(co.amount) as change_order_total
            FROM projects p
            JOIN estimates e ON p.id = e.project_id
            LEFT JOIN change_orders co ON p.id = co.project_id
            WHERE p.status IN ('in_progress', 'completed')
            AND p.created_at >= NOW() - INTERVAL '90 days'
            GROUP BY p.id, p.name, p.total_revenue, e.estimated_amount
            HAVING (p.total_revenue - e.estimated_amount) > 0
            AND (SUM(co.amount) IS NULL OR (p.total_revenue - e.estimated_amount) > SUM(co.amount))
            """
            
            # Placeholder values
            scope_creep = [
                {
                    "project_id": 1235, "project_name": "Thompson Basement Restoration", 
                    "current_revenue": 12500, "original_estimate": 9800,
                    "scope_diff": 2700, "scope_diff_pct": 27.6,
                    "change_order_count": 1, "change_order_total": 1200
                },
                {
                    "project_id": 1242, "project_name": "Hill Kitchen Remediation", 
                    "current_revenue": 18750, "original_estimate": 15500,
                    "scope_diff": 3250, "scope_diff_pct": 21.0,
                    "change_order_count": 0, "change_order_total": 0
                }
            ]
            
            if scope_creep:
                leaks["scope_creep"] = {
                    "leaks": scope_creep,
                    "total_impact": sum(
                        sc["scope_diff"] - sc.get("change_order_total", 0) 
                        for sc in scope_creep
                    ),
                    "action": "Implement proper change order documentation for all scope changes"
                }
            
            # Collection Leakage (uncollected deductibles)
            deductible_query = """
            SELECT 
                p.id as project_id,
                p.name as project_name,
                p.insurance_deductible as deductible_amount,
                SUM(CASE WHEN c.type = 'deductible' THEN c.amount ELSE 0 END) as collected_deductible,
                p.insurance_deductible - SUM(CASE WHEN c.type = 'deductible' THEN c.amount ELSE 0 END) as uncollected_amount
            FROM projects p
            LEFT JOIN collections c ON p.id = c.project_id
            WHERE p.insurance_carrier IS NOT NULL
            AND p.status = 'completed'
            AND p.created_at >= NOW() - INTERVAL '180 days'
            GROUP BY p.id, p.name, p.insurance_deductible
            HAVING p.insurance_deductible > SUM(CASE WHEN c.type = 'deductible' THEN c.amount ELSE 0 END)
            """
            
            # Placeholder values
            deductible_leakage = [
                {
                    "project_id": 1228, "project_name": "Davis Water Damage",
                    "deductible_amount": 1000, "collected_deductible": 0, "uncollected_amount": 1000
                },
                {
                    "project_id": 1230, "project_name": "Wilson Fire Remediation",
                    "deductible_amount": 2500, "collected_deductible": 1000, "uncollected_amount": 1500
                }
            ]
            
            if deductible_leakage:
                leaks["deductible_leakage"] = {
                    "leaks": deductible_leakage,
                    "total_impact": sum(dl["uncollected_amount"] for dl in deductible_leakage),
                    "action": "Implement upfront deductible collection at project start"
                }
            
            # Technician Productivity
            productivity_query = """
            WITH tech_benchmarks AS (
                SELECT 
                    job_type,
                    AVG(billable_hours / total_hours) as benchmark_productivity
                FROM job_time_tracking
                WHERE created_at >= NOW() - INTERVAL '180 days'
                GROUP BY job_type
            ),
            tech_productivity AS (
                SELECT 
                    t.id as tech_id,
                    t.name as tech_name,
                    j.job_type,
                    SUM(jt.billable_hours) as billable_hours,
                    SUM(jt.total_hours) as total_hours,
                    SUM(jt.billable_hours) / NULLIF(SUM(jt.total_hours), 0) as productivity_rate
                FROM technicians t
                JOIN job_time_tracking jt ON t.id = jt.tech_id
                JOIN jobs j ON jt.job_id = j.id
                WHERE jt.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY t.id, t.name, j.job_type
            )
            SELECT 
                tp.tech_id,
                tp.tech_name,
                tp.job_type,
                tp.billable_hours,
                tp.total_hours,
                tp.productivity_rate,
                tb.benchmark_productivity,
                (tp.productivity_rate - tb.benchmark_productivity) as productivity_gap,
                (tp.total_hours - tp.billable_hours) * labor_rate as unbilled_value
            FROM tech_productivity tp
            JOIN tech_benchmarks tb ON tp.job_type = tb.job_type
            JOIN labor_rates lr ON tp.job_type = lr.job_type
            WHERE (tp.productivity_rate - tb.benchmark_productivity) < -0.15
            """
            
            # Placeholder values
            productivity_leakage = [
                {
                    "tech_id": 12, "tech_name": "John Smith", "job_type": "water",
                    "billable_hours": 120, "total_hours": 180, "productivity_rate": 0.67,
                    "benchmark_productivity": 0.85, "productivity_gap": -0.18,
                    "unbilled_value": 3600
                },
                {
                    "tech_id": 15, "tech_name": "Robert Johnson", "job_type": "fire",
                    "billable_hours": 95, "total_hours": 140, "productivity_rate": 0.68,
                    "benchmark_productivity": 0.85, "productivity_gap": -0.17,
                    "unbilled_value": 2700
                }
            ]
            
            if productivity_leakage:
                leaks["productivity_leakage"] = {
                    "leaks": productivity_leakage,
                    "total_impact": sum(pl["unbilled_value"] for pl in productivity_leakage),
                    "action": "Provide training on time tracking and implement productivity incentives"
                }
            
            # Equipment Downtime
            equipment_query = """
            SELECT 
                e.id as equipment_id,
                e.name as equipment_name,
                e.daily_rate as rental_rate,
                SUM(d.downtime_hours) as total_downtime_hours,
                COUNT(DISTINCT d.date) as downtime_days,
                SUM(d.downtime_hours) / 8.0 * e.daily_rate as downtime_cost
            FROM equipment e
            JOIN equipment_downtime d ON e.id = d.equipment_id
            WHERE d.date >= NOW() - INTERVAL '90 days'
            GROUP BY e.id, e.name, e.daily_rate
            HAVING SUM(d.downtime_hours) > 24
            """
            
            # Placeholder values
            equipment_leakage = [
                {
                    "equipment_id": 5, "equipment_name": "Large Dehumidifier", "rental_rate": 150,
                    "total_downtime_hours": 48, "downtime_days": 6, "downtime_cost": 900
                },
                {
                    "equipment_id": 8, "equipment_name": "Air Scrubber XL", "rental_rate": 125,
                    "total_downtime_hours": 36, "downtime_days": 5, "downtime_cost": 563
                }
            ]
            
            if equipment_leakage:
                leaks["equipment_leakage"] = {
                    "leaks": equipment_leakage,
                    "total_impact": sum(el["downtime_cost"] for el in equipment_leakage),
                    "action": "Implement preventative maintenance program and equipment rotation strategy"
                }
            
            # Rework Costs
            rework_query = """
            SELECT 
                p.id as project_id,
                p.name as project_name,
                SUM(r.labor_hours) as rework_hours,
                SUM(r.material_cost) as rework_materials,
                SUM(r.labor_hours) * labor_rate + SUM(r.material_cost) as total_rework_cost,
                r.reason
            FROM projects p
            JOIN rework r ON p.id = r.project_id
            WHERE p.created_at >= NOW() - INTERVAL '90 days'
            GROUP BY p.id, p.name, r.reason
            """
            
            # Placeholder values
            rework_leakage = [
                {
                    "project_id": 1237, "project_name": "Garcia Mold Remediation",
                    "rework_hours": 12, "rework_materials": 350,
                    "total_rework_cost": 950, "reason": "Incomplete moisture removal"
                },
                {
                    "project_id": 1240, "project_name": "Anderson Fire Restoration",
                    "rework_hours": 8, "rework_materials": 275,
                    "total_rework_cost": 675, "reason": "Improper odor treatment"
                }
            ]
            
            if rework_leakage:
                leaks["rework_leakage"] = {
                    "leaks": rework_leakage,
                    "total_impact": sum(rl["total_rework_cost"] for rl in rework_leakage),
                    "action": "Review quality control process and implement training for common rework issues"
                }
            
            # Calculate total impact across all leak categories
            total_leak_impact = sum(
                category["total_impact"] 
                for category in leaks.values() 
                if "total_impact" in category
            )
            
            # Return comprehensive leak detection results
            return {
                "leak_categories": leaks,
                "total_leak_impact": total_leak_impact,
                "priority_fixes": [
                    {"category": cat, "impact": data["total_impact"], "action": data["action"]}
                    for cat, data in sorted(
                        leaks.items(), 
                        key=lambda item: item[1].get("total_impact", 0), 
                        reverse=True
                    )
                ]
            }
        
        except Exception as e:
            handle_error(f"Failed to detect revenue leaks: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to detect revenue leaks: {str(e)}")

# ---------------------- Smart Alert Framework ----------------------

def trigger_red_flag():
    """
    Trigger Red Flag alert for critical situations.
    Red Flag: <5 days runway + >$10K unpaid payroll
    
    Returns:
        Alert details if conditions are met, None otherwise.
    """
    with Spinner("Red Flag Check"):
        try:
            # Query for cash runway
            cash_query = """
            WITH daily_burn AS (
                SELECT 
                    AVG(amount) as daily_expense
                FROM expenses
                WHERE status = 'paid'
                AND paid_date >= NOW() - INTERVAL '30 days'
            ),
            current_cash AS (
                SELECT 
                    balance
                FROM cash_balances
                ORDER BY as_of_date DESC, id DESC
                LIMIT 1
            )
            SELECT 
                c.balance as current_cash,
                d.daily_expense,
                c.balance / NULLIF(d.daily_expense, 0) as runway_days
            FROM current_cash c, daily_burn d
            """
            
            # Query for unpaid payroll
            payroll_query = """
            SELECT 
                SUM(amount) as unpaid_payroll
            FROM expenses
            WHERE category = 'payroll'
            AND status = 'pending'
            AND due_date <= NOW() + INTERVAL '5 days'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            current_cash = 15000       # $15K current cash
            daily_expense = 4000       # $4K daily burn rate
            runway_days = current_cash / daily_expense if daily_expense > 0 else 0
            
            unpaid_payroll = 12000     # $12K unpaid payroll
            
            if runway_days < 5 and unpaid_payroll > 10000:
                return {
                    "alert_type": "red_flag",
                    "message": f"CRITICAL: Cash runway of {runway_days:.1f} days with ${unpaid_payroll:,.2f} in unpaid payroll",
                    "severity": 10,
                    "action": "Immediate action required: Accelerate collections, delay non-critical payments, arrange emergency funding",
                    "details": {
                        "current_cash": current_cash,
                        "daily_expense": daily_expense,
                        "runway_days": runway_days,
                        "unpaid_payroll": unpaid_payroll,
                        "due_date": (datetime.now() + timedelta(days=5)).isoformat()
                    }
                }
            
            return None
        
        except Exception as e:
            handle_error(f"Failed to check red flag conditions: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to check red flag conditions: {str(e)}")

def trigger_yellow_warning():
    """
    Trigger Yellow Warning alert for concerning situations.
    Yellow Warning: CAC >30% MoM + CLV stable
    
    Returns:
        Alert details if conditions are met, None otherwise.
    """
    with Spinner("Yellow Warning Check"):
        try:
            # Query for CAC and CLV trends
            query = """
            WITH current_month AS (
                SELECT 
                    AVG(lead_cost) as avg_cac,
                    COUNT(*) as lead_count,
                    (
                        AVG(total_revenue) * 
                        AVG((total_revenue - total_expenses - allocated_lead_cost) / total_revenue) * 
                        3  -- assuming 3 year customer relationship
                    ) as avg_clv
                FROM leads l
                LEFT JOIN projects p ON l.id = p.lead_id
                WHERE l.created_at >= DATE_TRUNC('month', NOW())
            ),
            previous_month AS (
                SELECT 
                    AVG(lead_cost) as avg_cac,
                    COUNT(*) as lead_count,
                    (
                        AVG(total_revenue) * 
                        AVG((total_revenue - total_expenses - allocated_lead_cost) / total_revenue) * 
                        3  -- assuming 3 year customer relationship
                    ) as avg_clv
                FROM leads l
                LEFT JOIN projects p ON l.id = p.lead_id
                WHERE l.created_at BETWEEN DATE_TRUNC('month', NOW() - INTERVAL '1 month') 
                                        AND DATE_TRUNC('month', NOW())
            )
            SELECT 
                cm.avg_cac as current_cac,
                pm.avg_cac as previous_cac,
                (cm.avg_cac - pm.avg_cac) / pm.avg_cac * 100 as cac_change_pct,
                cm.avg_clv as current_clv,
                pm.avg_clv as previous_clv,
                (cm.avg_clv - pm.avg_clv) / pm.avg_clv * 100 as clv_change_pct
            FROM current_month cm, previous_month pm
            """
            
            # TODO: Implement the actual database call
            # For now, we'll use placeholder values
            current_cac = 380          # $380 current CAC
            previous_cac = 290         # $290 previous CAC
            cac_change_pct = ((current_cac - previous_cac) / previous_cac * 100) if previous_cac > 0 else 0
            
            current_clv = 3100         # $3100 current CLV
            previous_clv = 3050        # $3050 previous CLV
            clv_change_pct = ((current_clv - previous_clv) / previous_clv * 100) if previous_clv > 0 else 0
            
            if cac_change_pct > 30 and abs(clv_change_pct) < 5:
                return {
                    "alert_type": "yellow_warning",
                    "message": f"WARNING: CAC increased by {cac_change_pct:.1f}% while CLV remained stable ({clv_change_pct:.1f}%)",
                    "severity": 7,
                    "action": "Review marketing spend and lead sources; evaluate lead qualification process",
                    "details": {
                        "current_cac": current_cac,
                        "previous_cac": previous_cac,
                        "cac_change_pct": cac_change_pct,
                        "current_clv": current_clv,
                        "previous_clv": previous_clv,
                        "clv_change_pct": clv_change_pct
                    }
                }
            
            return None
        
        except Exception as e:
            handle_error(f"Failed to check yellow warning conditions: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to check yellow warning conditions: {str(e)}")

def trigger_strategy_drift():
    """
    Trigger Strategy Drift alert for long-term concerns.
    Strategy Drift: Revenue CAGR < target for 3 months
    
    Returns:
        Alert details if conditions are met, None otherwise.
    """
    with Spinner("Strategy Drift Check"):
        try:
            # Query for revenue CAGR
            query = """
            WITH monthly_revenue AS (
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    SUM(total_revenue) as monthly_revenue
                FROM projects
                WHERE created_at >= NOW() - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', created_at)
                ORDER BY DATE_TRUNC('month', created_at)
            ),
            monthly_cagr AS (
                SELECT 
                    month,
                    monthly_revenue,
                    LAG(monthly_revenue, 12) OVER (ORDER BY month) as year_ago_revenue,
                    POWER(monthly_revenue / NULLIF(LAG(monthly_revenue, 12) OVER (ORDER BY month), 0), 1/1.0) - 1 as annual_growth_rate
                FROM monthly_revenue
            )
            SELECT 
                month,
                annual_growth_rate,
                20 as target_growth_rate,
                annual_growth_rate < 20 as below_target
            FROM monthly_cagr
            WHERE month > NOW() - INTERVAL '3 months'
            ORDER BY month DESC
            """
            
            # TODO: Implement the actual database call
            # For now, we'll use placeholder values
            monthly_growth_rates = [
                {"month": "2023-05-01", "annual_growth_rate": 18.5, "target_growth_rate": 20, "below_target": True},
                {"month": "2023-04-01", "annual_growth_rate": 17.8, "target_growth_rate": 20, "below_target": True},
                {"month": "2023-03-01", "annual_growth_rate": 19.2, "target_growth_rate": 20, "below_target": True}
            ]
            
            # Check if we have 3 consecutive months below target
            consecutive_below_target = all(rate["below_target"] for rate in monthly_growth_rates)
            
            if consecutive_below_target:
                return {
                    "alert_type": "strategy_drift",
                    "message": f"STRATEGY ALERT: Revenue CAGR below {monthly_growth_rates[0]['target_growth_rate']}% target for 3+ consecutive months",
                    "severity": 6,
                    "action": "Schedule strategy review session; evaluate market positioning and growth initiatives",
                    "details": {
                        "monthly_growth_rates": monthly_growth_rates,
                        "average_growth_rate": sum(rate["annual_growth_rate"] for rate in monthly_growth_rates) / len(monthly_growth_rates),
                        "target_rate": monthly_growth_rates[0]["target_growth_rate"],
                        "months_below_target": len(monthly_growth_rates)
                    }
                }
            
            return None
        
        except Exception as e:
            handle_error(f"Failed to check strategy drift conditions: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to check strategy drift conditions: {str(e)}")

def trigger_ops_breach():
    """
    Trigger Operations Breach alert for process breakdowns.
    Ops Breach: >10% jobs missing docs
    
    Returns:
        Alert details if conditions are met, None otherwise.
    """
    with Spinner("Operations Breach Check"):
        try:
            # Query for missing documentation
            query = """
            SELECT 
                COUNT(*) as total_projects,
                COUNT(CASE WHEN contract_uploaded_at IS NULL THEN 1 END) as missing_contract,
                COUNT(CASE WHEN inspection_report_id IS NULL THEN 1 END) as missing_inspection,
                COUNT(CASE WHEN approval_document_id IS NULL THEN 1 END) as missing_approval,
                COUNT(CASE WHEN 
                    contract_uploaded_at IS NULL OR 
                    inspection_report_id IS NULL OR 
                    approval_document_id IS NULL 
                THEN 1 END) as missing_any_doc,
                COUNT(CASE WHEN 
                    contract_uploaded_at IS NULL OR 
                    inspection_report_id IS NULL OR 
                    approval_document_id IS NULL 
                THEN 1 END) * 100.0 / COUNT(*) as missing_doc_percentage
            FROM projects
            WHERE status IN ('in_progress', 'completed')
            AND created_at >= NOW() - INTERVAL '30 days'
            """
            
            # TODO: Implement the actual database call
            # For now, we'll use placeholder values
            total_projects = 45
            missing_contract = 3
            missing_inspection = 5
            missing_approval = 2
            missing_any_doc = 8  # Some projects might be missing multiple docs
            missing_doc_percentage = (missing_any_doc / total_projects * 100) if total_projects > 0 else 0
            
            if missing_doc_percentage > 10:
                return {
                    "alert_type": "ops_breach",
                    "message": f"OPERATIONS ALERT: {missing_doc_percentage:.1f}% of recent projects missing required documentation",
                    "severity": 7,
                    "action": "Review documentation process; assign responsibility for resolving backlog",
                    "details": {
                        "total_projects": total_projects,
                        "missing_contract": missing_contract,
                        "missing_inspection": missing_inspection,
                        "missing_approval": missing_approval,
                        "missing_any_doc": missing_any_doc,
                        "missing_doc_percentage": missing_doc_percentage,
                        "threshold": 10
                    }
                }
            
            return None
        
        except Exception as e:
            handle_error(f"Failed to check operations breach conditions: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to check operations breach conditions: {str(e)}")

def trigger_payment_advisory():
    """
    Trigger Payment Advisory alert for cash flow warnings.
    Payment Advisory: AP > AR for 2 weeks + cash < $25K
    
    Returns:
        Alert details if conditions are met, None otherwise.
    """
    with Spinner("Payment Advisory Check"):
        try:
            # Query for AP vs AR and cash position
            query = """
            WITH weekly_ap_ar AS (
                SELECT 
                    date_trunc('week', due_date) as week,
                    SUM(amount) as weekly_ap
                FROM expenses
                WHERE status = 'pending'
                AND due_date >= NOW() - INTERVAL '4 weeks'
                GROUP BY date_trunc('week', due_date)
            ),
            weekly_ar AS (
                SELECT 
                    date_trunc('week', expected_date) as week,
                    SUM(amount) as weekly_ar
                FROM collections
                WHERE status = 'pending'
                AND expected_date >= NOW() - INTERVAL '4 weeks'
                GROUP BY date_trunc('week', expected_date)
            ),
            ap_ar_comparison AS (
                SELECT 
                    ap.week,
                    ap.weekly_ap,
                    ar.weekly_ar,
                    (ap.weekly_ap > ar.weekly_ar) as ap_exceeds_ar
                FROM weekly_ap_ar ap
                JOIN weekly_ar ar ON ap.week = ar.week
            ),
            cash_position AS (
                SELECT 
                    balance as current_cash
                FROM cash_balances
                ORDER BY as_of_date DESC, id DESC
                LIMIT 1
            )
            SELECT 
                c.current_cash,
                COUNT(CASE WHEN a.ap_exceeds_ar THEN 1 END) as weeks_ap_exceeds_ar
            FROM cash_position c
            CROSS JOIN (
                SELECT COUNT(CASE WHEN ap_exceeds_ar THEN 1 END) as weeks_ap_exceeds_ar
                FROM ap_ar_comparison
                WHERE week >= NOW() - INTERVAL '2 weeks'
            ) a
            """
            
            # TODO: Implement the actual database call
            # For now, we'll use placeholder values
            current_cash = 22500       # $22.5K current cash
            weeks_ap_exceeds_ar = 2    # AP > AR for 2 weeks
            
            if weeks_ap_exceeds_ar >= 2 and current_cash < 25000:
                return {
                    "alert_type": "payment_advisory",
                    "message": f"PAYMENT ADVISORY: AP exceeds AR for {weeks_ap_exceeds_ar} consecutive weeks with cash balance of ${current_cash:,.2f}",
                    "severity": 8,
                    "action": "Prioritize incoming payments; consider delaying non-critical AP",
                    "details": {
                        "current_cash": current_cash,
                        "weeks_ap_exceeds_ar": weeks_ap_exceeds_ar,
                        "cash_threshold": 25000
                    }
                }
            
            return None
        
        except Exception as e:
            handle_error(f"Failed to check payment advisory conditions: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to check payment advisory conditions: {str(e)}")

def get_all_alerts() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all alerts from all alert triggers.
    
    Returns:
        Dictionary with categorized alerts.
        
    Integration:
        - Add to executive dashboard
        - Use in daily management review
        - Include in operational planning
    """
    with Spinner("Smart Alerts"):
        try:
            alerts = {
                "red_flags": [],
                "yellow_warnings": [],
                "strategic_alerts": [],
                "operational_alerts": [],
                "financial_alerts": []
            }
            
            # Check each alert type
            red_flag = trigger_red_flag()
            if red_flag:
                alerts["red_flags"].append(red_flag)
            
            yellow_warning = trigger_yellow_warning()
            if yellow_warning:
                alerts["yellow_warnings"].append(yellow_warning)
            
            strategy_drift = trigger_strategy_drift()
            if strategy_drift:
                alerts["strategic_alerts"].append(strategy_drift)
            
            ops_breach = trigger_ops_breach()
            if ops_breach:
                alerts["operational_alerts"].append(ops_breach)
            
            payment_advisory = trigger_payment_advisory()
            if payment_advisory:
                alerts["financial_alerts"].append(payment_advisory)
            
            # Add standard red and yellow alerts
            red_alerts = check_red_alerts()
            yellow_warnings = check_yellow_warnings()
            
            alerts["red_flags"].extend(red_alerts)
            alerts["yellow_warnings"].extend(yellow_warnings)
            
            # Get all revenue leaks as operational alerts
            try:
                revenue_leaks = detect_revenue_leaks()
                if revenue_leaks and "priority_fixes" in revenue_leaks:
                    for fix in revenue_leaks["priority_fixes"]:
                        alerts["operational_alerts"].append({
                            "alert_type": "revenue_leak",
                            "message": f"Revenue leak detected in {fix['category']}: ${fix['impact']:,.2f} impact",
                            "severity": 7 if fix["impact"] > 5000 else 6,
                            "action": fix["action"],
                            "details": {
                                "category": fix["category"],
                                "impact": fix["impact"]
                            }
                        })
            except Exception as e:
                handle_error(f"Failed to process revenue leaks: {str(e)}", "alert_framework")
            
            # Add counts to the response
            total_alerts = sum(len(alert_list) for alert_list in alerts.values())
            highest_severity = max(
                [alert["severity"] for alert_list in alerts.values() for alert in alert_list],
                default=0
            )
            
            return {
                "alerts": alerts,
                "total_alerts": total_alerts,
                "highest_severity": highest_severity,
                "alert_counts": {
                    category: len(alert_list)
                    for category, alert_list in alerts.items()
                },
                "has_critical_alerts": highest_severity >= 9,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            handle_error(f"Failed to get all alerts: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to get all alerts: {str(e)}")

# ---------------------- Additional Predictive Functions ----------------------

def simulate_collections_probability():
    """
    Simulate collections probability using historical payment patterns.
    
    Returns:
        Dictionary with collection probability simulation results.
        
    Integration:
        - Add to collections dashboard
        - Use in cash flow forecasting
        - Include in financial planning
    """
    with Spinner("Collections Probability Simulation"):
        try:
            # This would be a more complex simulation based on historical data
            # For now, we'll return a placeholder implementation
            
            # Placeholder values for demo
            pending_collections = [
                {"id": 101, "amount": 12500, "expected_date": "2023-06-15", "probability": 0.95},
                {"id": 102, "amount": 8750, "expected_date": "2023-06-22", "probability": 0.85},
                {"id": 103, "amount": 15000, "expected_date": "2023-06-30", "probability": 0.75},
                {"id": 104, "amount": 9500, "expected_date": "2023-07-07", "probability": 0.65},
                {"id": 105, "amount": 11250, "expected_date": "2023-07-15", "probability": 0.55}
            ]
            
            # Calculate expected value (amount * probability)
            for collection in pending_collections:
                collection["expected_value"] = collection["amount"] * collection["probability"]
            
            # Calculate totals
            total_pending = sum(c["amount"] for c in pending_collections)
            total_expected = sum(c["expected_value"] for c in pending_collections)
            
            # Simple Monte Carlo simulation for range of outcomes
            num_trials = 1000
            simulated_totals = []
            
            np.random.seed(42)  # For reproducibility
            for _ in range(num_trials):
                trial_total = 0
                for collection in pending_collections:
                    # Simulate whether this collection comes in
                    if np.random.random() < collection["probability"]:
                        trial_total += collection["amount"]
                simulated_totals.append(trial_total)
            
            # Calculate percentiles
            p10 = np.percentile(simulated_totals, 10)
            p50 = np.percentile(simulated_totals, 50)
            p90 = np.percentile(simulated_totals, 90)
            
            return {
                "pending_collections": pending_collections,
                "total_pending": total_pending,
                "expected_collection": total_expected,
                "collection_ratio": (total_expected / total_pending) if total_pending > 0 else 0,
                "simulation_results": {
                    "p10": p10,
                    "p50": p50,
                    "p90": p90,
                    "min": min(simulated_totals),
                    "max": max(simulated_totals)
                }
            }
        
        except Exception as e:
            handle_error(f"Failed to simulate collections probability: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to simulate collections probability: {str(e)}")

def calculate_realtime_breakeven():
    """
    Calculate real-time breakeven point based on current business metrics.
    
    Returns:
        Dictionary with breakeven analysis results.
        
    Integration:
        - Add to financial dashboard
        - Use in pricing strategy
        - Include in operational planning
    """
    with Spinner("Realtime Breakeven Analysis"):
        try:
            # Query for fixed and variable costs
            fixed_cost_query = """
            SELECT 
                SUM(amount) as monthly_fixed_costs
            FROM expenses
            WHERE category IN ('rent', 'insurance', 'salaries', 'software', 'utilities')
            AND is_recurring = true
            AND created_at >= NOW() - INTERVAL '30 days'
            """
            
            variable_cost_query = """
            WITH job_costs AS (
                SELECT 
                    p.id as project_id,
                    p.total_revenue as revenue,
                    p.total_expenses as direct_expenses,
                    p.total_expenses / NULLIF(p.total_revenue, 0) as variable_cost_ratio
                FROM projects p
                WHERE p.status = 'completed'
                AND p.created_at >= NOW() - INTERVAL '90 days'
            )
            SELECT 
                AVG(variable_cost_ratio) as avg_variable_cost_ratio
            FROM job_costs
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            monthly_fixed_costs = 65000  # $65K monthly fixed costs
            avg_variable_cost_ratio = 0.6  # 60% variable costs
            
            # Calculate breakeven
            contribution_margin_ratio = 1 - avg_variable_cost_ratio
            breakeven_revenue = monthly_fixed_costs / contribution_margin_ratio if contribution_margin_ratio > 0 else float('inf')
            
            # Calculate current position
            current_monthly_revenue_query = """
            SELECT 
                SUM(total_revenue) as monthly_revenue
            FROM projects
            WHERE created_at >= NOW() - INTERVAL '30 days'
            """
            
            # Placeholder value
            current_monthly_revenue = 120000  # $120K monthly revenue
            
            # Calculate metrics
            margin_of_safety = current_monthly_revenue - breakeven_revenue
            margin_of_safety_percentage = (margin_of_safety / current_monthly_revenue * 100) if current_monthly_revenue > 0 else 0
            
            # Calculate daily breakeven
            business_days_per_month = 22  # Approximate
            daily_breakeven = breakeven_revenue / business_days_per_month
            
            return {
                "monthly_fixed_costs": monthly_fixed_costs,
                "variable_cost_ratio": avg_variable_cost_ratio,
                "contribution_margin_ratio": contribution_margin_ratio,
                "breakeven_revenue": {
                    "monthly": breakeven_revenue,
                    "daily": daily_breakeven
                },
                "current_position": {
                    "monthly_revenue": current_monthly_revenue,
                    "margin_of_safety": margin_of_safety,
                    "margin_of_safety_percentage": margin_of_safety_percentage,
                    "is_profitable": current_monthly_revenue > breakeven_revenue
                }
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate realtime breakeven: {str(e)}", "alert_framework")
            raise RuntimeError(f"Failed to calculate realtime breakeven: {str(e)}")