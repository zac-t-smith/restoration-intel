"""
Growth Accelerator Module

This module implements growth acceleration insights and strategies for the Restoration CRM.
"""

import os
import json
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import utils for consistent error handling
from api.py.utils import handle_error, Spinner, safe_divide

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
            handle_error(f"API error: {response.text}", "growth_accelerator")
            raise RuntimeError(f"Supabase RPC failed: {response.status_code}")
        return response.json()

async def _get_unconverted_leads() -> List[Dict]:
    """Find leads that haven't been converted after a certain period"""
    try:
        query = """
        SELECT 
            id, name, email, lead_source, lead_cost, created_at,
            NOW() - created_at as age
        FROM 
            leads
        WHERE 
            status = 'contacted'
            AND created_at < (NOW() - INTERVAL '14 days')
        ORDER BY 
            created_at ASC
        LIMIT 10
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for lead in results:
            days_old = (datetime.now() - datetime.fromisoformat(lead["created_at"].replace("Z", "+00:00"))).days
            insights.append({
                "type": "unconverted_lead",
                "category": "revenue_leak",
                "priority": "high" if days_old > 30 else "medium",
                "data": lead,
                "title": f"Unconverted Lead: {lead['name']}",
                "description": f"Lead is {days_old} days old and still in 'contacted' status",
                "recommended_action": "Follow up immediately and offer incentive for closure",
                "potential_value": lead["lead_cost"] * 3  # Assuming 3x ROI on lead cost
            })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get unconverted leads: {str(e)}", "growth_accelerator")
        return []

async def _get_paused_projects() -> List[Dict]:
    """Identify projects on hold for too long"""
    try:
        query = """
        SELECT 
            p.id, p.name, p.total_revenue, p.status, p.created_at,
            c.name as customer_name
        FROM 
            projects p
        JOIN 
            customers c ON p.customer_id = c.id
        WHERE 
            p.status = 'on_hold'
            AND p.updated_at < (NOW() - INTERVAL '14 days')
        ORDER BY 
            p.updated_at ASC
        LIMIT 10
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for project in results:
            days_paused = (datetime.now() - datetime.fromisoformat(project["created_at"].replace("Z", "+00:00"))).days
            insights.append({
                "type": "paused_project",
                "category": "revenue_leak",
                "priority": "high" if project["total_revenue"] > 10000 else "medium",
                "data": project,
                "title": f"Paused Project: {project['name']}",
                "description": f"Project has been on hold for {days_paused} days",
                "recommended_action": "Contact customer to discuss resuming work",
                "potential_value": project["total_revenue"] * 0.5  # Assuming 50% of revenue still collectible
            })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get paused projects: {str(e)}", "growth_accelerator")
        return []

async def _get_underbilled_invoices() -> List[Dict]:
    """Find projects where invoiced amount is less than total revenue"""
    try:
        query = """
        SELECT 
            p.id, p.name, p.total_revenue, 
            c.name as customer_name,
            COALESCE(SUM(col.amount), 0) as invoiced_amount
        FROM 
            projects p
        JOIN 
            customers c ON p.customer_id = c.id
        LEFT JOIN 
            collections col ON p.id = col.project_id
        WHERE 
            p.status IN ('in_progress', 'completed')
        GROUP BY 
            p.id, p.name, p.total_revenue, c.name
        HAVING 
            COALESCE(SUM(col.amount), 0) < p.total_revenue * 0.9
        ORDER BY 
            (p.total_revenue - COALESCE(SUM(col.amount), 0)) DESC
        LIMIT 10
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for project in results:
            unbilled_amount = project["total_revenue"] - project["invoiced_amount"]
            insights.append({
                "type": "underbilled_invoice",
                "category": "revenue_leak",
                "priority": "high" if unbilled_amount > 5000 else "medium",
                "data": project,
                "title": f"Underbilled Project: {project['name']}",
                "description": f"${unbilled_amount:.2f} of revenue not yet invoiced",
                "recommended_action": "Review project and create remaining invoices",
                "potential_value": unbilled_amount
            })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get underbilled invoices: {str(e)}", "growth_accelerator")
        return []

async def _get_overdue_collections() -> List[Dict]:
    """Identify overdue payments"""
    try:
        query = """
        SELECT 
            col.id, col.amount, col.expected_date, col.description,
            p.id as project_id, p.name as project_name,
            c.name as customer_name
        FROM 
            collections col
        JOIN 
            projects p ON col.project_id = p.id
        JOIN 
            customers c ON p.customer_id = c.id
        WHERE 
            col.status = 'pending'
            AND col.expected_date < NOW()
        ORDER BY 
            col.expected_date ASC
        LIMIT 10
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for collection in results:
            days_overdue = (datetime.now() - datetime.fromisoformat(collection["expected_date"].replace("Z", "+00:00"))).days
            insights.append({
                "type": "overdue_collection",
                "category": "revenue_leak",
                "priority": "high" if days_overdue > 30 or collection["amount"] > 10000 else "medium",
                "data": collection,
                "title": f"Overdue Payment: {collection['description']}",
                "description": f"Payment of ${collection['amount']:.2f} is {days_overdue} days overdue",
                "recommended_action": "Contact customer immediately and offer payment plan if needed",
                "potential_value": collection["amount"]
            })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get overdue collections: {str(e)}", "growth_accelerator")
        return []

