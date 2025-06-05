/**
 * Vendor API Service
 * 
 * Provides methods for interacting with the vendor API endpoints
 */

import { Vendor, VendorInput } from '../models/vendor';

/**
 * Base API URL from environment variable
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/py';

/**
 * Get all vendors
 * 
 * @returns Promise with array of vendors
 */
export async function getVendors(): Promise<Vendor[]> {
  try {
    const response = await fetch(`${API_URL}/vendors`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch vendors: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching vendors:', error);
    throw error;
  }
}

/**
 * Get a vendor by ID
 * 
 * @param id - Vendor ID
 * @returns Promise with vendor details
 */
export async function getVendor(id: number): Promise<Vendor> {
  try {
    const response = await fetch(`${API_URL}/vendors/${id}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch vendor: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching vendor ${id}:`, error);
    throw error;
  }
}

/**
 * Create a new vendor
 * 
 * @param vendor - Vendor data to create
 * @returns Promise with created vendor
 */
export async function createVendor(vendor: VendorInput): Promise<Vendor> {
  try {
    const response = await fetch(`${API_URL}/vendors`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(vendor),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create vendor: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating vendor:', error);
    throw error;
  }
}

/**
 * Update an existing vendor
 * 
 * @param id - Vendor ID
 * @param vendor - Updated vendor data
 * @returns Promise with updated vendor
 */
export async function updateVendor(id: number, vendor: VendorInput): Promise<Vendor> {
  try {
    const response = await fetch(`${API_URL}/vendors/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(vendor),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update vendor: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error updating vendor ${id}:`, error);
    throw error;
  }
}

/**
 * Delete a vendor
 * 
 * @param id - Vendor ID
 * @returns Promise with deletion status
 */
export async function deleteVendor(id: number): Promise<{ success: boolean }> {
  try {
    const response = await fetch(`${API_URL}/vendors/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete vendor: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error deleting vendor ${id}:`, error);
    throw error;
  }
}

/**
 * Get vendor payment summary statistics
 * 
 * @param id - Vendor ID
 * @returns Promise with vendor payment statistics
 */
export async function getVendorPaymentStats(id: number): Promise<{
  total_spend: number;
  average_payment_time: number;
  payment_history: Array<{ date: string; amount: number; days_to_payment: number }>;
}> {
  try {
    const response = await fetch(`${API_URL}/vendors/${id}/payment-stats`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch vendor payment stats: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching payment stats for vendor ${id}:`, error);
    throw error;
  }
}

/**
 * Get vendor expenses
 * 
 * @param id - Vendor ID
 * @returns Promise with vendor expenses
 */
export async function getVendorExpenses(id: number): Promise<any[]> {
  try {
    const response = await fetch(`${API_URL}/vendors/${id}/expenses`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch vendor expenses: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching expenses for vendor ${id}:`, error);
    throw error;
  }
}