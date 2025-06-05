#!/usr/bin/env python3
"""
Jobs Runner CLI

This script runs all the background jobs and engines in sequence,
including the leading indicator engine, AP prioritization, and growth accelerator.
It can be run manually or scheduled as a cron job.
"""
import sys
import argparse
import asyncio
import httpx
from datetime import datetime
from typing import List, Dict, Any
from api.py.engines.leading_indicator_engine import run_all_indicators
from api.py.modules.expenses_module import get_vendor_recommendations
from api.py.growth_accelerator import generate_growth_insights
from api.py.utils import handle_error, Spinner

async def main_async():
    """Async main function to run all jobs"""
    parser = argparse.ArgumentParser(description="Run Restoration-Intel background jobs")
    parser.add_argument("--job", choices=["all", "indicators", "ap", "growth"], default="all",
                       help="Specify which job to run (default: all)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    def log(message):
        if args.verbose:
            print(message)
    
    results = {
        "indicators": {"status": "not_run", "error": None, "data": None},
        "ap": {"status": "not_run", "error": None, "data": None},
        "growth": {"status": "not_run", "error": None, "data": None}
    }
    
    async with httpx.AsyncClient() as client:
        # Run Leading Indicator Engine
        if args.job in ["all", "indicators"]:
            log("Running Leading Indicator Engine...")
            try:
                indicators = await run_all_indicators()
                log(f"Successfully calculated {len(indicators)} leading indicators")
                
                breached = [i for i in indicators if i.get("breach")]
                if breached:
                    log(f"Found {len(breached)} breached indicators:")
                    for indicator in breached:
                        log(f"  - {indicator['kpi_code']}: {indicator['value']:.2f}")
                
                results["indicators"] = {"status": "success", "error": None, "data": indicators}
            except Exception as e:
                handle_error(f"Error in leading indicators: {str(e)}", "jobs_runner")
                results["indicators"] = {"status": "error", "error": str(e), "data": None}

        # Run AP Prioritization
        if args.job in ["all", "ap"]:
            log("Running AP Prioritization...")
            try:
                recommendations = await get_vendor_recommendations(client)
                log(f"Generated {len(recommendations)} vendor recommendations")
                results["ap"] = {"status": "success", "error": None, "data": recommendations}
            except Exception as e:
                handle_error(f"Error in AP prioritization: {str(e)}", "jobs_runner")
                results["ap"] = {"status": "error", "error": str(e), "data": None}

        # Run Growth Insights
        if args.job in ["all", "growth"]:
            log("Running Growth Insights...")
            try:
                insights = await generate_growth_insights()
                log(f"Generated {len(insights)} growth insights")
                results["growth"] = {"status": "success", "error": None, "data": insights}
            except Exception as e:
                handle_error(f"Error in growth insights: {str(e)}", "jobs_runner")
                results["growth"] = {"status": "error", "error": str(e), "data": None}
    
    return results

def main():
    """Main entry point"""
    try:
        results = asyncio.run(main_async())
        sys.exit(0 if all(r["status"] == "success" for r in results.values()) else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        handle_error(f"Unexpected error: {str(e)}", "jobs_runner")
        sys.exit(1)

if __name__ == "__main__":
    main()