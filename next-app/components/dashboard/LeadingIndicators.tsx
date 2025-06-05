/**
 * Leading Indicators Component
 * 
 * Displays critical leading indicators with trend visualization and actionable recommendations
 */

'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { getLeadingIndicators, runLeadingIndicatorsCalculation } from '@/lib/services/kpiService';
import { useToast } from '@/components/ui/use-toast';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[250px] flex items-center justify-center">
      <Skeleton className="w-full h-full" />
    </div>
  )
});

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

interface LeadingIndicatorsProps {
  initialData?: LeadingIndicator[];
  loading?: boolean;
}

export default function LeadingIndicators({
  initialData,
  loading: initialLoading = false
}: LeadingIndicatorsProps) {
  const [indicators, setIndicators] = useState<LeadingIndicator[]>(initialData || []);
  const [loading, setLoading] = useState(initialLoading);
  const [calculating, setCalculating] = useState(false);
  const [selectedIndicator, setSelectedIndicator] = useState<LeadingIndicator | null>(null);
  
  const { toast } = useToast();
  
  const fetchIndicators = async () => {
    setLoading(true);
    try {
      const data = await getLeadingIndicators(true);
      setIndicators(data);
    } catch (error) {
      console.error('Error fetching leading indicators:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch leading indicators',
        variant: 'error',
      });
    } finally {
      setLoading(false);
    }
  };
  
  const runCalculation = async () => {
    setCalculating(true);
    try {
      const result = await runLeadingIndicatorsCalculation();
      toast({
        title: 'Calculation Complete',
        description: `${result.calculated_count} indicators calculated. ${result.breach_count} breaches detected.`,
        variant: result.breach_count > 0 ? 'error' : 'default',
      });
      
      // Refresh the indicators list
      fetchIndicators();
    } catch (error) {
      console.error('Error running leading indicators calculation:', error);
      toast({
        title: 'Error',
        description: 'Failed to run calculation',
        variant: 'error',
      });
    } finally {
      setCalculating(false);
    }
  };
  
  // Generate sample plot data for the selected indicator
  const generatePlotData = (indicator: LeadingIndicator) => {
    // This would typically come from an API with historical data
    // Using sample data for now
    const dates = [];
    const values = [];
    const threshold = [];
    
    // Generate 12 weeks of data
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i * 7);
      dates.push(date.toISOString().split('T')[0]);
      
      // Generate sample values with a breach at the end
      let value;
      if (i < 10) {
        // Normal values
        value = Math.random() * 0.2 + 0.7; // Between 0.7 and 0.9
      } else {
        // Values approaching and then breaching the threshold
        value = Math.random() * 0.3 + 0.4; // Between 0.4 and 0.7
      }
      
      // Scale the value based on the indicator's current value
      value = value * (indicator.value * 1.5);
      values.push(value);
      
      // Constant threshold line
      threshold.push(indicator.value);
    }
    
    return {
      dates,
      values,
      threshold
    };
  };
  
  const indicatorDescriptions: Record<string, string> = {
    'pipeline_velocity_days': 'Average days from Bid to Contract',
    'backlog_coverage_ratio': 'Signed work for next 12 weeks ÷ average weekly burn',
    'ar_30d_new': 'AR that just crossed the 30-day threshold',
    'ap_30-45_ratio': 'AP due in 30-45 days ÷ AP due now or earlier',
    'real_time_CAC': 'Qualified leads ÷ paid-lead spend',
    'runway_p5_weeks': '5-percentile cash-out weeks (Monte-Carlo)',
    'gp_per_job_drift': 'Change in GP/job vs 3-month rolling average',
    'price_cost_delta': 'Supplier price index change – Average job price change'
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Leading Indicators</h2>
        <Button 
          onClick={runCalculation} 
          disabled={calculating}
          size="sm"
        >
          {calculating ? 'Calculating...' : 'Run Calculation'}
        </Button>
      </div>
      
      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Alert key={i} className="border-l-4 border-l-gray-300">
              <AlertTitle>
                <Skeleton className="h-4 w-36" />
              </AlertTitle>
              <AlertDescription>
                <div className="mt-2 space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-5/6" />
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      ) : indicators.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-6">
              <p className="text-gray-500">No leading indicators in breach</p>
              <p className="text-sm text-gray-400 mt-1">All systems operating within normal parameters</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column: Alert list */}
          <div className="space-y-4">
            {indicators.map((indicator) => (
              <Alert 
                key={indicator.id} 
                className={`border-l-4 border-l-red-500 cursor-pointer transition-all ${selectedIndicator?.id === indicator.id ? 'ring-2 ring-blue-300' : 'hover:bg-gray-50'}`}
                onClick={() => setSelectedIndicator(indicator)}
              >
                <AlertTitle className="flex items-center">
                  <span className="mr-2">Critical Leading Indicator:</span>
                  <Badge variant="destructive">{indicator.kpi_code}</Badge>
                </AlertTitle>
                <AlertDescription>
                  <p className="text-sm text-gray-500 mt-1">
                    {indicatorDescriptions[indicator.kpi_code] || indicator.kpi_code}
                  </p>
                  <div className="mt-2">
                    <p className="font-medium">Current Value: <span className="text-red-600">{indicator.value.toFixed(2)}</span></p>
                    <p className="text-xs text-gray-500 mt-1">Last calculated: {new Date(indicator.calculated_at).toLocaleString()}</p>
                  </div>
                </AlertDescription>
              </Alert>
            ))}
          </div>
          
          {/* Right column: Selected indicator details */}
          {selectedIndicator && (
            <Card>
              <CardHeader>
                <CardTitle>{selectedIndicator.kpi_code}</CardTitle>
                <CardDescription>
                  {indicatorDescriptions[selectedIndicator.kpi_code] || selectedIndicator.kpi_code}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Trend visualization */}
                <div className="mb-4">
                  {(() => {
                    const plotData = generatePlotData(selectedIndicator);
                    return (
                      <Plot
                        data={[
                          {
                            x: plotData.dates,
                            y: plotData.values,
                            type: 'scatter',
                            mode: 'lines+markers',
                            name: 'Value',
                            line: {
                              color: 'rgba(59, 130, 246, 0.8)', // blue-500
                              width: 2
                            }
                          },
                          {
                            x: plotData.dates,
                            y: plotData.threshold,
                            type: 'scatter',
                            mode: 'lines',
                            name: 'Threshold',
                              // Use type assertion to work around incomplete typings
                              line: {
                                color: 'rgba(239, 68, 68, 0.6)', // red-500
                                width: 2,
                                // Typings don't include dash, but it works at runtime
                              } as any
                            }
                          ]}
                          layout={{
                            title: '12-Week Trend',
                            height: 250,
                            margin: {
                              l: 40,
                              r: 20,
                              t: 30,
                              b: 40
                            },
                            // These properties belong inside the layout object
                            yaxis: {
                              title: 'Value'
                            },
                            legend: {
                              orientation: 'h',
                              y: -0.2
                            },
                            autosize: true
                            // Use any type to bypass incomplete Plotly typings
                          } as any}
                          config={{
                            responsive: true,
                            displayModeBar: false
                        }}
                        className="w-full"
                      />
                    );
                  })()}
                </div>
                
                {/* Playbook */}
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-2">Recommended Action Plan</h3>
                  
                  <div className="bg-gray-50 p-4 rounded-md space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900">Action</h4>
                      <p className="text-gray-700">{selectedIndicator.playbook_json.action}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900">Rationale</h4>
                      <p className="text-gray-700">{selectedIndicator.playbook_json.rationale}</p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900">Expected Impact</h4>
                      <p className="text-gray-700">{selectedIndicator.playbook_json.expected_impact}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}