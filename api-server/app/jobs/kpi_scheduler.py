from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from ..services.growth_accelerator import (
    detect_revenue_leaks,
    detect_operational_bottlenecks,
    detect_capital_inefficiencies
)

def run_kpi_calculations():
    """Run all KPI calculations and metrics analysis"""
    try:
        # Run revenue leak detection
        revenue_leaks = detect_revenue_leaks()
        
        # Run operational bottleneck detection
        bottlenecks = detect_operational_bottlenecks()
        
        # Run capital inefficiency detection
        inefficiencies = detect_capital_inefficiencies()
        
        return {
            'revenue_leaks': revenue_leaks,
            'bottlenecks': bottlenecks,
            'inefficiencies': inefficiencies
        }
    except Exception as e:
        print(f"Error running KPI calculations: {str(e)}")
        return None

def start_scheduler():
    """Start the KPI calculation scheduler"""
    scheduler = BackgroundScheduler()
    
    # Run KPI calculations every hour
    scheduler.add_job(
        run_kpi_calculations,
        trigger=CronTrigger(hour='*'),
        id='kpi_calculations',
        name='Run KPI calculations hourly',
        replace_existing=True
    )
    
    scheduler.start()