/**
 * Vendor model interface
 * 
 * Represents a vendor entity in the system with payment terms and contact information
 */

export interface Vendor {
  id: number;
  name: string;
  payment_terms: string;
  contact: string;
  created_at: string;
  sla_days?: number; // Optional service level agreement days
  notes?: string;   // Optional notes
}

/**
 * Create/Update Vendor DTO
 */
export interface VendorInput {
  name: string;
  payment_terms: number;
  contact: string | null;
  sla_days?: number;
  notes?: string | null;
}

/**
 * Vendor with relationship information
 */
export interface VendorWithRelationship extends Vendor {
  relationship_type: 'standard' | 'critical' | 'preferred';
  total_spend: number;
  average_payment_time: number;
  active_expenses_count: number;
}

/**
 * Payment terms options
 */
export const PAYMENT_TERMS_OPTIONS = [
  { value: 15, label: 'Net 15' },
  { value: 30, label: 'Net 30' },
  { value: 45, label: 'Net 45' },
  { value: 60, label: 'Net 60' },
  { value: 0, label: 'Critical Vendor (Immediate)' },
  { value: 10, label: 'Early Payment Discount' },
  { value: 20, label: 'Preferred Vendor' },
];