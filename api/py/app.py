"""
FastAPI Bridge for Restoration-Intel
Exposes Python analytics functions to Next.js app
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
import json
import httpx
from dotenv import load_dotenv
import numpy as np
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get Supabase URL and anon key from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Create FastAPI app
app = FastAPI(title="Restoration-Intel API Bridge")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LeadingIndicatorInput(BaseModel):
    kpi_code: str
    value: float
    breach: bool = False
    playbook_json: Dict[str, str] = None

# Helper functions
async def supabase_rpc(function_name: str, params: Dict = None):
    """Call a Supabase RPC function"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/rpc/{function_name}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=params or {}, headers=headers)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

# Routes
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"status": "online", "service": "Restoration-Intel API Bridge", "timestamp": datetime.now().isoformat()}

@app.get("/cash-position")
async def get_cash_position():
    """Get current cash position with projections"""
    try:
        result = await supabase_rpc("get_cash_position")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cash position: {str(e)}")

@app.get("/ap-timeline")
async def get_ap_timeline():
    """Get accounts payable timeline with payment recommendations"""
    try:
        result = await supabase_rpc("get_ap_timeline")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AP timeline: {str(e)}")

@app.post("/lead-indicators")
async def create_leading_indicator(data: LeadingIndicatorInput):
    """Insert a new leading indicator"""
    try:
        # Prepare the playbook if not provided
        if not data.playbook_json and data.breach:
            # Default playbooks for different indicators
            playbooks = {
                "pipeline_velocity_days": {
                    "action": "Review sales process and follow-up protocols",
                    "rationale": "Longer time to convert leads impacts cash flow",
                    "expected_impact": "Reduced sales cycle by 15-20%"
                },
                "backlog_coverage_ratio": {
                    "action": "Increase marketing spend and sales outreach",
                    "rationale": "Insufficient future work booked",
                    "expected_impact": "Restore 8+ weeks of backlog coverage"
                },
                "ar_30d_new": {
                    "action": "Contact clients with upcoming payments",
                    "rationale": "Proactive collections management",
                    "expected_impact": "Reduce DSO by 5-7 days"
                },
                "runway_p5_weeks": {
                    "action": "Implement cash conservation measures",
                    "rationale": "Risk of cash shortfall in Monte-Carlo simulation",
                    "expected_impact": "Extend runway by 8+ weeks"
                }
            }
            
            data.playbook_json = playbooks.get(data.kpi_code, {
                "action": "Review KPI data and identify root causes",
                "rationale": "KPI breach detected",
                "expected_impact": "Return KPI to acceptable range"
            })
        
        # Call Supabase function
        payload = {
            "kpi_code": data.kpi_code,
            "kpi_date": datetime.now().date().isoformat(),
            "value": data.value,
            "breach": data.breach,
            "playbook_json": data.playbook_json
        }
        
        result = await supabase_rpc("insert_leading_indicator", payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating leading indicator: {str(e)}")

@app.get("/lead-indicators/calculate/runway")
async def calculate_runway_p5():
    """Calculate 5-percentile runway weeks using Monte-Carlo simulation"""
    try:
        # Call Supabase to get cash flow data
        # This would be a separate RPC function in a real implementation
        # For demo, we'll use simulated data
        
        # Simulate cash flow metrics
        current_cash = 45000
        weekly_burn_mean = 8500
        weekly_burn_std = 2200
        weekly_inflow_mean = 9200
        weekly_inflow_std = 3800
        correlation = 0.3  # Some correlation between inflows and outflows
        
        # Run Monte-Carlo simulation (1000 trials, 12 weeks)
        weeks = 12
        trials = 1000
        results = []
        
        for _ in range(trials):
            # Generate correlated random variables for inflows and outflows
            z1 = np.random.normal(0, 1, weeks)
            z2 = correlation * z1 + np.sqrt(1 - correlation**2) * np.random.normal(0, 1, weeks)
            
            inflows = weekly_inflow_mean + weekly_inflow_std * z1
            outflows = weekly_burn_mean + weekly_burn_std * z2
            
            # Calculate net cash flow
            net_flows = inflows - outflows
            
            # Calculate cumulative cash position
            cash_position = np.zeros(weeks + 1)
            cash_position[0] = current_cash
            
            for i in range(weeks):
                cash_position[i + 1] = cash_position[i] + net_flows[i]
            
            # Find week when cash runs out (if it does)
            runway = weeks
            for i in range(weeks + 1):
                if cash_position[i] <= 0:
                    runway = i
                    break
            
            results.append(runway)
        
        # Calculate 5th percentile
        p5_runway = np.percentile(results, 5)
        
        # Determine if this is a breach
        is_breach = p5_runway < 8  # 8 weeks is the threshold
        
        # Create leading indicator
        indicator_data = LeadingIndicatorInput(
            kpi_code="runway_p5_weeks",
            value=float(p5_runway),
            breach=is_breach
        )
        
        result = await create_leading_indicator(indicator_data)
        
        # Add simulation details to result
        result["simulation_details"] = {
            "trials": trials,
            "weeks_simulated": weeks,
            "percentiles": {
                "p5": float(p5_runway),
                "p25": float(np.percentile(results, 25)),
                "p50": float(np.percentile(results, 50)),
                "p75": float(np.percentile(results, 75))
            },
            "breach": is_breach,
            "threshold": 8
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating runway: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)