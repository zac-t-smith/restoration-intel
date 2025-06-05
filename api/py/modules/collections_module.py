"""
Collections Module

This module handles accounts receivable management, collections tracking,
and DSO calculations for the Restoration CRM.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import engines and utils
from ..engines.timeline_ap import get_ap_recommendations
from ..utils import handle_error, Spinner, format_currency, safe_divide

def get_all_collections(filters=None):
    """
    Get all collections with optional filtering
    
    Args:
        filters: Optional dict of filter parameters
        
    Returns:
        List of collection objects
    """
    with Spinner("Collections"):
        try:
            # In a real implementation, this would query the database
            # For now, we'll just return sample data
            
            collections = [
                {
                    "id": 1,
                    "project_id": 1,
                    "description": "Initial Payment",
                    "amount": 6250.00,
                    "expected_date": datetime.now() - timedelta(days=20),
                    "status": "received",
                    "actual_date": datetime.now() - timedelta(days=20),
                    "confidence_percentage": 100,
                    "project_name": "Smith Water Damage",
                    "customer_name": "John Smith"
                },
                {
                    "id": 2,
                    "project_id": 1,
                    "description": "Final Payment",
                    "amount": 6250.00,
                    "expected_date": datetime.now() + timedelta(days=10),
                    "status": "pending",
                    "actual_date": None,
                    "confidence_percentage": 90,
                    "project_name": "Smith Water Damage",
                    "customer_name": "John Smith"
                },
                {
                    "id": 3,
                    "project_id": 2,
                    "description": "Initial Payment",
                    "amount": 9583.33,
                    "expected_date": datetime.now() - timedelta(days=30),
                    "status": "received",
                    "actual_date": datetime.now() - timedelta(days=32),
                    "confidence_percentage": 100,
                    "project_name": "Doe Fire Damage",
                    "customer_name": "Jane Doe"
                },
                {
                    "id": 4,
                    "project_id": 2,
                    "description": "Progress Payment",
                    "amount": 9583.33,
                    "expected_date": datetime.now() - timedelta(days=10),
                    "status": "received",
                    "actual_date": datetime.now() - timedelta(days=9),
                    "confidence_percentage": 100,
                    "project_name": "Doe Fire Damage",
                    "customer_name": "Jane Doe"
                },
                {
                    "id": 5,
                    "project_id": 2,
                    "description": "Final Payment",
                    "amount": 9583.34,
                    "expected_date": datetime.now() + timedelta(days=20),
                    "status": "pending",
                    "actual_date": None,
                    "confidence_percentage": 75,
                    "project_name": "Doe Fire Damage",
                    "customer_name": "Jane Doe"
                }
            ]
            
            # Apply filters if provided
            if filters:
                filtered_collections = []
                for collection in collections:
                    include = True
                    
                    # Filter by status
                    if 'status' in filters and collection['status'] != filters['status']:
                        include = False
                    
                    # Filter by date range
                    if 'start_date' in filters and collection['expected_date'] < filters['start_date']:
                        include = False
                    if 'end_date' in filters and collection['expected_date'] > filters['end_date']:
                        include = False
                    
                    # Filter by project
                    if 'project_id' in filters and collection['project_id'] != filters['project_id']:
                        include = False
                    
                    # Filter by confidence
                    if 'min_confidence' in filters and collection['confidence_percentage'] < filters['min_confidence']:
                        include = False
                    
                    if include:
                        filtered_collections.append(collection)
                
                return filtered_collections
            
            return collections
        
        except Exception as e:
            handle_error(f"Failed to get collections: {str(e)}", "collections_module")
            return []

def add_collection(data):
    """
    Add a new collection
    
    Args:
        data: Dictionary with collection data
        
    Returns:
        Dictionary with status and message
    """
    try:
        # In a real implementation, this would insert into the database
        return {
            "status": "success",
            "message": "Collection added successfully",
            "id": 123  # Mock ID
        }
    except Exception as e:
        handle_error(f"Failed to add collection: {str(e)}", "collections_module")
        return {
            "status": "error",
            "message": f"Failed to add collection: {str(e)}"
        }

def update_collection(id, data):
    """
    Update an existing collection
    
    Args:
        id: ID of the collection to update
        data: Dictionary with updated collection data
        
    Returns:
        Dictionary with status and message
    """
    try:
        # In a real implementation, this would update the database
        return {
            "status": "success",
            "message": f"Collection {id} updated successfully"
        }
    except Exception as e:
        handle_error(f"Failed to update collection: {str(e)}", "collections_module")
        return {
            "status": "error",
            "message": f"Failed to update collection: {str(e)}"
        }

def delete_collection(id):
    """
    Delete a collection
    
    Args:
        id: ID of the collection to delete
        
    Returns:
        Dictionary with status and message
    """
    try:
        # In a real implementation, this would delete from the database
        return {
            "status": "success",
            "message": f"Collection {id} deleted successfully"
        }
    except Exception as e:
        handle_error(f"Failed to delete collection: {str(e)}", "collections_module")
        return {
            "status": "error",
            "message": f"Failed to delete collection: {str(e)}"
        }

def get_collection_status_summary():
    """
    Get summary of collections by status
    
    Returns:
        Dictionary with counts and amounts by status
    """
    with Spinner("Collection Summary"):
        try:
            collections = get_all_collections()
            
            # Initialize summary
            summary = {
                "received": {"count": 0, "amount": 0},
                "pending": {"count": 0, "amount": 0},
                "overdue": {"count": 0, "amount": 0},
                "total": {"count": 0, "amount": 0}
            }
            
            # Calculate summary
            now = datetime.now()
            for collection in collections:
                status = collection["status"]
                
                # Check if pending and overdue
                if status == "pending" and collection["expected_date"] < now:
                    status = "overdue"
                
                # Increment counts and amounts
                if status in summary:
                    summary[status]["count"] += 1
                    summary[status]["amount"] += collection["amount"]
                
                # Add to total
                summary["total"]["count"] += 1
                summary["total"]["amount"] += collection["amount"]
            
            return summary
        
        except Exception as e:
            handle_error(f"Failed to get collection status summary: {str(e)}", "collections_module")
            return {}

def get_aging_analysis():
    """
    Get aging analysis of collections
    
    Returns:
        Dictionary with aging buckets and amounts
    """
    with Spinner("Aging Analysis"):
        try:
            collections = get_all_collections({"status": "pending"})
            
            # Initialize aging buckets
            aging = {
                "current": {"count": 0, "amount": 0},
                "1_30": {"count": 0, "amount": 0},
                "31_60": {"count": 0, "amount": 0},
                "61_90": {"count": 0, "amount": 0},
                "90_plus": {"count": 0, "amount": 0},
                "total": {"count": 0, "amount": 0}
            }
            
            # Calculate aging
            now = datetime.now()
            for collection in collections:
                expected_date = collection["expected_date"]
                days_diff = (now - expected_date).days if expected_date < now else -1
                
                # Determine bucket
                bucket = "current"
                if days_diff >= 0 and days_diff <= 30:
                    bucket = "1_30"
                elif days_diff > 30 and days_diff <= 60:
                    bucket = "31_60"
                elif days_diff > 60 and days_diff <= 90:
                    bucket = "61_90"
                elif days_diff > 90:
                    bucket = "90_plus"
                
                # Increment counts and amounts
                aging[bucket]["count"] += 1
                aging[bucket]["amount"] += collection["amount"]
                
                # Add to total
                aging["total"]["count"] += 1
                aging["total"]["amount"] += collection["amount"]
            
            return aging
        
        except Exception as e:
            handle_error(f"Failed to get aging analysis: {str(e)}", "collections_module")
            return {}

def calculate_days_sales_outstanding():
    """
    Calculate the Days Sales Outstanding (DSO) using real period instead of fixed 30 days
    
    Returns:
        The DSO value (float)
    """
    with Spinner("DSO Calculation"):
        try:
            # Get paid collections from the last 90 days to determine real period
            now = datetime.now()
            start_date = now - timedelta(days=90)
            
            # In a real implementation, this would query the database
            # For now, we'll use our sample data
            collections = get_all_collections()
            
            # Filter to received collections within period
            paid_collections = [c for c in collections if c["status"] == "received" and c["actual_date"] >= start_date]
            
            if not paid_collections:
                handle_error("No paid collections found in the last 90 days", "collections_module")
                return 0
            
            # Calculate the real period by finding earliest and latest payment dates
            dates = [c["actual_date"] for c in paid_collections]
            earliest_date = min(dates)
            latest_date = max(dates)
            
            real_period_days = (latest_date - earliest_date).days
            if real_period_days <= 0:
                real_period_days = 1  # Avoid division by zero
            
            # Calculate total revenue in the period
            total_revenue = sum(c["amount"] for c in paid_collections)
            
            # Get current accounts receivable (pending collections)
            pending_collections = [c for c in collections if c["status"] == "pending"]
            accounts_receivable = sum(c["amount"] for c in pending_collections)
            
            # Calculate average daily revenue based on real period
            daily_revenue = total_revenue / real_period_days
            
            # Calculate DSO
            if daily_revenue <= 0:
                return 0
                
            dso = accounts_receivable / daily_revenue
            
            return dso
        
        except Exception as e:
            handle_error(f"Failed to calculate DSO: {str(e)}", "collections_module")
            return 0

def get_expected_inflows(days=90):
    """
    Get expected cash inflows for the specified number of days
    
    Args:
        days: Number of days to forecast
        
    Returns:
        List of expected inflows with dates and amounts
    """
    with Spinner("Expected Inflows"):
        try:
            # Get pending collections
            collections = get_all_collections({"status": "pending"})
            
            # Filter to collections within forecast period
            end_date = datetime.now() + timedelta(days=days)
            forecast_collections = [c for c in collections if c["expected_date"] <= end_date]
            
            # Calculate expected inflows
            inflows = []
            for collection in forecast_collections:
                # Apply confidence percentage
                expected_amount = collection["amount"] * (collection["confidence_percentage"] / 100)
                
                inflows.append({
                    "id": collection["id"],
                    "description": collection["description"],
                    "project_name": collection["project_name"],
                    "customer_name": collection["customer_name"],
                    "date": collection["expected_date"],
                    "amount": collection["amount"],
                    "expected_amount": expected_amount,
                    "confidence": collection["confidence_percentage"]
                })
            
            # Sort by date
            inflows.sort(key=lambda x: x["date"])
            
            return inflows
        
        except Exception as e:
            handle_error(f"Failed to get expected inflows: {str(e)}", "collections_module")
            return []

def get_collection_metrics():
    """
    Get collection performance metrics
    
    Returns:
        Dictionary with collection metrics
    """
    with Spinner("Collection Metrics"):
        try:
            collections = get_all_collections()
            
            # Filter to received collections
            received = [c for c in collections if c["status"] == "received"]
            
            if not received:
                return {
                    "dso": 0,
                    "avg_days_to_collect": 0,
                    "on_time_percentage": 0,
                    "total_collected": 0,
                    "total_pending": 0
                }
            
            # Calculate metrics
            total_days_to_collect = 0
            on_time_count = 0
            
            for collection in received:
                expected_date = collection["expected_date"]
                actual_date = collection["actual_date"]
                
                if actual_date and expected_date:
                    days_to_collect = (actual_date - expected_date).days
                    total_days_to_collect += max(0, days_to_collect)
                    
                    # Count on-time collections (collected on or before expected date)
                    if actual_date <= expected_date:
                        on_time_count += 1
            
            avg_days_to_collect = total_days_to_collect / len(received)
            on_time_percentage = (on_time_count / len(received)) * 100
            
            # Calculate DSO using real period
            dso = calculate_days_sales_outstanding()
            
            # Calculate totals
            total_collected = sum(c["amount"] for c in received)
            total_pending = sum(c["amount"] for c in collections if c["status"] == "pending")
            
            return {
                "dso": dso,
                "avg_days_to_collect": avg_days_to_collect,
                "on_time_percentage": on_time_percentage,
                "total_collected": total_collected,
                "total_pending": total_pending
            }
        
        except Exception as e:
            handle_error(f"Failed to get collection metrics: {str(e)}", "collections_module")
            return {}

# Main function to render the collections module
def render_collections(context=None):
    """Main function to render the collections module in a web context"""
    try:
        # Get collection data
        collections = get_all_collections()
        
        # Get collection status summary
        status_summary = get_collection_status_summary()
        
        # Get aging analysis
        aging = get_aging_analysis()
        
        # Get collection metrics
        metrics = get_collection_metrics()
        
        # Get expected inflows
        inflows = get_expected_inflows()
        
        # Get timeline-based AP recommendations
        # This is a key change - using the new timeline engine instead of weighted-score
        ap_recommendations = get_ap_recommendations()
        
        return {
            "collections": collections,
            "status_summary": status_summary,
            "aging": aging,
            "metrics": metrics,
            "inflows": inflows,
            "ap_recommendations": ap_recommendations
        }
    except Exception as e:
        handle_error(f"Failed to render collections module: {str(e)}", "collections_module")
        return {"error": str(e)}