"""
KPI Dictionary Module

This module defines key performance indicators (KPIs) used throughout the application,
including their labels, descriptions, and thresholds.
"""

# Dictionary of KPI definitions
KPI_DEFINITIONS = {
    "pipeline_velocity_days": {
        "label": "Pipeline Velocity (days)",
        "description": "Average days from lead to contract",
        "threshold": 14
    },
    "backlog_coverage_ratio": {
        "label": "Backlog Coverage Ratio",
        "description": "Signed revenue next 12 weeks ÷ avg weekly burn",
        "threshold": 1.5
    },
    "ar_30d_new": {
        "label": "New AR 30d",
        "description": "A/R entering 30-day bucket",
        "threshold": 10000
    },
    "ap_30_45_ratio": {
        "label": "AP 30-45 Ratio",
        "description": "A/P due 30-45 ÷ A/P due ≤ now",
        "threshold": 0.5
    },
    "real_time_CAC": {
        "label": "Real-time CAC",
        "description": "Qualified leads ÷ paid-lead spend",
        "threshold": 250
    },
    "runway_p5_weeks": {
        "label": "Runway P5 Weeks",
        "description": "5th-percentile runway weeks",
        "threshold": 8
    },
    "gp_per_job_drift": {
        "label": "GP/Job Drift",
        "description": "Δ true GP/job vs 3-month rolling avg",
        "threshold": -5
    },
    "price_cost_delta": {
        "label": "Price-Cost Delta",
        "description": "Supplier price index Δ – avg job price Δ",
        "threshold": -2
    }
}

def get_kpi_label(kpi_code):
    """Get the human-readable label for a KPI code"""
    return KPI_DEFINITIONS.get(kpi_code, {}).get("label", kpi_code)

def get_kpi_description(kpi_code):
    """Get the description for a KPI code"""
    return KPI_DEFINITIONS.get(kpi_code, {}).get("description", "")

def get_kpi_threshold(kpi_code):
    """Get the threshold value for a KPI code"""
    return KPI_DEFINITIONS.get(kpi_code, {}).get("threshold")

def get_kpi_status(kpi_code, value):
    """
    Determine the status of a KPI based on its value and threshold
    
    Returns:
        str: One of "critical", "warning", "good", "excellent"
    """
    threshold = get_kpi_threshold(kpi_code)
    
    if threshold is None:
        return "unknown"
    
    # KPIs where lower is better
    if kpi_code in ["pipeline_velocity_days", "real_time_CAC"]:
        if value > threshold * 1.5:
            return "critical"
        elif value > threshold:
            return "warning"
        elif value > threshold * 0.8:
            return "good"
        else:
            return "excellent"
    
    # KPIs where higher is better
    elif kpi_code in ["backlog_coverage_ratio", "runway_p5_weeks"]:
        if value < threshold * 0.5:
            return "critical"
        elif value < threshold:
            return "warning"
        elif value < threshold * 1.2:
            return "good"
        else:
            return "excellent"
    
    # KPIs with negative thresholds (higher is better)
    elif kpi_code in ["gp_per_job_drift", "price_cost_delta"]:
        if value < threshold * 1.5:
            return "critical"
        elif value < threshold:
            return "warning"
        elif value < 0:
            return "good"
        else:
            return "excellent"
    
    # KPIs with positive thresholds (lower is better)
    elif kpi_code in ["ar_30d_new", "ap_30_45_ratio"]:
        if value > threshold * 1.5:
            return "critical"
        elif value > threshold:
            return "warning"
        elif value > threshold * 0.5:
            return "good"
        else:
            return "excellent"
    
    # Default case
    return "unknown"

def get_all_kpis():
    """Get a list of all KPI codes"""
    return list(KPI_DEFINITIONS.keys())

def get_kpis_by_category(category):
    """
    Get KPIs filtered by category (financial, operational, etc.)
    
    This is a placeholder function - categories would be added to the
    KPI_DEFINITIONS dictionary in a real implementation.
    """
    # Placeholder categorization
    categories = {
        "financial": ["runway_p5_weeks", "gp_per_job_drift", "price_cost_delta"],
        "operational": ["pipeline_velocity_days", "backlog_coverage_ratio"],
        "collections": ["ar_30d_new", "ap_30_45_ratio"],
        "marketing": ["real_time_CAC"]
    }
    
    return categories.get(category, [])