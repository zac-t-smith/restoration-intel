"""
Operational Efficiency & Unit Economics Metrics Module

This module contains functions for calculating operational efficiency and unit economics metrics.
Phase 2: Operational Efficiency & Unit Economics (30-180 Days)
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
            handle_error(f"API error: {response.text}", "operational_metrics")
            raise RuntimeError(f"Supabase RPC failed: {response.status_code}")
        return response.json()

async def _execute_sql(query: str, params: Dict = None) -> List[Dict]:
    """Execute a SQL query against Supabase"""
    result = await _call_supabase_rpc("execute_sql", {"query": query, "params": params or {}})
    return result

def calculate_rpj(segmentation: str = None) -> Dict[str, float]:
    """
    Calculate Revenue Per Job (RPJ).
    
    Formula: Total Revenue ÷ Number of Jobs Completed
    
    Args:
        segmentation: Optional segmentation parameter (e.g., 'job_type', 'customer_type').
                      If provided, results will be segmented accordingly.
        
    Returns:
        Dictionary with RPJ values, potentially segmented if requested.
        
    Integration:
        - Add to operational dashboard as key performance indicator
        - Use in job type profitability analysis
        - Include in pricing strategy
    """
    with Spinner("Revenue Per Job"):
        try:
            # Base SQL query for all jobs
            if segmentation is None or segmentation == 'overall':
                query = """
                SELECT 
                    COUNT(*) as job_count,
                    SUM(total_revenue) as total_revenue,
                    SUM(total_revenue) / COUNT(*) as rpj
                FROM projects
                WHERE status = 'completed'
                """
            # Segmented query by job type
            elif segmentation == 'job_type':
                query = """
                SELECT 
                    job_type,
                    COUNT(*) as job_count,
                    SUM(total_revenue) as total_revenue,
                    SUM(total_revenue) / COUNT(*) as rpj
                FROM projects
                WHERE status = 'completed'
                GROUP BY job_type
                ORDER BY job_type
                """
            # Other segmentation options can be added here
            else:
                raise ValueError(f"Unsupported segmentation: {segmentation}")
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            if segmentation is None or segmentation == 'overall':
                return {"overall_rpj": 8750.0, "job_count": 24, "total_revenue": 210000.0}
            elif segmentation == 'job_type':
                return {
                    "water": {"rpj": 7500.0, "job_count": 12, "total_revenue": 90000.0},
                    "fire": {"rpj": 12000.0, "job_count": 8, "total_revenue": 96000.0},
                    "mold": {"rpj": 6000.0, "job_count": 4, "total_revenue": 24000.0}
                }
        
        except Exception as e:
            handle_error(f"Failed to calculate Revenue Per Job: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate Revenue Per Job: {str(e)}")

def calculate_job_completion_rate(period: str = 'month') -> float:
    """
    Calculate Job Completion Rate.
    
    Formula: (Jobs Completed ÷ Jobs Started) × 100
    
    Args:
        period: Time period for calculation ('month', 'quarter', 'year').
               Defaults to 'month'.
        
    Returns:
        Job completion rate as a percentage.
        
    Integration:
        - Add to operational dashboard
        - Use in resource allocation planning
        - Include in team performance metrics
    """
    with Spinner("Job Completion Rate"):
        try:
            # Determine date range based on period
            if period == 'month':
                date_range = "30 days"
            elif period == 'quarter':
                date_range = "90 days"
            elif period == 'year':
                date_range = "365 days"
            else:
                raise ValueError(f"Unsupported period: {period}")
            
            # SQL query to get job completion stats
            query = f"""
            SELECT 
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                COUNT(*) as total_jobs
            FROM projects
            WHERE created_at >= NOW() - INTERVAL '{date_range}'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            completed_jobs = 18
            total_jobs = 20
            
            # Calculate completion rate
            completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            return completion_rate
        
        except Exception as e:
            handle_error(f"Failed to calculate Job Completion Rate: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate Job Completion Rate: {str(e)}")