async def _get_late_projects() -> List[Dict]:
    """Find projects past their estimated completion date"""
    try:
        query = """
        SELECT 
            p.id, p.name, p.total_revenue, p.estimated_completion,
            c.name as customer_name
        FROM 
            projects p
        JOIN 
            customers c ON p.customer_id = c.id
        WHERE 
            p.status = 'in_progress'
            AND p.estimated_completion < NOW()
        ORDER BY 
            p.estimated_completion ASC
        LIMIT 10
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for project in results:
            days_late = (datetime.now() - datetime.fromisoformat(project["estimated_completion"].replace("Z", "+00:00"))).days
            insights.append({
                "type": "late_project",
                "category": "operational_bottleneck",
                "priority": "high" if days_late > 14 else "medium",
                "data": project,
                "title": f"Late Project: {project['name']}",
                "description": f"Project is {days_late} days past estimated completion date",
                "recommended_action": "Review project plan and allocate additional resources",
                "potential_value": project["total_revenue"] * 0.1  # Estimate 10% revenue at risk due to delay
            })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get late projects: {str(e)}", "growth_accelerator")
        return []

async def _get_missing_contracts() -> List[Dict]:
    """Identify active projects without uploaded contracts"""
    try:
        query = """
        SELECT 
            p.id, p.name, p.total_revenue, p.status,
            c.name as customer_name
        FROM 
            projects p
        JOIN 
            customers c ON p.customer_id = c.id
        WHERE 
            p.status IN ('signed', 'scheduled', 'in_progress')
            AND (p.contract_path IS NULL OR p.contract_filename IS NULL)
        ORDER BY 
            p.total_revenue DESC
        LIMIT 10
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for project in results:
            insights.append({
                "type": "missing_contract",
                "category": "operational_bottleneck",
                "priority": "high" if project["total_revenue"] > 10000 else "medium",
                "data": project,
                "title": f"Missing Contract: {project['name']}",
                "description": f"Active project worth ${project['total_revenue']:.2f} has no uploaded contract",
                "recommended_action": "Upload signed contract document immediately",
                "potential_value": project["total_revenue"] * 0.25  # Estimate 25% revenue at risk without contract
            })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get missing contracts: {str(e)}", "growth_accelerator")
        return []

