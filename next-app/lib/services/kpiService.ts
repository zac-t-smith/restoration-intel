/**
 * KPI Service
 * 
 * Service for fetching KPI data from the FastAPI backend
 */

interface KpiValue {
  value: number;
  status: 'critical' | 'warning' | 'good' | 'excellent';
  formatted_value: string;
  trend?: number;
  trend_direction?: 'up' | 'down' | 'flat';
}

export interface Kpi {
  code: string;
  name: string;
  description: string;
  category: string;
  value: KpiValue;
  thresholds: {
    critical: number;
    warning: number;
    good: number;
    excellent: number;
  };
}

interface LeadingIndicator {
  id: number;
  kpi_code: string;
  value: number;
  breach: boolean;
  playbook_json: {
    action: string;
    rationale: string;
    expected_impact: string;
  };
  calculated_at: string;
}

/**
 * Fetch KPIs by category
 * @param category The KPI category to fetch (financial, operational, marketing, customer)
 * @returns A promise that resolves to an array of KPIs
 */
export async function getKpisByCategory(category: string): Promise<Kpi[]> {
  try {
    const response = await fetch(`/api/py/kpi/by-category/${category}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching KPIs: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.kpis || [];
  } catch (error) {
    console.error(`Failed to fetch ${category} KPIs:`, error);
    throw error;
  }
}

/**
 * Fetch all KPIs
 * @returns A promise that resolves to an array of all KPIs
 */
export async function getAllKpis(): Promise<Kpi[]> {
  try {
    const categories = ['financial', 'operational', 'marketing', 'customer'];
    const kpiPromises = categories.map(category => getKpisByCategory(category));
    const kpiArrays = await Promise.all(kpiPromises);
    
    // Flatten the arrays of KPIs from each category
    return kpiArrays.flat();
  } catch (error) {
    console.error('Failed to fetch all KPIs:', error);
    throw error;
  }
}

/**
 * Fetch KPI trend data
 * @param kpiCode The KPI code to fetch trend data for
 * @param months The number of months of historical data to fetch
 * @returns A promise that resolves to an array of monthly KPI values
 */
export async function getKpiTrend(kpiCode: string, months: number = 12): Promise<any[]> {
  try {
    const response = await fetch(`/api/py/kpi/trend/${kpiCode}?months=${months}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching KPI trend: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.trend_data || [];
  } catch (error) {
    console.error(`Failed to fetch trend data for ${kpiCode}:`, error);
    throw error;
  }
}

/**
 * Fetch leading indicators
 * @param breachedOnly Whether to fetch only indicators in breach
 * @returns A promise that resolves to an array of leading indicators
 */
export async function getLeadingIndicators(breachedOnly: boolean = false): Promise<LeadingIndicator[]> {
  try {
    const queryParam = breachedOnly ? '?breached_only=true' : '';
    const response = await fetch(`/api/py/leading-indicators${queryParam}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching leading indicators: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.indicators || [];
  } catch (error) {
    console.error('Failed to fetch leading indicators:', error);
    throw error;
  }
}

/**
 * Manually trigger the leading indicators calculation
 * @returns A promise that resolves to the calculation summary
 */
export async function runLeadingIndicatorsCalculation(): Promise<any> {
  try {
    const response = await fetch('/api/py/leading-indicators/run');
    
    if (!response.ok) {
      throw new Error(`Error running leading indicators calculation: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to run leading indicators calculation:', error);
    throw error;
  }
}

/**
 * Fetch lead-to-revenue funnel data
 * @returns A promise that resolves to the funnel data
 */
export async function getLeadToRevenueFunnel(): Promise<{
  leads: number;
  qualified: number;
  billable: number;
  collected: number;
}> {
  try {
    const response = await fetch('/api/py/kpi/lead-to-revenue-funnel');
    
    if (!response.ok) {
      throw new Error(`Error fetching lead-to-revenue funnel: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.funnel || {
      leads: 0,
      qualified: 0,
      billable: 0,
      collected: 0
    };
  } catch (error) {
    console.error('Failed to fetch lead-to-revenue funnel:', error);
    throw error;
  }
}

/**
 * Fetch rolling KPI trend data for the dashboard
 * @param months The number of months of historical data to fetch
 * @returns A promise that resolves to the monthly KPI data
 */
export async function getRollingKpiTrend(months: number = 12): Promise<any[]> {
  try {
    const response = await fetch(`/api/py/kpi/rolling-trend?months=${months}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching rolling KPI trend: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.monthly_data || [];
  } catch (error) {
    console.error('Failed to fetch rolling KPI trend:', error);
    throw error;
  }
}