def calculate_adc() -> float:
    """
    Calculate Average Days to Complete (ADC).
    
    Formula: Total Days for All Jobs ÷ Number of Jobs
    
    Returns:
        Average days to complete a job.
        
    Integration:
        - Add to operational dashboard
        - Use in scheduling and resource planning
        - Include in customer communication about timelines
    """
    with Spinner("Average Days to Complete"):
        try:
            # SQL query to calculate days to complete for each job
            query = """
            SELECT 
                AVG(
                    CASE 
                        WHEN status = 'completed' THEN 
                            EXTRACT(DAY FROM (updated_at - start_date))
                        ELSE NULL
                    END
                ) as avg_days_to_complete
            FROM projects
            WHERE status = 'completed'
            AND updated_at >= NOW() - INTERVAL '90 days'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return a placeholder value
            return 12.5  # 12.5 days average
        
        except Exception as e:
            handle_error(f"Failed to calculate Average Days to Complete: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate Average Days to Complete: {str(e)}")

def calculate_cac_by_channel() -> Dict[str, float]:
    """
    Calculate Customer Acquisition Cost (CAC) by Channel.
    
    Formula: Total Marketing/Sales Spend ÷ New Customers Acquired
    
    Returns:
        Dictionary with CAC values for each channel.
        
    Integration:
        - Add to marketing dashboard
        - Use in marketing budget allocation
        - Include in ROI analysis
    """
    with Spinner("CAC by Channel"):
        try:
            # SQL query to get lead costs and conversions by source
            query = """
            SELECT 
                l.lead_source,
                SUM(l.lead_cost) as total_cost,
                COUNT(DISTINCT c.id) as customers_acquired,
                SUM(l.lead_cost) / NULLIF(COUNT(DISTINCT c.id), 0) as cac
            FROM leads l
            LEFT JOIN customers c ON l.id = c.lead_id
            WHERE l.created_at >= NOW() - INTERVAL '90 days'
            GROUP BY l.lead_source
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll return placeholder values
            return {
                "Google Ads": 285.75,
                "Facebook": 320.50,
                "Referral": 125.00,
                "Direct Mail": 450.25,
                "Overall": 295.50
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate CAC by Channel: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate CAC by Channel: {str(e)}")

def calculate_clv() -> float:
    """
    Calculate Customer Lifetime Value (CLV).
    
    Formula: (Average Revenue per Customer × Gross Margin %) ÷ Churn Rate
    
    Returns:
        Calculated CLV value.
        
    Integration:
        - Add to executive dashboard
        - Use in customer retention strategy
        - Include in marketing investment decisions
    """
    with Spinner("Customer Lifetime Value"):
        try:
            # SQL query to get average revenue per customer
            avg_revenue_query = """
            SELECT 
                AVG(customer_revenue) as avg_revenue_per_customer
            FROM (
                SELECT 
                    c.id as customer_id,
                    SUM(p.total_revenue) as customer_revenue
                FROM customers c
                JOIN projects p ON c.id = p.customer_id
                GROUP BY c.id
            ) as customer_revenues
            """
            
            # SQL query to get gross margin
            gross_margin_query = """
            SELECT 
                (SUM(total_revenue) - SUM(total_expenses) - SUM(allocated_lead_cost)) / SUM(total_revenue) * 100 as gross_margin_pct
            FROM projects
            WHERE status = 'completed'
            AND updated_at >= NOW() - INTERVAL '365 days'
            """
            
            # SQL query to get churn rate (approximated by lack of repeat business)
            churn_query = """
            WITH customer_projects AS (
                SELECT 
                    c.id as customer_id,
                    MAX(p.created_at) as last_project_date
                FROM customers c
                JOIN projects p ON c.id = p.customer_id
                GROUP BY c.id
            )
            SELECT 
                COUNT(CASE WHEN last_project_date < NOW() - INTERVAL '365 days' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0) as churn_rate
            FROM customer_projects
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            avg_revenue_per_customer = 18500.0
            gross_margin_pct = 42.5  # 42.5%
            churn_rate = 0.15  # 15% annual churn
            
            # Calculate CLV
            clv = (avg_revenue_per_customer * (gross_margin_pct / 100)) / churn_rate if churn_rate > 0 else 0
            
            return clv
        
        except Exception as e:
            handle_error(f"Failed to calculate Customer Lifetime Value: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate Customer Lifetime Value: {str(e)}")

def calculate_nrr() -> float:
    """
    Calculate Net Revenue Retention (NRR).
    
    Formula: ((Starting ARR + Expansion - Contraction - Churn) ÷ Starting ARR) × 100
    
    Returns:
        NRR as a percentage.
        
    Integration:
        - Add to executive dashboard
        - Use in customer success strategy
        - Include in investor reporting
    """
    with Spinner("Net Revenue Retention"):
        try:
            # Define time periods
            current_period_start = datetime.now() - timedelta(days=30)
            current_period_end = datetime.now()
            prior_period_start = datetime.now() - timedelta(days=60)
            prior_period_end = datetime.now() - timedelta(days=30)
            
            # SQL query to get starting ARR (using prior period)
            starting_arr_query = f"""
            SELECT 
                SUM(total_revenue) as starting_arr
            FROM projects
            WHERE created_at BETWEEN '{prior_period_start.isoformat()}' AND '{prior_period_end.isoformat()}'
            """
            
            # SQL query to get expansion revenue (additional revenue from existing customers)
            expansion_query = f"""
            SELECT 
                SUM(p2.total_revenue - p1.total_revenue) as expansion
            FROM projects p1
            JOIN projects p2 ON p1.customer_id = p2.customer_id
            WHERE p1.created_at BETWEEN '{prior_period_start.isoformat()}' AND '{prior_period_end.isoformat()}'
            AND p2.created_at BETWEEN '{current_period_start.isoformat()}' AND '{current_period_end.isoformat()}'
            AND p2.total_revenue > p1.total_revenue
            """
            
            # SQL query to get contraction revenue (reduced revenue from existing customers)
            contraction_query = f"""
            SELECT 
                SUM(p1.total_revenue - p2.total_revenue) as contraction
            FROM projects p1
            JOIN projects p2 ON p1.customer_id = p2.customer_id
            WHERE p1.created_at BETWEEN '{prior_period_start.isoformat()}' AND '{prior_period_end.isoformat()}'
            AND p2.created_at BETWEEN '{current_period_start.isoformat()}' AND '{current_period_end.isoformat()}'
            AND p2.total_revenue < p1.total_revenue
            """
            
            # SQL query to get churn (lost revenue from customers who didn't return)
            churn_query = f"""
            SELECT 
                SUM(p.total_revenue) as churn
            FROM projects p
            WHERE p.created_at BETWEEN '{prior_period_start.isoformat()}' AND '{prior_period_end.isoformat()}'
            AND p.customer_id NOT IN (
                SELECT DISTINCT customer_id
                FROM projects
                WHERE created_at BETWEEN '{current_period_start.isoformat()}' AND '{current_period_end.isoformat()}'
            )
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            starting_arr = 100000.0
            expansion = 20000.0
            contraction = 5000.0
            churn = 10000.0
            
            # Calculate NRR
            nrr = ((starting_arr + expansion - contraction - churn) / starting_arr * 100) if starting_arr > 0 else 0
            
            return nrr
        
        except Exception as e:
            handle_error(f"Failed to calculate Net Revenue Retention: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate Net Revenue Retention: {str(e)}")

def calculate_technician_utilization() -> float:
    """
    Calculate Technician Utilization Rate.
    
    Formula: (Billable Hours ÷ Available Hours) × 100
    
    Returns:
        Technician utilization rate as a percentage.
        
    Integration:
        - Add to operations dashboard
        - Use in workforce planning
        - Include in productivity analysis
    """
    with Spinner("Technician Utilization"):
        try:
            # Note: This assumes there's a table for tracking technician hours
            # SQL query to get billable and available hours
            query = """
            SELECT 
                SUM(billable_hours) as total_billable_hours,
                SUM(available_hours) as total_available_hours,
                SUM(billable_hours) / NULLIF(SUM(available_hours), 0) * 100 as utilization_rate
            FROM technician_hours
            WHERE work_date >= NOW() - INTERVAL '30 days'
            """
            
            # TODO: Implement the actual database calls or integrate with time tracking system
            # For now, we'll use placeholder values
            billable_hours = 1250
            available_hours = 1600
            
            # Calculate utilization rate
            utilization_rate = (billable_hours / available_hours * 100) if available_hours > 0 else 0
            
            return utilization_rate
        
        except Exception as e:
            handle_error(f"Failed to calculate Technician Utilization: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate Technician Utilization: {str(e)}")

def calculate_equipment_roi() -> Dict[str, float]:
    """
    Calculate Equipment ROI.
    
    Formula: (Annual Revenue from Equipment - Annual Equipment Costs) ÷ Equipment Investment
    
    Returns:
        Dictionary with overall and per-equipment ROI values.
        
    Integration:
        - Add to asset management dashboard
        - Use in equipment purchase decisions
        - Include in capital expenditure planning
    """
    with Spinner("Equipment ROI"):
        try:
            # Note: This assumes there's a table for tracking equipment
            # SQL query to get equipment revenue, costs, and investment
            query = """
            SELECT 
                e.id as equipment_id,
                e.name as equipment_name,
                SUM(p.total_revenue * e.usage_percentage / 100) as annual_revenue,
                SUM(e.maintenance_cost + e.depreciation) as annual_costs,
                e.purchase_price as equipment_investment,
                (SUM(p.total_revenue * e.usage_percentage / 100) - SUM(e.maintenance_cost + e.depreciation)) / NULLIF(e.purchase_price, 0) as roi
            FROM equipment e
            JOIN equipment_usage eu ON e.id = eu.equipment_id
            JOIN projects p ON eu.project_id = p.id
            WHERE p.created_at >= NOW() - INTERVAL '365 days'
            GROUP BY e.id, e.name, e.purchase_price
            """
            
            # TODO: Implement the actual database calls or integrate with asset management system
            # For now, we'll use placeholder values
            overall_roi = 1.75  # 175% ROI
            equipment_roi = {
                "Water Extractors": 2.1,
                "Dehumidifiers": 1.9,
                "Air Movers": 1.6,
                "Thermal Imaging Cameras": 1.2
            }
            
            # Combine results
            result = {"overall": overall_roi}
            result.update(equipment_roi)
            
            return result
        
        except Exception as e:
            handle_error(f"Failed to calculate Equipment ROI: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate Equipment ROI: {str(e)}")

def calculate_first_time_fix_rate() -> float:
    """
    Calculate First-Time Fix Rate.
    
    Formula: (Jobs Completed on First Visit ÷ Total Jobs) × 100
    
    Returns:
        First-time fix rate as a percentage.
        
    Integration:
        - Add to service quality dashboard
        - Use in training and process improvement
        - Include in customer satisfaction analysis
    """
    with Spinner("First-Time Fix Rate"):
        try:
            # Note: This assumes there's tracking for visit counts
            # SQL query to get first-time fix stats
            query = """
            SELECT 
                COUNT(CASE WHEN visit_count = 1 THEN 1 END) as single_visit_jobs,
                COUNT(*) as total_jobs,
                COUNT(CASE WHEN visit_count = 1 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as first_time_fix_rate
            FROM projects
            WHERE status = 'completed'
            AND updated_at >= NOW() - INTERVAL '90 days'
            """
            
            # TODO: Implement the actual database calls or integrate with job tracking system
            # For now, we'll use placeholder values
            single_visit_jobs = 42
            total_jobs = 50
            
            # Calculate first-time fix rate
            first_time_fix_rate = (single_visit_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            return first_time_fix_rate
        
        except Exception as e:
            handle_error(f"Failed to calculate First-Time Fix Rate: {str(e)}", "operational_metrics")
            raise RuntimeError(f"Failed to calculate First-Time Fix Rate: {str(e)}")