async def _get_idle_cash() -> List[Dict]:
    """Detect significant cash sitting idle"""
    try:
        query = """
        SELECT 
            balance, as_of_date
        FROM 
            cash_balances
        ORDER BY 
            as_of_date DESC, id DESC
        LIMIT 1
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        if not results:
            return []
        
        current_balance = results[0]["balance"]
        
        # Get average monthly expenses
        expenses_query = """
        SELECT 
            AVG(monthly_expenses) as avg_monthly_expenses
        FROM (
            SELECT 
                date_trunc('month', created_at) as month,
                SUM(amount) as monthly_expenses
            FROM 
                expenses
            WHERE 
                created_at > (NOW() - INTERVAL '6 months')
            GROUP BY 
                date_trunc('month', created_at)
        ) as monthly
        """
        
        expenses_result = await _call_supabase_rpc("execute_sql", {"query": expenses_query})
        avg_monthly_expenses = expenses_result[0]["avg_monthly_expenses"] or 0
        
        # If cash balance exceeds 3 months of expenses, consider it idle
        if current_balance > avg_monthly_expenses * 3:
            excess_cash = current_balance - (avg_monthly_expenses * 2)  # Keep 2 months as reserve
            insights = [{
                "type": "idle_cash",
                "category": "capital_inefficiency",
                "priority": "medium",
                "data": {"current_balance": current_balance, "avg_monthly_expenses": avg_monthly_expenses},
                "title": "Excess Cash Balance",
                "description": f"${excess_cash:.2f} in excess of 2-month operating reserve",
                "recommended_action": "Consider investing in growth initiatives or equipment",
                "potential_value": excess_cash * 0.05  # Assuming 5% return on investment
            }]
            return insights
        
        return []
    except Exception as e:
        handle_error(f"Failed to get idle cash: {str(e)}", "growth_accelerator")
        return []

async def _get_inefficient_lead_sources() -> List[Dict]:
    """Identify lead sources with poor conversion rates"""
    try:
        query = """
        SELECT 
            lead_source,
            COUNT(*) as total_leads,
            SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) as converted_leads,
            SUM(lead_cost) as total_cost
        FROM 
            leads
        WHERE 
            created_at > (NOW() - INTERVAL '90 days')
        GROUP BY 
            lead_source
        HAVING 
            COUNT(*) >= 5
        ORDER BY 
            (SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END)::float / COUNT(*)) ASC
        LIMIT 5
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for source in results:
            conversion_rate = safe_divide(source["converted_leads"], source["total_leads"]) * 100
            cost_per_conversion = safe_divide(source["total_cost"], source["converted_leads"])
            
            if conversion_rate < 15 or (cost_per_conversion > 500 and source["total_leads"] > 10):
                insights.append({
                    "type": "inefficient_lead_source",
                    "category": "capital_inefficiency",
                    "priority": "high" if source["total_cost"] > 5000 else "medium",
                    "data": source,
                    "title": f"Inefficient Lead Source: {source['lead_source']}",
                    "description": f"{conversion_rate:.1f}% conversion rate, ${cost_per_conversion:.2f} per conversion",
                    "recommended_action": "Reduce spend or optimize landing pages and follow-up process",
                    "potential_value": source["total_cost"] * 0.3  # Potential 30% savings
                })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get inefficient lead sources: {str(e)}", "growth_accelerator")
        return []

async def _get_early_payment_opportunities() -> List[Dict]:
    """Find vendors offering early payment discounts"""
    try:
        query = """
        SELECT 
            v.id, v.name, v.sla_days,
            COUNT(e.id) as expense_count,
            SUM(e.amount) as total_expenses
        FROM 
            vendors v
        JOIN 
            expenses e ON v.id = e.vendor_id
        WHERE 
            e.created_at > (NOW() - INTERVAL '90 days')
        GROUP BY 
            v.id, v.name, v.sla_days
        HAVING 
            SUM(e.amount) > 5000
        ORDER BY 
            SUM(e.amount) DESC
        LIMIT 10
        """
        
        results = await _call_supabase_rpc("execute_sql", {"query": query})
        
        insights = []
        for vendor in results:
            # Assume vendors with sla_days > 15 might offer early payment discounts
            if vendor["sla_days"] > 15:
                potential_discount = vendor["total_expenses"] * 0.02  # Assume 2% discount for early payment
                insights.append({
                    "type": "early_payment_opportunity",
                    "category": "capital_inefficiency",
                    "priority": "medium",
                    "data": vendor,
                    "title": f"Early Payment Opportunity: {vendor['name']}",
                    "description": f"Potential ${potential_discount:.2f} savings with early payment",
                    "recommended_action": "Negotiate early payment discount terms",
                    "potential_value": potential_discount
                })
        
        return insights
    except Exception as e:
        handle_error(f"Failed to get early payment opportunities: {str(e)}", "growth_accelerator")
        return []

