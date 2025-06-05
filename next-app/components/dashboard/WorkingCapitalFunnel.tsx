/**
 * Working-Capital Funnel Component
 * 
 * Visualizes the company's cash cycle including days-to-invoice, 
 * days-to-collect (DSO), days-to-pay (DPO) and the resulting cash gap
 */

'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[300px] flex items-center justify-center">
      <Skeleton className="w-full h-full" />
    </div>
  )
});

interface WaterFallData {
  days_to_invoice: number;
  days_to_collect: number; // DSO
  days_to_pay: number; // DPO
  cash_gap: number;
  trend: {
    months: string[];
    days_to_invoice: number[];
    days_to_collect: number[];
    days_to_pay: number[];
    cash_gap: number[];
  };
}

// Hard-coded sample data (would come from API in real implementation)
const sampleData: WaterFallData = {
  days_to_invoice: 5.2,
  days_to_collect: 32.8, // DSO
  days_to_pay: 21.5, // DPO
  cash_gap: 16.5,
  trend: {
    months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    days_to_invoice: [6.1, 5.8, 5.5, 5.3, 5.2, 5.2],
    days_to_collect: [35.2, 34.5, 33.7, 33.2, 32.8, 32.8],
    days_to_pay: [20.8, 21.0, 21.2, 21.4, 21.5, 21.5],
    cash_gap: [20.5, 19.3, 18.0, 17.1, 16.5, 16.5]
  }
};

