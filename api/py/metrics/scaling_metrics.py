"""
Scaling & Growth Metrics Module

This module contains functions for calculating metrics related to scaling and growth.
Phases 4-6: Scale Preparation, Scaling & Expansion, and Market Domination
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
            handle_error(f"API error: {response.text}", "scaling_metrics")
            raise RuntimeError(f"Supabase RPC failed: {response.status_code}")
        return response.json()

async def _execute_sql(query: str, params: Dict = None) -> List[Dict]:
    """Execute a SQL query against Supabase"""
    result = await _call_supabase_rpc("execute_sql", {"query": query, "params": params or {}})
    return result

# ---------------------- Phase 4: Scale Preparation (6-18 Months) ----------------------

def calculate_market_share(geography: str) -> float:
    """
    Calculate Market Share by Geography.
    
    Formula: Your Revenue ÷ Total Addressable Market × 100
    
    Args:
        geography: The geographic area to calculate market share for (e.g., 'city', 'county', 'state').
        
    Returns:
        Market share percentage.
        
    Integration:
        - Add to executive dashboard
        - Use in expansion planning
        - Include in investor reporting
    """
    with Spinner("Market Share Calculation"):
        try:
            # This requires market data, which might be sourced externally
            # SQL query to get company revenue by geography
            query = f"""
            SELECT 
                SUM(p.total_revenue) as company_revenue
            FROM projects p
            JOIN customers c ON p.customer_id = c.id
            WHERE c.geography = '{geography}'
            AND p.created_at >= NOW() - INTERVAL '365 days'
            """
            
            # TODO: Implement the actual database calls and market size data integration
            # For now, we'll use placeholder values
            company_revenue = 5250000  # $5.25M annual revenue in the specified geography
            
            # Market size data would ideally come from industry databases or reports
            # These would be stored in a separate table or external API
            market_sizes = {
                "Springfield": 35000000,      # $35M
                "Shelbyville": 22000000,      # $22M
                "Capital City": 85000000,     # $85M
                "Illinois": 450000000,        # $450M
                "Overall": 2500000000         # $2.5B
            }
            
            total_addressable_market = market_sizes.get(geography, 50000000)  # Default to $50M if not found
            
            # Calculate market share
            market_share = (company_revenue / total_addressable_market * 100) if total_addressable_market > 0 else 0
            
            return market_share
        
        except Exception as e:
            handle_error(f"Failed to calculate Market Share for {geography}: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Market Share: {str(e)}")

def calculate_pipeline_velocity() -> float:
    """
    Calculate Pipeline Velocity.
    
    Formula: (Number of Opportunities × Average Deal Size × Win Rate) ÷ Average Sales Cycle Length
    
    Returns:
        Pipeline velocity value ($ per day).
        
    Integration:
        - Add to sales dashboard
        - Use in revenue forecasting
        - Include in sales team performance metrics
    """
    with Spinner("Pipeline Velocity"):
        try:
            # Calculate components of pipeline velocity
            # SQL query for lead stats
            query = """
            WITH lead_stats AS (
                SELECT 
                    COUNT(*) as total_opportunities,
                    COUNT(CASE WHEN status = 'converted' THEN 1 END) as won_opportunities,
                    COUNT(CASE WHEN status = 'converted' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0) as win_rate,
                    AVG(EXTRACT(DAY FROM (
                        CASE WHEN status = 'converted' AND converted_at IS NOT NULL 
                        THEN converted_at - created_at 
                        ELSE NULL END
                    ))) as avg_sales_cycle_days
                FROM leads
                WHERE created_at >= NOW() - INTERVAL '90 days'
            ),
            project_stats AS (
                SELECT 
                    AVG(total_revenue) as avg_deal_size
                FROM projects
                WHERE created_at >= NOW() - INTERVAL '90 days'
            )
            SELECT 
                ls.total_opportunities,
                ls.won_opportunities,
                ls.win_rate,
                ls.avg_sales_cycle_days,
                ps.avg_deal_size,
                (ls.total_opportunities * ps.avg_deal_size * ls.win_rate) / NULLIF(ls.avg_sales_cycle_days, 0) as pipeline_velocity
            FROM lead_stats ls, project_stats ps
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            total_opportunities = 120     # 120 opportunities in pipeline
            avg_deal_size = 15000         # $15,000 average deal size
            win_rate = 0.25               # 25% win rate
            avg_sales_cycle_days = 18     # 18 days average sales cycle
            
            # Calculate pipeline velocity
            pipeline_velocity = (total_opportunities * avg_deal_size * win_rate) / avg_sales_cycle_days if avg_sales_cycle_days > 0 else 0
            
            return pipeline_velocity
        
        except Exception as e:
            handle_error(f"Failed to calculate Pipeline Velocity: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Pipeline Velocity: {str(e)}")

