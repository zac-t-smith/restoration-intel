/**
 * Dashboard Content Component
 * 
 * Client component that fetches data and renders the dashboard content
 */

'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import LeadToRevenueFunnel from '@/components/dashboard/LeadToRevenueFunnel';
import RollingKpiTrend from '@/components/dashboard/RollingKpiTrend';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { getKpisByCategory, getLeadToRevenueFunnel, getRollingKpiTrend, getLeadingIndicators, Kpi } from '@/lib/services/kpiService';

export default function DashboardContent() {
  // State for different data sets
  const [financialKpis, setFinancialKpis] = useState<Kpi[]>([]);
  const [funnelData, setFunnelData] = useState<any>(null);
  const [kpiTrendData, setKpiTrendData] = useState<any[]>([]);
  const [leadingIndicators, setLeadingIndicators] = useState<any[]>([]);
  const [loading, setLoading] = useState({
    kpis: true,
    funnel: true,
    trends: true,
    indicators: true
  });

  // Fetch data on component mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch financial KPIs
        const financialKpisData = await getKpisByCategory('financial');
        setFinancialKpis(financialKpisData);
        setLoading(prev => ({ ...prev, kpis: false }));

        // Fetch funnel data
        const funnelData = await getLeadToRevenueFunnel();
        setFunnelData(funnelData);
        setLoading(prev => ({ ...prev, funnel: false }));

        // Fetch KPI trend data
        const trendData = await getRollingKpiTrend();
        setKpiTrendData(trendData);
        setLoading(prev => ({ ...prev, trends: false }));

        // Fetch leading indicators in breach
        const indicators = await getLeadingIndicators(true);
        setLeadingIndicators(indicators);
        setLoading(prev => ({ ...prev, indicators: false }));
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Set loading to false even if there's an error
        setLoading({
          kpis: false,
          funnel: false,
          trends: false,
          indicators: false
        });
      }
    };

    fetchDashboardData();
  }, []);

  // Helper function to get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'good': return 'bg-green-100 text-green-800 border-green-200';
      case 'excellent': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Alert Banners for Leading Indicators in breach */}
      {!loading.indicators && leadingIndicators.length > 0 && (
        <div className="space-y-2">
          {leadingIndicators.map((indicator) => (
            <Alert 
              key={indicator.id} 
              className="border-l-4 border-l-red-500"
            >
              <AlertTitle className="flex items-center">
                <span className="mr-2">Critical Leading Indicator:</span>
                <Badge variant="destructive">{indicator.kpi_code}</Badge>
              </AlertTitle>
              <AlertDescription>
                <div className="mt-2">
                  <p className="font-medium">Recommended Action:</p>
                  <p>{indicator.playbook_json.action}</p>
                  
                  <p className="font-medium mt-2">Rationale:</p>
                  <p>{indicator.playbook_json.rationale}</p>
                  
                  <p className="font-medium mt-2">Expected Impact:</p>
                  <p>{indicator.playbook_json.expected_impact}</p>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading.kpis ? (
          // KPI skeleton loaders
          Array(4).fill(0).map((_, i) => (
            <Card key={i} className="shadow-sm">
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-10 w-2/3 mb-2" />
                <Skeleton className="h-4 w-1/3" />
              </CardContent>
            </Card>
          ))
        ) : (
          // Actual KPI cards
          financialKpis.slice(0, 4).map((kpi) => (
            <Card key={kpi.code} className={`shadow-sm border-l-4 ${getStatusColor(kpi.value.status)}`}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500">{kpi.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{kpi.value.formatted_value}</div>
                <p className="text-xs text-gray-500">{kpi.description}</p>
                {kpi.value.trend && (
                  <div className={`text-xs mt-1 ${kpi.value.trend_direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {kpi.value.trend_direction === 'up' ? '↑' : '↓'} {kpi.value.trend}% from last period
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Lead-to-Revenue Funnel */}
      <LeadToRevenueFunnel data={funnelData} loading={loading.funnel} />

      {/* Rolling KPI Trend */}
      <RollingKpiTrend data={kpiTrendData} loading={loading.trends} />

      {/* LTV/CAC Ratio */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Customer Economics</CardTitle>
          <CardDescription>Real-time LTV/CAC ratio and unit economics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-500">Customer Lifetime Value</p>
              <p className="text-3xl font-bold text-blue-600">$18,500</p>
              <p className="text-xs text-gray-400">Based on 24-month retention</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-500">Customer Acquisition Cost</p>
              <p className="text-3xl font-bold text-amber-600">$2,120</p>
              <p className="text-xs text-gray-400">Avg across all channels</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-500">LTV:CAC Ratio</p>
              <p className="text-3xl font-bold text-green-600">8.7x</p>
              <p className="text-xs text-gray-400">Target &gt; 3.0x</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}