export default function WorkingCapitalFunnel() {
  const [data, setData] = useState<WaterFallData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>('waterfall');
  
  // Fetch data (simulated)
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      // Simulate API call
      setTimeout(() => {
        setData(sampleData);
        setLoading(false);
      }, 500);
    };
    
    fetchData();
  }, []);
  
  // Get trend status badge for cash gap
  const getTrendStatus = (current: number, previous: number) => {
    const diff = current - previous;
    const percentChange = (diff / previous) * 100;
    
    if (percentChange <= -5) {
      return <Badge variant="success">Improving ({percentChange.toFixed(1)}%)</Badge>;
    } else if (percentChange >= 5) {
      return <Badge variant="destructive">Worsening ({percentChange.toFixed(1)}%)</Badge>;
    } else {
      return <Badge variant="secondary">Stable ({percentChange.toFixed(1)}%)</Badge>;
    }
  };
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Working-Capital Funnel</CardTitle>
        <CardDescription>
          Visualize your order-to-cash and procure-to-pay cycles
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="waterfall" value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-4">
            <TabsTrigger value="waterfall">Cash Gap Waterfall</TabsTrigger>
            <TabsTrigger value="trend">Historical Trend</TabsTrigger>
            <TabsTrigger value="details">Metric Details</TabsTrigger>
          </TabsList>
          
          <TabsContent value="waterfall">
            {loading ? (
              <div className="w-full h-[300px] flex items-center justify-center">
                <Skeleton className="w-full h-full" />
              </div>
            ) : data ? (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium">Cash Gap: {data.cash_gap.toFixed(1)} days</h3>
                  {getTrendStatus(data.cash_gap, data.trend.cash_gap[data.trend.cash_gap.length - 2])}
                </div>
                
                <Plot
                  data={[
                    {
                      type: 'waterfall',
                      orientation: 'v',
                      measure: ['absolute', 'relative', 'relative', 'total'],
                      x: ['Project Completion', 'Days to Invoice', 'Days to Collect', 'Cash Gap'],
                      y: [0, data.days_to_invoice, data.days_to_collect, data.cash_gap],
                      text: [
                        'Start',
                        `+${data.days_to_invoice.toFixed(1)} days`,
                        `+${data.days_to_collect.toFixed(1)} days`,
                        `${data.cash_gap.toFixed(1)} days`
                      ],
                      textposition: 'outside',
                      decreasing: { marker: { color: 'rgba(59, 130, 246, 0.8)' } }, // blue-500
                      increasing: { marker: { color: 'rgba(239, 68, 68, 0.8)' } }, // red-500
                      totals: { marker: { color: 'rgba(16, 185, 129, 0.8)' } }, // green-500
                      connector: {
                        line: {
                          color: 'rgb(107, 114, 128)',
                          width: 1
                        }
                      }
                    } as any
                  ]}
                  layout={{
                    title: 'Cash Gap Analysis',
                    height: 300,
                    margin: {
                      l: 40,
                      r: 20,
                      t: 30,
                      b: 40
                    },
                    yaxis: {
                      title: 'Days',
                      zeroline: true
                    },
                    showlegend: false,
                    annotations: [
                      {
                        x: 1,
                        y: data.days_to_invoice + data.days_to_collect + 10,
                        text: `DPO: ${data.days_to_pay.toFixed(1)} days`,
                        showarrow: true,
                        arrowhead: 2,
                        arrowcolor: 'rgba(16, 185, 129, 0.8)',
                        arrowsize: 1,
                        arrowwidth: 2,
                        ax: 0,
                        ay: -40
                      }
                    ]
                  } as any}
                  config={{
                    responsive: true,
                    displayModeBar: false
                  }}
                  className="w-full"
                />
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xs text-gray-500">Days to Invoice</div>
                    <div className="text-lg font-semibold">{data.days_to_invoice.toFixed(1)}</div>
                    <div className="text-xs text-gray-500">Target: 3.0</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xs text-gray-500">DSO</div>
                    <div className="text-lg font-semibold">{data.days_to_collect.toFixed(1)}</div>
                    <div className="text-xs text-gray-500">Target: 28.0</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xs text-gray-500">DPO</div>
                    <div className="text-lg font-semibold">{data.days_to_pay.toFixed(1)}</div>
                    <div className="text-xs text-gray-500">Target: 25.0</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <div className="text-xs text-gray-500">Cash Gap</div>
                    <div className="text-lg font-semibold">{data.cash_gap.toFixed(1)}</div>
                    <div className="text-xs text-gray-500">Target: 12.0</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                No working capital data available
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="trend">
            {loading ? (
              <div className="w-full h-[300px] flex items-center justify-center">
                <Skeleton className="w-full h-full" />
              </div>
            ) : data ? (
              <Plot
                data={[
                  {
                    x: data.trend.months,
                    y: data.trend.days_to_invoice,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Days to Invoice',
                    line: {
                      color: 'rgba(37, 99, 235, 0.8)', // blue-600
                      width: 2
                    } as any
                  },
                  {
                    x: data.trend.months,
                    y: data.trend.days_to_collect,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'DSO',
                    line: {
                      color: 'rgba(220, 38, 38, 0.8)', // red-600
                      width: 2
                    } as any
                  },
                  {
                    x: data.trend.months,
                    y: data.trend.days_to_pay,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'DPO',
                    line: {
                      color: 'rgba(5, 150, 105, 0.8)', // green-600
                      width: 2
                    } as any
                  },
                  {
                    x: data.trend.months,
                    y: data.trend.cash_gap,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Cash Gap',
                    line: {
                      color: 'rgba(217, 119, 6, 0.8)', // amber-600
                      width: 3,
                      dash: 'dot'
                    } as any
                  }
                ]}
                layout={{
                  title: '6-Month Working Capital Trend',
                  height: 300,
                  margin: {
                    l: 40,
                    r: 20,
                    t: 30,
                    b: 40
                  },
                  yaxis: {
                    title: 'Days',
                    zeroline: true
                  },
                  legend: {
                    orientation: 'h',
                    y: -0.2
                  }
                } as any}
                config={{
                  responsive: true,
                  displayModeBar: false
                }}
                className="w-full"
              />
            ) : (
              <div className="text-center py-12 text-gray-500">
                No trend data available
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="details">
            {loading ? (
              <div className="w-full h-[300px] flex items-center justify-center">
                <Skeleton className="w-full h-full" />
              </div>
            ) : data ? (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-2">Days to Invoice</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Average time from project completion to invoice issuance.
                  </p>
                  <div className="bg-blue-50 p-3 rounded-md">
                    <p className="text-sm">
                      <strong>Current:</strong> {data.days_to_invoice.toFixed(1)} days
                    </p>
                    <p className="text-sm mt-1">
                      <strong>Recommendation:</strong> Implement same-day invoicing process for all completed projects.
                      Each day reduced in invoicing time directly improves cash gap.
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Days Sales Outstanding (DSO)</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Average time from invoice issuance to payment collection.
                  </p>
                  <div className="bg-red-50 p-3 rounded-md">
                    <p className="text-sm">
                      <strong>Current:</strong> {data.days_to_collect.toFixed(1)} days
                    </p>
                    <p className="text-sm mt-1">
                      <strong>Recommendation:</strong> Implement automated payment reminders at 15, 30, and 45 days.
                      Consider early payment incentives for large invoices.
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Days Payable Outstanding (DPO)</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Average time from vendor invoice receipt to payment.
                  </p>
                  <div className="bg-green-50 p-3 rounded-md">
                    <p className="text-sm">
                      <strong>Current:</strong> {data.days_to_pay.toFixed(1)} days
                    </p>
                    <p className="text-sm mt-1">
                      <strong>Recommendation:</strong> Extend payment terms with key vendors to net-30 where possible.
                      Balance early payment discounts with cash flow optimization.
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Cash Gap</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    The duration for which the business needs to finance its operations (DSO + Days to Invoice - DPO).
                  </p>
                  <div className="bg-amber-50 p-3 rounded-md">
                    <p className="text-sm">
                      <strong>Current:</strong> {data.cash_gap.toFixed(1)} days
                    </p>
                    <p className="text-sm mt-1">
                      <strong>Recommendation:</strong> Target a 5-day reduction in the next quarter by implementing the
                      recommendations above. Every day reduced saves approximately $1,000 in working capital needs per $1M in annual revenue.
                    </p>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Cash Conversion Cycle Projection</h3>
                  <p className="text-sm text-gray-600">
                    Based on current trends, the cash gap is predicted to {
                      data.trend.cash_gap[0] > data.trend.cash_gap[data.trend.cash_gap.length - 1]
                        ? <span className="text-green-600">improve by approximately {(data.trend.cash_gap[0] - data.trend.cash_gap[data.trend.cash_gap.length - 1]).toFixed(1)} days</span>
                        : <span className="text-red-600">worsen by approximately {(data.trend.cash_gap[data.trend.cash_gap.length - 1] - data.trend.cash_gap[0]).toFixed(1)} days</span>
                    } over the next quarter if no changes are made.
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                No detail data available
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}