def calculate_insurance_carrier_penetration() -> Dict[str, Any]:
    """
    Calculate Insurance Carrier Penetration.
    
    Formula: Number of Active Carrier Relationships ÷ Total Carriers in Market
    
    Returns:
        Dictionary with penetration metrics and carrier details.
        
    Integration:
        - Add to strategic partnerships dashboard
        - Use in carrier relationship development
        - Include in market expansion planning
    """
    with Spinner("Insurance Carrier Penetration"):
        try:
            # SQL query to get active insurance carrier relationships
            query = """
            SELECT 
                COUNT(DISTINCT insurance_carrier) as active_carriers,
                array_agg(DISTINCT insurance_carrier) as carrier_list
            FROM projects
            WHERE insurance_carrier IS NOT NULL
            AND created_at >= NOW() - INTERVAL '365 days'
            """
            
            # TODO: Implement the actual database calls and market data integration
            # For now, we'll use placeholder values
            active_carriers = 12
            carrier_list = [
                "State Farm", "Allstate", "GEICO", "Progressive", 
                "Liberty Mutual", "Farmers", "Nationwide", "Travelers",
                "American Family", "Erie Insurance", "USAA", "Hartford"
            ]
            
            # Total carriers in market (this would ideally come from industry database)
            total_carriers_in_market = 35
            
            # Calculate penetration
            penetration = (active_carriers / total_carriers_in_market * 100) if total_carriers_in_market > 0 else 0
            
            # Return comprehensive metrics
            return {
                "penetration_percentage": penetration,
                "active_carriers": active_carriers,
                "total_carriers": total_carriers_in_market,
                "carrier_list": carrier_list,
                "top_opportunities": [
                    "Mercury Insurance", "Amica", "Auto-Owners Insurance"
                ]
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate Insurance Carrier Penetration: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Insurance Carrier Penetration: {str(e)}")

def calculate_revenue_per_employee() -> Dict[str, float]:
    """
    Calculate Revenue per Employee.
    
    Formula: Total Revenue ÷ Total FTEs
    
    Returns:
        Dictionary with revenue per employee metrics.
        
    Integration:
        - Add to executive dashboard
        - Use in workforce planning
        - Include in productivity analysis
    """
    with Spinner("Revenue per Employee"):
        try:
            # SQL query to get total revenue
            revenue_query = """
            SELECT 
                SUM(total_revenue) as total_revenue
            FROM projects
            WHERE created_at >= NOW() - INTERVAL '365 days'
            """
            
            # SQL query to get employee count
            employee_query = """
            SELECT 
                COUNT(*) as employee_count,
                SUM(CASE WHEN department = 'field' THEN 1 ELSE 0 END) as field_employees,
                SUM(CASE WHEN department = 'office' THEN 1 ELSE 0 END) as office_employees,
                SUM(CASE WHEN department = 'management' THEN 1 ELSE 0 END) as management_employees
            FROM employees
            WHERE status = 'active'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            total_revenue = 8750000  # $8.75M annual revenue
            
            employee_counts = {
                "total": 45,
                "field": 32,
                "office": 10,
                "management": 3
            }
            
            # Calculate revenue per employee for each category
            revenue_per_employee = {
                category: total_revenue / count if count > 0 else 0
                for category, count in employee_counts.items()
            }
            
            # Include raw data for context
            return {
                "revenue_per_employee": revenue_per_employee,
                "total_revenue": total_revenue,
                "employee_counts": employee_counts
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate Revenue per Employee: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Revenue per Employee: {str(e)}")

def calculate_manager_span() -> Dict[str, Any]:
    """
    Calculate Management Span of Control.
    
    Formula: Number of Direct Reports per Manager
    
    Returns:
        Dictionary with span metrics and details.
        
    Integration:
        - Add to organizational health dashboard
        - Use in management structure planning
        - Include in operational efficiency analysis
    """
    with Spinner("Management Span"):
        try:
            # SQL query to get management span data
            query = """
            SELECT 
                m.id as manager_id,
                m.name as manager_name,
                COUNT(e.id) as direct_reports
            FROM employees m
            JOIN employees e ON e.manager_id = m.id
            WHERE m.status = 'active' AND e.status = 'active'
            GROUP BY m.id, m.name
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            manager_spans = [
                {"manager_id": 1, "manager_name": "John Smith", "direct_reports": 8},
                {"manager_id": 2, "manager_name": "Jane Doe", "direct_reports": 12},
                {"manager_id": 3, "manager_name": "Bob Johnson", "direct_reports": 5}
            ]
            
            # Calculate average span
            total_managers = len(manager_spans)
            total_direct_reports = sum(m["direct_reports"] for m in manager_spans)
            avg_span = total_direct_reports / total_managers if total_managers > 0 else 0
            
            # Add summary metrics
            result = {
                "average_span": avg_span,
                "manager_details": manager_spans,
                "total_managers": total_managers,
                "total_direct_reports": total_direct_reports
            }
            
            return result
        
        except Exception as e:
            handle_error(f"Failed to calculate Management Span: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Management Span: {str(e)}")

# ---------------------- Phase 5: Scaling & Expansion (18 Months - 5 Years) ----------------------

def calculate_location_roi(location_id: int) -> Dict[str, float]:
    """
    Calculate Location ROI.
    
    Formula: (Location Annual Profit - Location Investment) ÷ Location Investment
    
    Args:
        location_id: ID of the location to analyze.
        
    Returns:
        Dictionary with location ROI metrics.
        
    Integration:
        - Add to expansion planning dashboard
        - Use in location performance evaluation
        - Include in investment decision-making
    """
    with Spinner(f"Location ROI - Location #{location_id}"):
        try:
            # SQL query to get location performance data
            query = f"""
            WITH location_projects AS (
                SELECT 
                    p.id as project_id,
                    p.total_revenue,
                    p.total_expenses,
                    p.allocated_lead_cost
                FROM projects p
                WHERE p.location_id = {location_id}
                AND p.created_at >= NOW() - INTERVAL '365 days'
            ),
            location_overhead AS (
                SELECT 
                    SUM(amount) as overhead_cost
                FROM expenses
                WHERE location_id = {location_id}
                AND category = 'overhead'
                AND created_at >= NOW() - INTERVAL '365 days'
            )
            SELECT 
                SUM(lp.total_revenue) as annual_revenue,
                SUM(lp.total_expenses) as direct_expenses,
                SUM(lp.allocated_lead_cost) as lead_costs,
                lo.overhead_cost,
                (
                    SUM(lp.total_revenue) - 
                    SUM(lp.total_expenses) - 
                    SUM(lp.allocated_lead_cost) - 
                    lo.overhead_cost
                ) as annual_profit
            FROM location_projects lp, location_overhead lo
            """
            
            # SQL query to get location investment data
            investment_query = f"""
            SELECT 
                initial_investment,
                recurring_investment,
                initial_investment + recurring_investment as total_investment
            FROM locations
            WHERE id = {location_id}
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            annual_revenue = 1250000     # $1.25M
            direct_expenses = 650000      # $650K
            lead_costs = 75000           # $75K
            overhead_cost = 225000       # $225K
            annual_profit = annual_revenue - direct_expenses - lead_costs - overhead_cost
            
            initial_investment = 500000   # $500K initial setup
            recurring_investment = 100000 # $100K recurring investments
            total_investment = initial_investment + recurring_investment
            
            # Calculate ROI
            roi = (annual_profit / total_investment) if total_investment > 0 else 0
            
            # Return comprehensive metrics
            return {
                "location_id": location_id,
                "annual_revenue": annual_revenue,
                "annual_profit": annual_profit,
                "total_investment": total_investment,
                "roi": roi,
                "roi_percentage": roi * 100,
                "payback_period_years": total_investment / annual_profit if annual_profit > 0 else float('inf')
            }
        
        except Exception as e:
            handle_error(f"Failed to calculate Location ROI for location {location_id}: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Location ROI: {str(e)}")

def calculate_cross_location_efficiency() -> float:
    """
    Calculate Cross-Location Efficiency.
    
    Formula: Shared Resources Revenue ÷ Shared Resources Cost
    
    Returns:
        Cross-location efficiency ratio.
        
    Integration:
        - Add to multi-location dashboard
        - Use in shared services optimization
        - Include in resource allocation planning
    """
    with Spinner("Cross-Location Efficiency"):
        try:
            # SQL query to get shared resources data
            query = """
            -- Shared resources revenue (revenue attributed to shared resources)
            WITH shared_revenue AS (
                SELECT 
                    SUM(p.total_revenue * r.contribution_percentage / 100) as revenue
                FROM projects p
                JOIN resource_contributions r ON p.id = r.project_id
                JOIN resources res ON r.resource_id = res.id
                WHERE res.is_shared = true
                AND p.created_at >= NOW() - INTERVAL '365 days'
            ),
            -- Shared resources cost
            shared_cost AS (
                SELECT 
                    SUM(cost) as total_cost
                FROM resource_costs
                WHERE is_shared = true
                AND period >= NOW() - INTERVAL '365 days'
            )
            -- Calculate efficiency
            SELECT 
                sr.revenue as shared_resources_revenue,
                sc.total_cost as shared_resources_cost,
                sr.revenue / NULLIF(sc.total_cost, 0) as efficiency_ratio
            FROM shared_revenue sr, shared_cost sc
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            shared_resources_revenue = 2500000  # $2.5M revenue attributed to shared resources
            shared_resources_cost = 1200000     # $1.2M cost of shared resources
            
            # Calculate efficiency ratio
            efficiency_ratio = shared_resources_revenue / shared_resources_cost if shared_resources_cost > 0 else 0
            
            return efficiency_ratio
        
        except Exception as e:
            handle_error(f"Failed to calculate Cross-Location Efficiency: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Cross-Location Efficiency: {str(e)}")

def calculate_digital_lead_conversion_rate() -> Dict[str, float]:
    """
    Calculate Digital Lead Conversion Rate.
    
    Formula: (Leads Converting to Jobs ÷ Total Digital Leads) × 100
    
    Returns:
        Dictionary with digital lead conversion metrics.
        
    Integration:
        - Add to marketing dashboard
        - Use in digital marketing strategy
        - Include in customer acquisition planning
    """
    with Spinner("Digital Lead Conversion"):
        try:
            # SQL query to get digital lead conversion data
            query = """
            SELECT 
                lead_source,
                COUNT(*) as total_leads,
                COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads,
                COUNT(CASE WHEN status = 'converted' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as conversion_rate
            FROM leads
            WHERE lead_source_type = 'digital'
            AND created_at >= NOW() - INTERVAL '90 days'
            GROUP BY lead_source
            
            UNION ALL
            
            SELECT 
                'overall' as lead_source,
                COUNT(*) as total_leads,
                COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_leads,
                COUNT(CASE WHEN status = 'converted' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as conversion_rate
            FROM leads
            WHERE lead_source_type = 'digital'
            AND created_at >= NOW() - INTERVAL '90 days'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            digital_sources = {
                "Google Ads": {"total": 120, "converted": 18, "rate": 15.0},
                "Facebook": {"total": 85, "converted": 12, "rate": 14.1},
                "Instagram": {"total": 45, "converted": 5, "rate": 11.1},
                "Website": {"total": 95, "converted": 22, "rate": 23.2},
                "Email": {"total": 65, "converted": 8, "rate": 12.3},
                "overall": {"total": 410, "converted": 65, "rate": 15.9}
            }
            
            return digital_sources
        
        except Exception as e:
            handle_error(f"Failed to calculate Digital Lead Conversion Rate: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Digital Lead Conversion Rate: {str(e)}")

def calculate_process_standardization_score() -> Dict[str, Any]:
    """
    Calculate Process Standardization Score.
    
    Formula: (Standardized Processes ÷ Total Core Processes) × 100
    
    Returns:
        Dictionary with process standardization metrics.
        
    Integration:
        - Add to operations dashboard
        - Use in process improvement initiatives
        - Include in scaling readiness assessment
    """
    with Spinner("Process Standardization"):
        try:
            # SQL query to get process standardization data
            query = """
            SELECT 
                department,
                COUNT(*) as total_processes,
                COUNT(CASE WHEN is_standardized = true THEN 1 END) as standardized_processes,
                COUNT(CASE WHEN is_standardized = true THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as standardization_score
            FROM business_processes
            GROUP BY department
            
            UNION ALL
            
            SELECT 
                'overall' as department,
                COUNT(*) as total_processes,
                COUNT(CASE WHEN is_standardized = true THEN 1 END) as standardized_processes,
                COUNT(CASE WHEN is_standardized = true THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as standardization_score
            FROM business_processes
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            process_data = {
                "sales": {"total": 12, "standardized": 9, "score": 75.0},
                "operations": {"total": 25, "standardized": 22, "score": 88.0},
                "customer_service": {"total": 18, "standardized": 14, "score": 77.8},
                "finance": {"total": 15, "standardized": 13, "score": 86.7},
                "hr": {"total": 10, "standardized": 7, "score": 70.0},
                "overall": {"total": 80, "standardized": 65, "score": 81.3}
            }
            
            # Add core processes that need standardization
            needs_standardization = [
                {"process": "Lead qualification", "department": "sales", "priority": "high"},
                {"process": "Customer onboarding", "department": "customer_service", "priority": "medium"},
                {"process": "Equipment maintenance", "department": "operations", "priority": "low"}
            ]
            
            result = {
                "standardization_by_department": process_data,
                "overall_score": process_data["overall"]["score"],
                "needs_standardization": needs_standardization
            }
            
            return result
        
        except Exception as e:
            handle_error(f"Failed to calculate Process Standardization Score: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Process Standardization Score: {str(e)}")

# ---------------------- Phase 6: Market Domination (5-10 Years) ----------------------

def calculate_revenue_cagr(start_date: str, end_date: str) -> float:
    """
    Calculate Revenue CAGR (Compound Annual Growth Rate).
    
    Formula: ((Ending Revenue ÷ Beginning Revenue)^(1/number of years)) - 1
    
    Args:
        start_date: Start date for CAGR calculation (YYYY-MM-DD)
        end_date: End date for CAGR calculation (YYYY-MM-DD)
        
    Returns:
        CAGR value as a percentage.
        
    Integration:
        - Add to executive dashboard
        - Use in long-term planning
        - Include in investor reporting
    """
    with Spinner("Revenue CAGR"):
        try:
            # Parse dates
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            
            # Calculate years between dates
            years = (end - start).days / 365.25
            
            if years <= 0:
                raise ValueError("End date must be after start date")
            
            # SQL query to get revenue for start and end periods
            start_revenue_query = f"""
            SELECT 
                SUM(total_revenue) as revenue
            FROM projects
            WHERE created_at BETWEEN '{start_date}' AND '{(start + timedelta(days=365)).isoformat()}'
            """
            
            end_revenue_query = f"""
            SELECT 
                SUM(total_revenue) as revenue
            FROM projects
            WHERE created_at BETWEEN '{(end - timedelta(days=365)).isoformat()}' AND '{end_date}'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            beginning_revenue = 2500000  # $2.5M starting annual revenue
            ending_revenue = 8750000     # $8.75M ending annual revenue
            
            # Calculate CAGR
            cagr = (((ending_revenue / beginning_revenue) ** (1 / years)) - 1) * 100 if beginning_revenue > 0 else 0
            
            return cagr
        
        except Exception as e:
            handle_error(f"Failed to calculate Revenue CAGR: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Revenue CAGR: {str(e)}")

def calculate_ebitda_margin() -> Dict[str, float]:
    """
    Calculate EBITDA Margin Progression.
    
    Formula: EBITDA ÷ Revenue × 100
    
    Returns:
        Dictionary with EBITDA margin metrics.
        
    Integration:
        - Add to financial dashboard
        - Use in profitability analysis
        - Include in investor reporting
    """
    with Spinner("EBITDA Margin"):
        try:
            # SQL query to calculate EBITDA margin for multiple periods
            query = """
            WITH annual_metrics AS (
                -- Current year
                SELECT 
                    'current_year' as period,
                    SUM(total_revenue) as revenue,
                    (
                        SUM(total_revenue) - 
                        SUM(total_expenses) - 
                        (SELECT SUM(amount) FROM expenses WHERE category = 'overhead' AND created_at >= NOW() - INTERVAL '1 year')
                    ) as ebitda
                FROM projects
                WHERE created_at >= NOW() - INTERVAL '1 year'
                
                UNION ALL
                
                -- Previous year
                SELECT 
                    'previous_year' as period,
                    SUM(total_revenue) as revenue,
                    (
                        SUM(total_revenue) - 
                        SUM(total_expenses) - 
                        (SELECT SUM(amount) FROM expenses WHERE category = 'overhead' AND created_at BETWEEN NOW() - INTERVAL '2 year' AND NOW() - INTERVAL '1 year')
                    ) as ebitda
                FROM projects
                WHERE created_at BETWEEN NOW() - INTERVAL '2 year' AND NOW() - INTERVAL '1 year'
                
                UNION ALL
                
                -- Two years ago
                SELECT 
                    'two_years_ago' as period,
                    SUM(total_revenue) as revenue,
                    (
                        SUM(total_revenue) - 
                        SUM(total_expenses) - 
                        (SELECT SUM(amount) FROM expenses WHERE category = 'overhead' AND created_at BETWEEN NOW() - INTERVAL '3 year' AND NOW() - INTERVAL '2 year')
                    ) as ebitda
                FROM projects
                WHERE created_at BETWEEN NOW() - INTERVAL '3 year' AND NOW() - INTERVAL '2 year'
            )
            SELECT 
                period,
                revenue,
                ebitda,
                (ebitda / NULLIF(revenue, 0)) * 100 as ebitda_margin
            FROM annual_metrics
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            ebitda_data = {
                "current_year": {"revenue": 8750000, "ebitda": 1750000, "margin": 20.0},
                "previous_year": {"revenue": 6500000, "ebitda": 1105000, "margin": 17.0},
                "two_years_ago": {"revenue": 4200000, "ebitda": 630000, "margin": 15.0}
            }
            
            # Add trend analysis
            year_over_year_change = ebitda_data["current_year"]["margin"] - ebitda_data["previous_year"]["margin"]
            two_year_change = ebitda_data["current_year"]["margin"] - ebitda_data["two_years_ago"]["margin"]
            
            result = {
                "periods": ebitda_data,
                "year_over_year_change": year_over_year_change,
                "two_year_change": two_year_change,
                "current_margin": ebitda_data["current_year"]["margin"]
            }
            
            return result
        
        except Exception as e:
            handle_error(f"Failed to calculate EBITDA Margin: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate EBITDA Margin: {str(e)}")

def calculate_ev_multiple() -> float:
    """
    Calculate Enterprise Value Multiple.
    
    Formula: Enterprise Value ÷ EBITDA
    
    Returns:
        Enterprise value multiple.
        
    Integration:
        - Add to valuation dashboard
        - Use in exit strategy planning
        - Include in investor reporting
    """
    with Spinner("EV Multiple"):
        try:
            # This calculation requires company valuation data
            # SQL query to get EBITDA for trailing twelve months
            ebitda_query = """
            SELECT 
                SUM(total_revenue) as revenue,
                (
                    SUM(total_revenue) - 
                    SUM(total_expenses) - 
                    (SELECT SUM(amount) FROM expenses WHERE category = 'overhead' AND created_at >= NOW() - INTERVAL '1 year')
                ) as ebitda
            FROM projects
            WHERE created_at >= NOW() - INTERVAL '1 year'
            """
            
            # TODO: Implement the actual database calls
            # For now, we'll use placeholder values
            ttm_ebitda = 1750000  # $1.75M trailing twelve months EBITDA
            
            # Enterprise value would typically be calculated or estimated
            # For a private company, this might be based on industry multiples, recent transactions, etc.
            enterprise_value = 14000000  # $14M estimated enterprise value
            
            # Calculate EV multiple
            ev_multiple = enterprise_value / ttm_ebitda if ttm_ebitda > 0 else 0
            
            return ev_multiple
        
        except Exception as e:
            handle_error(f"Failed to calculate Enterprise Value Multiple: {str(e)}", "scaling_metrics")
            raise RuntimeError(f"Failed to calculate Enterprise Value Multiple: {str(e)}")