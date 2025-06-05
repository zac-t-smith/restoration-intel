"""
Profitability & Margin Optimization Metrics Module

This module contains functions for calculating profitability and margin optimization metrics.
Phase 3: Profitability & Margin Optimization (90-365 Days)
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
            handle_error(f"API error: {response.text}", "profitability_metrics")
            raise RuntimeError(f"Supabase RPC failed: {response.status_code}")
        return response.json()

async def _execute_sql(query: str, params: Dict = None) -> List[Dict]:
    """Execute a SQL query against Supabase"""
    result = await _call_supabase_rpc("execute_sql", {"query": query, "params": params or {}})
    return result

def calculate_gross_margin_by_service_line() -> Dict[str, float]:
    """
    Calculate Gross Margin by Service Line.
    
    Formula: (Revenue - Direct Costs) ÷ Revenue × 100
    
    Returns:
        Dictionary with gross margin percentages for each service line.
        
    Integration:
        - Add to financial dashboard
        - Use in service line optimization
        - Include in pricing strategy
    """
    with Spinner("Gross Margin by Service Line"):
        try:
            # SQL query to calculate gross margin by service line (job type)
            query = """
            SELECT 
                job_type as service_line,
                SUM(total_revenue) as revenue,
                SUM(total_expenses) as direct_costs,
                SUM(total_revenue - total_expenses - allocated_lead_cost) as gross_profit,
                (SUM(total_revenue - total_expenses - allocated_lead_cost) / NULLIF(SUM(total_revenue), 0)) * 100 as gross_margin_pct
            FROM projects
            WHERE status = 'completed'
            AND updated_at >= NOW() - INTERVAL '365 days'
            GROUP BY job_type
            ORDER BY gross_margin_pct DESC
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            return {
                "water": 42.5,
                "fire": 48.2,
                "mold": 51.8,
                "reconstruction": 38.6,
                "overall": 45.3
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate Gross Margin by Service Line: {str(e)}", "profitability_metrics")
            raise RuntimeError(f"Failed to calculate Gross Margin by Service Line: {str(e)}")

def calculate_job_level_profitability(job_id: int) -> Dict[str, float]:
    """
    Calculate Job-Level Profitability.
    
    Formula: Job Revenue - (Labor + Materials + Equipment + Overhead Allocation)
    
    Args:
        job_id: The ID of the job/project to analyze.
        
    Returns:
        Dictionary with profitability metrics for the specified job.
        
    Integration:
        - Add to project management dashboard
        - Use in job costing analysis
        - Include in crew performance evaluation
    """
    with Spinner(f"Job Profitability - Job #{job_id}"):
        try:
            # SQL query to get job details
            query = f"""
            SELECT 
                p.id as job_id,
                p.name as job_name,
                p.total_revenue as revenue,
                (
                    SELECT SUM(amount) 
                    FROM expenses 
                    WHERE project_id = p.id AND category = 'labor'
                ) as labor_cost,
                (
                    SELECT SUM(amount) 
                    FROM expenses 
                    WHERE project_id = p.id AND category = 'materials'
                ) as materials_cost,
                (
                    SELECT SUM(amount) 
                    FROM expenses 
                    WHERE project_id = p.id AND category = 'equipment'
                ) as equipment_cost,
                (
                    SELECT SUM(amount) 
                    FROM expenses 
                    WHERE project_id = p.id AND category = 'overhead'
                ) as overhead_cost,
                p.allocated_lead_cost as lead_cost,
                p.total_expenses as total_direct_costs,
                p.total_revenue - p.total_expenses - p.allocated_lead_cost as gross_profit,
                (p.total_revenue - p.total_expenses - p.allocated_lead_cost) / NULLIF(p.total_revenue, 0) * 100 as gross_margin_pct
            FROM projects p
            WHERE p.id = {job_id}
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            return {
                "job_id": job_id,
                "job_name": f"Project #{job_id}",
                "revenue": 12500.00,
                "labor_cost": 4200.00,
                "materials_cost": 2800.00,
                "equipment_cost": 800.00,
                "overhead_cost": 500.00,
                "lead_cost": 350.00,
                "total_direct_costs": 8300.00,
                "gross_profit": 3850.00,
                "gross_margin_pct": 30.8
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate Job-Level Profitability for job {job_id}: {str(e)}", "profitability_metrics")
            raise RuntimeError(f"Failed to calculate Job-Level Profitability: {str(e)}")

def calculate_labor_efficiency_ratio() -> Dict[str, float]:
    """
    Calculate Labor Efficiency Ratio.
    
    Formula: Revenue per Labor Hour ÷ Fully-Loaded Labor Cost per Hour
    
    Returns:
        Dictionary with labor efficiency metrics, overall and by job type.
        
    Integration:
        - Add to operations dashboard
        - Use in labor cost optimization
        - Include in crew training and performance improvement
    """
    with Spinner("Labor Efficiency Ratio"):
        try:
            # This calculation requires data about labor hours and costs
            # SQL query to calculate labor efficiency
            query = """
            WITH job_metrics AS (
                SELECT 
                    p.id as job_id,
                    p.job_type,
                    p.total_revenue as revenue,
                    (
                        SELECT SUM(amount) 
                        FROM expenses 
                        WHERE project_id = p.id AND category = 'labor'
                    ) as labor_cost,
                    (
                        SELECT SUM(hours) 
                        FROM labor_hours 
                        WHERE project_id = p.id
                    ) as labor_hours
                FROM projects p
                WHERE p.status = 'completed'
                AND p.updated_at >= NOW() - INTERVAL '90 days'
            )
            SELECT 
                job_type,
                SUM(revenue) / NULLIF(SUM(labor_hours), 0) as revenue_per_labor_hour,
                SUM(labor_cost) / NULLIF(SUM(labor_hours), 0) as labor_cost_per_hour,
                (SUM(revenue) / NULLIF(SUM(labor_hours), 0)) / NULLIF(SUM(labor_cost) / NULLIF(SUM(labor_hours), 0), 0) as labor_efficiency_ratio
            FROM job_metrics
            GROUP BY job_type
            
            UNION ALL
            
            SELECT 
                'overall' as job_type,
                SUM(revenue) / NULLIF(SUM(labor_hours), 0) as revenue_per_labor_hour,
                SUM(labor_cost) / NULLIF(SUM(labor_hours), 0) as labor_cost_per_hour,
                (SUM(revenue) / NULLIF(SUM(labor_hours), 0)) / NULLIF(SUM(labor_cost) / NULLIF(SUM(labor_hours), 0), 0) as labor_efficiency_ratio
            FROM job_metrics
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            return {
                "overall": {
                    "ratio": 1.75,
                    "revenue_per_hour": 105.00,
                    "cost_per_hour": 60.00
                },
                "water": {
                    "ratio": 1.85,
                    "revenue_per_hour": 111.00,
                    "cost_per_hour": 60.00
                },
                "fire": {
                    "ratio": 1.93,
                    "revenue_per_hour": 135.00,
                    "cost_per_hour": 70.00
                },
                "mold": {
                    "ratio": 1.67,
                    "revenue_per_hour": 100.00,
                    "cost_per_hour": 60.00
                }
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate Labor Efficiency Ratio: {str(e)}", "profitability_metrics")
            raise RuntimeError(f"Failed to calculate Labor Efficiency Ratio: {str(e)}")

def calculate_inventory_turnover() -> float:
    """
    Calculate Inventory Turnover.
    
    Formula: COGS ÷ Average Inventory Value
    
    Returns:
        Inventory turnover ratio.
        
    Integration:
        - Add to inventory management dashboard
        - Use in purchasing and stock level decisions
        - Include in cash flow optimization
    """
    with Spinner("Inventory Turnover"):
        try:
            # This calculation requires inventory data
            # SQL query to calculate inventory turnover
            query = """
            -- Get COGS from completed projects (using materials expenses)
            WITH material_cogs AS (
                SELECT 
                    SUM(amount) as total_cogs
                FROM expenses
                WHERE category = 'materials'
                AND created_at >= NOW() - INTERVAL '365 days'
            ),
            -- Get average inventory value (beginning and ending for the period)
            inventory_values AS (
                SELECT 
                    AVG(total_value) as avg_inventory_value
                FROM (
                    SELECT 
                        SUM(quantity * unit_cost) as total_value,
                        snapshot_date
                    FROM inventory_snapshots
                    WHERE snapshot_date IN (
                        (NOW() - INTERVAL '365 days')::date,
                        NOW()::date
                    )
                    GROUP BY snapshot_date
                ) as inventory_snapshots
            )
            -- Calculate turnover
            SELECT 
                m.total_cogs / NULLIF(i.avg_inventory_value, 0) as inventory_turnover
            FROM material_cogs m
            CROSS JOIN inventory_values i
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return a placeholder value
            return 8.5  # Inventory turns over 8.5 times per year
        
        except Exception as e:
            handle_error(f"Failed to calculate Inventory Turnover: {str(e)}", "profitability_metrics")
            raise RuntimeError(f"Failed to calculate Inventory Turnover: {str(e)}")

def calculate_ap_leverage() -> Dict[str, float]:
    """
    Calculate Accounts Payable Leverage.
    
    Formula: Average Payment Period ÷ Industry Standard
    
    Returns:
        Dictionary with AP leverage metrics.
        
    Integration:
        - Add to financial dashboard
        - Use in cash flow management
        - Include in vendor relationship strategy
    """
    with Spinner("AP Leverage"):
        try:
            # Calculate average days to pay vendors
            query = """
            SELECT 
                AVG(EXTRACT(DAY FROM (e.paid_date - e.due_date))) as avg_payment_period,
                v.name as vendor_name
            FROM expenses e
            JOIN vendors v ON e.vendor_id = v.id
            WHERE e.status = 'paid'
            AND e.paid_date >= NOW() - INTERVAL '90 days'
            GROUP BY v.name
            
            UNION ALL
            
            SELECT 
                AVG(EXTRACT(DAY FROM (e.paid_date - e.due_date))) as avg_payment_period,
                'overall' as vendor_name
            FROM expenses e
            WHERE e.status = 'paid'
            AND e.paid_date >= NOW() - INTERVAL '90 days'
            """
            
            # TODO: Implement the actual database calls
            # Industry standard payment period (typically 30 days)
            industry_standard = 30.0
            
            # For now, we'll return placeholder values
            avg_payment_periods = {
                "overall": 38.5,
                "Premier Contractors": 42.0,
                "Quality Materials Inc": 35.0,
                "Rapid Response Services": 28.0
            }
            
            # Calculate AP leverage (ratio of actual to industry standard)
            ap_leverage = {
                vendor: period / industry_standard
                for vendor, period in avg_payment_periods.items()
            }
            
            # Add additional context
            result = {
                "ap_leverage": ap_leverage,
                "avg_payment_periods": avg_payment_periods,
                "industry_standard": industry_standard
            }
            
            return result
        
        except Exception as e:
            handle_error(f"Failed to calculate AP Leverage: {str(e)}", "profitability_metrics")
            raise RuntimeError(f"Failed to calculate AP Leverage: {str(e)}")