async def generate_growth_insights() -> List[Dict[str, Any]]:
    """
    Generate growth insights and opportunities.
    Returns a list of actionable insights with priorities and expected impact.
    """
    try:
        insights = []
        
        # Gather data in parallel
        unconverted_leads, revenue_trends, capacity_data = await asyncio.gather(
            _get_unconverted_leads(),
            _analyze_revenue_trends(),
            _analyze_capacity_utilization()
        )
        
        # Process lead conversion opportunities
        if unconverted_leads:
            insights.append({
                "type": "lead_conversion",
                "title": "Lead Conversion Opportunity",
                "description": f"Found {len(unconverted_leads)} unconverted leads that need attention",
                "priority": "high" if len(unconverted_leads) > 10 else "medium",
                "potential_impact": sum(lead.get("lead_cost", 0) for lead in unconverted_leads),
                "action_items": [
                    "Review lead follow-up process",
                    "Implement automated follow-up sequences",
                    "Assign dedicated sales resources"
                ]
            })
            
        # Process revenue insights
        if revenue_trends:
            insights.extend(analyze_revenue_opportunities(revenue_trends))
            
        # Process capacity insights
        if capacity_data:
            insights.extend(analyze_capacity_opportunities(capacity_data))
            
        return sorted(insights, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
        
    except Exception as e:
        handle_error(f"Error generating growth insights: {str(e)}")
        return []

async def analyze_revenue_opportunities(trends: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze revenue data for growth opportunities"""
    insights = []
    
    try:
        if trends.get("mrr_growth_rate", 0) < 0.05:  # Less than 5% MRR growth
            insights.append({
                "type": "revenue_growth",
                "title": "Revenue Growth Opportunity",
                "description": "MRR growth rate below target threshold",
                "priority": "high",
                "potential_impact": "Increase MRR by 20% through targeted initiatives",
                "action_items": [
                    "Review pricing strategy",
                    "Implement upsell campaigns",
                    "Launch referral program"
                ]
            })
            
        return insights
    except Exception as e:
        handle_error(f"Error analyzing revenue opportunities: {str(e)}")
        return []

async def analyze_capacity_opportunities(capacity: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze capacity utilization for optimization opportunities"""
    insights = []
    
    try:
        utilization = capacity.get("utilization_rate", 0)
        if utilization < 0.75:  # Less than 75% capacity utilization
            insights.append({
                "type": "capacity_optimization",
                "title": "Capacity Optimization Opportunity",
                "description": f"Current capacity utilization at {utilization:.1%}",
                "priority": "medium",
                "potential_impact": "Improve resource utilization by 15-20%",
                "action_items": [
                    "Optimize resource scheduling",
                    "Review team structure and roles",
                    "Implement capacity forecasting"
                ]
            })
            
        return insights
    except Exception as e:
        handle_error(f"Error analyzing capacity opportunities: {str(e)}")
        return []

def generate_growth_insights() -> List[Dict[str, Any]]:
    """
    Generate growth insights for the business.
    
    This function analyzes data across multiple dimensions of the business to
    identify opportunities for growth, operational improvements, and capital
    efficiency.
    
    Returns:
        List of insight objects with recommendations
        
    Raises:
        RuntimeError: If no insights could be generated
    """
    with Spinner("Growth Accelerator"):
        try:
            # Create asyncio event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Gather all insights
            all_insights = []
            
            # Revenue leak detection
            all_insights.extend(loop.run_until_complete(_get_unconverted_leads()))
            all_insights.extend(loop.run_until_complete(_get_paused_projects()))
            all_insights.extend(loop.run_until_complete(_get_underbilled_invoices()))
            all_insights.extend(loop.run_until_complete(_get_overdue_collections()))
            
            # Operational bottleneck detection
            all_insights.extend(loop.run_until_complete(_get_late_projects()))
            all_insights.extend(loop.run_until_complete(_get_missing_contracts()))
            
            # Capital inefficiency detection
            all_insights.extend(loop.run_until_complete(_get_idle_cash()))
            all_insights.extend(loop.run_until_complete(_get_inefficient_lead_sources()))
            all_insights.extend(loop.run_until_complete(_get_early_payment_opportunities()))
            
            # Check if we found any insights
            if not all_insights:
                error_message = "Growth Accelerator returned no insights – verify inputs and data"
                handle_error(error_message, "growth_accelerator")
                raise RuntimeError(error_message)
            
            # Sort insights by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_insights = sorted(
                all_insights,
                key=lambda x: (
                    priority_order.get(x.get("priority", "low"), 99),
                    -1 * x.get("potential_value", 0)
                )
            )
            
            return sorted_insights
            
        except Exception as e:
            handle_error(f"Failed to generate growth insights: {str(e)}", "growth_accelerator")
            raise

if __name__ == "__main__":
    # Simple test if run directly
    try:
        insights = generate_growth_insights()
        print(f"Found {len(insights)} growth insights")
        for i, insight in enumerate(insights[:5], 1):
            print(f"{i}. [{insight['priority']}] {insight['title']} - ${insight['potential_value']:.2f}")
    except Exception as e:
        print(f"Error: {e}")