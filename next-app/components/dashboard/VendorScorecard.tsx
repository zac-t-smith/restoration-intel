/**
 * Vendor/Subcontractor Scorecard Component
 * 
 * Displays performance metrics for vendors including on-time %, 
 * variance vs PO, defect rate; auto-flags top-10 variance Δ
 */

'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[300px] flex items-center justify-center">
      <Skeleton className="w-full h-full" />
    </div>
  )
});

interface VendorMetrics {
  id: number;
  name: string;
  on_time_percentage: number;
  variance_percentage: number;
  defect_rate: number;
  response_time_hours: number;
  total_spend: number;
  active_projects: number;
  flagged: boolean;
  trend: {
    on_time: number[];
    variance: number[];
    defect_rate: number[];
  };
  historical_data: {
    months: string[];
    values: number[];
  };
  last_month_delta: number;
}

interface ScorecardData {
  vendors: VendorMetrics[];
  top_performers: string[];
  flagged_vendors: string[];
  average_on_time: number;
  average_variance: number;
  average_defect_rate: number;
}

// Sample data for development (would come from API in production)
const sampleData: ScorecardData = {
  vendors: [
    {
      id: 1,
      name: "Premier Suppliers",
      on_time_percentage: 96.2,
      variance_percentage: 1.8,
      defect_rate: 0.5,
      response_time_hours: 2.3,
      total_spend: 120500,
      active_projects: 5,
      flagged: false,
      trend: {
        on_time: [94, 95, 96, 96.2],
        variance: [2.5, 2.2, 2.0, 1.8],
        defect_rate: [0.8, 0.7, 0.6, 0.5]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [95, 96, 97, 96.2]
      },
      last_month_delta: -0.8
    },
    {
      id: 2,
      name: "Quality Materials Inc",
      on_time_percentage: 91.5,
      variance_percentage: 3.2,
      defect_rate: 1.2,
      response_time_hours: 4.8,
      total_spend: 85300,
      active_projects: 3,
      flagged: false,
      trend: {
        on_time: [89, 90, 91, 91.5],
        variance: [4.1, 3.8, 3.5, 3.2],
        defect_rate: [1.6, 1.4, 1.3, 1.2]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [89, 90, 91, 91.5]
      },
      last_month_delta: 0.5
    },
    {
      id: 3,
      name: "Discount Supplies Co",
      on_time_percentage: 82.3,
      variance_percentage: 9.8,
      defect_rate: 3.2,
      response_time_hours: 12.6,
      total_spend: 42000,
      active_projects: 2,
      flagged: true,
      trend: {
        on_time: [86, 85, 83, 82.3],
        variance: [7.2, 8.1, 8.9, 9.8],
        defect_rate: [2.8, 2.9, 3.1, 3.2]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [86, 85, 83, 82.3]
      },
      last_month_delta: -0.7
    },
    {
      id: 4,
      name: "FastTrack Logistics",
      on_time_percentage: 98.5,
      variance_percentage: 0.6,
      defect_rate: 0.2,
      response_time_hours: 1.2,
      total_spend: 76500,
      active_projects: 4,
      flagged: false,
      trend: {
        on_time: [97, 97.5, 98, 98.5],
        variance: [1.0, 0.8, 0.7, 0.6],
        defect_rate: [0.4, 0.3, 0.3, 0.2]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [97, 97.5, 98, 98.5]
      },
      last_month_delta: 0.5
    },
    {
      id: 5,
      name: "Budget Materials",
      on_time_percentage: 78.4,
      variance_percentage: 12.5,
      defect_rate: 4.1,
      response_time_hours: 18.2,
      total_spend: 28000,
      active_projects: 1,
      flagged: true,
      trend: {
        on_time: [82, 80, 79, 78.4],
        variance: [9.6, 10.8, 11.7, 12.5],
        defect_rate: [3.5, 3.8, 4.0, 4.1]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [82, 80, 79, 78.4]
      },
      last_month_delta: -0.6
    },
    {
      id: 6,
      name: "Elite Contractors",
      on_time_percentage: 94.8,
      variance_percentage: 2.1,
      defect_rate: 0.8,
      response_time_hours: 3.1,
      total_spend: 142000,
      active_projects: 6,
      flagged: false,
      trend: {
        on_time: [93, 93.5, 94, 94.8],
        variance: [2.6, 2.4, 2.2, 2.1],
        defect_rate: [1.1, 1.0, 0.9, 0.8]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [93, 93.5, 94, 94.8]
      },
      last_month_delta: 0.8
    },
    {
      id: 7,
      name: "Superior Services",
      on_time_percentage: 93.6,
      variance_percentage: 2.8,
      defect_rate: 1.0,
      response_time_hours: 3.8,
      total_spend: 98000,
      active_projects: 4,
      flagged: false,
      trend: {
        on_time: [92, 92.5, 93, 93.6],
        variance: [3.2, 3.0, 2.9, 2.8],
        defect_rate: [1.2, 1.1, 1.0, 1.0]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [92, 92.5, 93, 93.6]
      },
      last_month_delta: 0.6
    },
    {
      id: 8,
      name: "ValueMax Supplies",
      on_time_percentage: 87.2,
      variance_percentage: 5.4,
      defect_rate: 2.1,
      response_time_hours: 8.6,
      total_spend: 54000,
      active_projects: 3,
      flagged: true,
      trend: {
        on_time: [88, 88, 87.5, 87.2],
        variance: [4.8, 5.0, 5.2, 5.4],
        defect_rate: [1.8, 1.9, 2.0, 2.1]
      },
      historical_data: {
        months: ['Mar', 'Apr', 'May', 'Jun'],
        values: [88, 88, 87.5, 87.2]
      },
      last_month_delta: -0.3
    }
  ],
  top_performers: ["FastTrack Logistics", "Premier Suppliers", "Elite Contractors"],
  flagged_vendors: ["Budget Materials", "Discount Supplies Co", "ValueMax Supplies"],
  average_on_time: 90.3,
  average_variance: 4.8,
  average_defect_rate: 1.6
};

export default function VendorScorecard() {
  const [data, setData] = useState<ScorecardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedVendor, setSelectedVendor] = useState<VendorMetrics | null>(null);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof VendorMetrics, 
    direction: 'asc' | 'desc'
  }>({ key: 'on_time_percentage', direction: 'desc' });
  
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
  
  // Sort vendors based on current sort config
  const getSortedVendors = () => {
    if (!data) return [];
    
    return [...data.vendors].sort((a, b) => {
      const aValue = a[sortConfig.key] as number | string;
      const bValue = b[sortConfig.key] as number | string;
      
      if (sortConfig.direction === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  };
  
  // Handle sort request
  const requestSort = (key: keyof VendorMetrics) => {
    let direction: 'asc' | 'desc' = 'desc';
    
    if (sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    
    setSortConfig({ key, direction });
  };
  
  // Get badge for on-time percentage
  const getOnTimeBadge = (value: number) => {
    if (value >= 95) return <Badge variant="success">Excellent ({value}%)</Badge>;
    if (value >= 90) return <Badge variant="outline" className="bg-green-50">Good ({value}%)</Badge>;
    if (value >= 85) return <Badge variant="outline" className="bg-yellow-50">Fair ({value}%)</Badge>;
    if (value >= 80) return <Badge variant="warning">Poor ({value}%)</Badge>;
    return <Badge variant="destructive">Critical ({value}%)</Badge>;
  };
  
  // Get badge for variance percentage
  const getVarianceBadge = (value: number) => {
    if (value <= 1) return <Badge variant="success">Excellent ({value}%)</Badge>;
    if (value <= 3) return <Badge variant="outline" className="bg-green-50">Good ({value}%)</Badge>;
    if (value <= 5) return <Badge variant="outline" className="bg-yellow-50">Fair ({value}%)</Badge>;
    if (value <= 10) return <Badge variant="warning">High ({value}%)</Badge>;
    return <Badge variant="destructive">Excessive ({value}%)</Badge>;
  };
  
  // Get badge for defect rate
  const getDefectBadge = (value: number) => {
    if (value <= 0.5) return <Badge variant="success">Excellent ({value}%)</Badge>;
    if (value <= 1.0) return <Badge variant="outline" className="bg-green-50">Good ({value}%)</Badge>;
    if (value <= 2.0) return <Badge variant="outline" className="bg-yellow-50">Fair ({value}%)</Badge>;
    if (value <= 3.0) return <Badge variant="warning">High ({value}%)</Badge>;
    return <Badge variant="destructive">Excessive ({value}%)</Badge>;
  };
  
  // Render trend sparkline
  const renderTrendSparkline = (vendor: VendorMetrics, metric: 'on_time' | 'variance' | 'defect_rate') => {
    const months = ['Mar', 'Apr', 'May', 'Jun'];
    const values = vendor.trend[metric];
    
    return (
      <Plot
        data={[
          {
            x: months,
            y: values,
            type: 'scatter',
            mode: 'lines+markers',
            line: {
              color: metric === 'on_time' 
                ? 'rgba(16, 185, 129, 0.8)' // green
                : metric === 'variance' 
                  ? 'rgba(239, 68, 68, 0.8)' // red
                  : 'rgba(59, 130, 246, 0.8)', // blue
              width: 2
            },
            marker: {
              size: 4
            }
          } as any
        ]}
        layout={{
          height: 80,
          width: 120,
          margin: {
            l: 10,
            r: 10,
            t: 10,
            b: 20
          },
          xaxis: {
            showticklabels: true,
            showgrid: false,
            tickfont: {
              size: 8
            }
          },
          yaxis: {
            showticklabels: false,
            showgrid: false
          },
          showlegend: false
        } as any}
        config={{
          displayModeBar: false,
          responsive: true
        }}
        className="mt-1"
      />
    );
  };
  
  // Render vendor detail view
  const renderVendorDetail = () => {
    if (!selectedVendor) return null;
    
    return (
      <div className="mt-6 border rounded-lg p-4">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-lg font-medium">{selectedVendor.name}</h3>
            <p className="text-sm text-gray-500">
              ${selectedVendor.total_spend.toLocaleString()} total spend • {selectedVendor.active_projects} active projects
            </p>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setSelectedVendor(null)}
          >
            Close
          </Button>
        </div>
        
        <Tabs defaultValue="performance">
          <TabsList className="mb-4">
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="historical">Historical</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          </TabsList>
          
          <TabsContent value="performance">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xs text-gray-500">On-Time Percentage</div>
                <div className="text-lg font-semibold">{selectedVendor.on_time_percentage}%</div>
                <div className="text-xs text-gray-500">
                  vs. {data?.average_on_time}% avg
                  <span className={selectedVendor.on_time_percentage > (data?.average_on_time || 0) ? 'text-green-500 ml-1' : 'text-red-500 ml-1'}>
                    ({selectedVendor.on_time_percentage > (data?.average_on_time || 0) ? '+' : ''}
                    {(selectedVendor.on_time_percentage - (data?.average_on_time || 0)).toFixed(1)}%)
                  </span>
                </div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xs text-gray-500">Variance from PO</div>
                <div className="text-lg font-semibold">{selectedVendor.variance_percentage}%</div>
                <div className="text-xs text-gray-500">
                  vs. {data?.average_variance}% avg
                  <span className={selectedVendor.variance_percentage < (data?.average_variance || 0) ? 'text-green-500 ml-1' : 'text-red-500 ml-1'}>
                    ({selectedVendor.variance_percentage < (data?.average_variance || 0) ? '' : '+'}
                    {(selectedVendor.variance_percentage - (data?.average_variance || 0)).toFixed(1)}%)
                  </span>
                </div>
              </div>
              
              <div className="bg-gray-50 p-3 rounded-md">
                <div className="text-xs text-gray-500">Defect Rate</div>
                <div className="text-lg font-semibold">{selectedVendor.defect_rate}%</div>
                <div className="text-xs text-gray-500">
                  vs. {data?.average_defect_rate}% avg
                  <span className={selectedVendor.defect_rate < (data?.average_defect_rate || 0) ? 'text-green-500 ml-1' : 'text-red-500 ml-1'}>
                    ({selectedVendor.defect_rate < (data?.average_defect_rate || 0) ? '' : '+'}
                    {(selectedVendor.defect_rate - (data?.average_defect_rate || 0)).toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
            
            <div className="mt-4">
              <h4 className="text-sm font-medium mb-2">3-Month Performance Trend</h4>
              <Plot
                data={[
                  {
                    x: selectedVendor.historical_data.months,
                    y: selectedVendor.trend.on_time,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'On-Time %',
                    line: { color: 'rgba(16, 185, 129, 0.8)' }
                  } as any,
                  {
                    x: selectedVendor.historical_data.months,
                    y: selectedVendor.trend.variance,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Variance %',
                    line: { color: 'rgba(239, 68, 68, 0.8)' }
                  } as any,
                  {
                    x: selectedVendor.historical_data.months,
                    y: selectedVendor.trend.defect_rate,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Defect Rate',
                    line: { color: 'rgba(59, 130, 246, 0.8)' }
                  } as any
                ]}
                layout={{
                  height: 250,
                  margin: {
                    l: 40,
                    r: 20,
                    t: 20,
                    b: 40
                  },
                  legend: {
                    orientation: 'h',
                    y: -0.2
                  },
                  yaxis: {
                    title: 'Percentage'
                  }
                } as any}
                config={{
                  responsive: true,
                  displayModeBar: false
                }}
              />
            </div>
          </TabsContent>
          
          <TabsContent value="historical">
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Key Performance Indicators</h4>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Month</TableHead>
                      <TableHead>On-Time %</TableHead>
                      <TableHead>Variance %</TableHead>
                      <TableHead>Defect Rate</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedVendor.historical_data.months.map((month, index) => (
                      <TableRow key={month}>
                        <TableCell>{month}</TableCell>
                        <TableCell>{selectedVendor.trend.on_time[index]}%</TableCell>
                        <TableCell>{selectedVendor.trend.variance[index]}%</TableCell>
                        <TableCell>{selectedVendor.trend.defect_rate[index]}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              <div>
                <h4 className="text-sm font-medium mb-2">Monthly Δ Analysis</h4>
                <p className="text-sm text-gray-600">
                  {selectedVendor.name} has shown a{' '}
                  <span className={selectedVendor.last_month_delta >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                    {selectedVendor.last_month_delta >= 0 ? 'positive' : 'negative'} trend
                  </span>{' '}
                  over the last month with a {Math.abs(selectedVendor.last_month_delta).toFixed(1)}% {selectedVendor.last_month_delta >= 0 ? 'improvement' : 'decline'} in 
                  on-time percentage.
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  {selectedVendor.variance_percentage > 5 ? (
                    <>PO variance has consistently been above target. Consider implementing stricter change order procedures with this vendor.</>
                  ) : (
                    <>PO variance is within acceptable limits. Continue monitoring for any significant changes.</>
                  )}
                </p>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="recommendations">
            <div className="space-y-4">
              {selectedVendor.flagged ? (
                <Alert variant="default" className="bg-yellow-50 text-yellow-900 border-yellow-200">
                  <AlertTitle>Performance Warning</AlertTitle>
                  <AlertDescription>
                    This vendor is flagged for performance issues. Consider implementing the recommendations below.
                  </AlertDescription>
                </Alert>
              ) : data?.top_performers.includes(selectedVendor.name) ? (
                <Alert variant="default" className="bg-green-50 text-green-900 border-green-200">
                  <AlertTitle>Top Performer</AlertTitle>
                  <AlertDescription>
                    This vendor is among your top performers. Consider increasing allocation and discussing longer-term contracts.
                  </AlertDescription>
                </Alert>
              ) : null}
              
              <div>
                <h4 className="text-sm font-medium mb-2">Recommendations</h4>
                <ul className="space-y-2">
                  {selectedVendor.on_time_percentage < 90 && (
                    <li className="text-sm bg-yellow-50 p-2 rounded">
                      <span className="font-medium">Improve On-Time Delivery:</span> Schedule a quarterly business review meeting 
                      to address timeline expectations and communication protocols.
                    </li>
                  )}
                  
                  {selectedVendor.variance_percentage > 5 && (
                    <li className="text-sm bg-yellow-50 p-2 rounded">
                      <span className="font-medium">Reduce PO Variance:</span> Implement stricter change order procedures 
                      and require written approval for any deviation from original PO.
                    </li>
                  )}
                  
                  {selectedVendor.defect_rate > 2 && (
                    <li className="text-sm bg-yellow-50 p-2 rounded">
                      <span className="font-medium">Address Quality Issues:</span> Request a quality improvement plan 
                      and consider implementing additional quality control checkpoints.
                    </li>
                  )}
                  
                  {selectedVendor.on_time_percentage >= 95 && selectedVendor.variance_percentage <= 2 && (
                    <li className="text-sm bg-green-50 p-2 rounded">
                      <span className="font-medium">Strengthen Partnership:</span> Consider offering preferred vendor 
                      status and discussing volume-based discounts or long-term agreements.
                    </li>
                  )}
                  
                  {selectedVendor.on_time_percentage < 80 && selectedVendor.variance_percentage > 10 && (
                    <li className="text-sm bg-red-50 p-2 rounded">
                      <span className="font-medium">Critical Action Required:</span> Review all active projects with this vendor 
                      and consider phasing out for non-critical work while they address performance issues.
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    );
  };
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Vendor & Subcontractor Scorecard</CardTitle>
        <CardDescription>
          Performance metrics for all active vendors and subcontractors
        </CardDescription>
      </CardHeader>
      <CardContent>
        {data?.flagged_vendors.length > 0 && (
          <Alert variant="default" className="mb-4 bg-yellow-50 text-yellow-900 border-yellow-200">
            <AlertTitle>Vendor Performance Alert</AlertTitle>
            <AlertDescription>
              {data.flagged_vendors.length} vendors are flagged for performance issues. Click on the vendor name to see detailed analysis and recommendations.
            </AlertDescription>
          </Alert>
        )}
        
        {loading ? (
          <div className="w-full h-[400px] flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : data ? (
          <>
            <div className="overflow-x-auto">
              <Table className="w-full">
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[200px]">
                      <Button 
                        variant="ghost" 
                        onClick={() => requestSort('name')}
                        className="-ml-4"
                      >
                        Vendor Name {sortConfig.key === 'name' ? (sortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                      </Button>
                    </TableHead>
                    <TableHead>
                      <Button 
                        variant="ghost" 
                        onClick={() => requestSort('on_time_percentage')}
                        className="-ml-4"
                      >
                        On-Time % {sortConfig.key === 'on_time_percentage' ? (sortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                      </Button>
                    </TableHead>
                    <TableHead>
                      <Button 
                        variant="ghost" 
                        onClick={() => requestSort('variance_percentage')}
                        className="-ml-4"
                      >
                        Variance % {sortConfig.key === 'variance_percentage' ? (sortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                      </Button>
                    </TableHead>
                    <TableHead>
                      <Button 
                        variant="ghost" 
                        onClick={() => requestSort('defect_rate')}
                        className="-ml-4"
                      >
                        Defect Rate {sortConfig.key === 'defect_rate' ? (sortConfig.direction === 'asc' ? '↑' : '↓') : ''}
                      </Button>
                    </TableHead>
                    <TableHead>3-Month Trend</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {getSortedVendors().map((vendor) => (
                    <TableRow key={vendor.id} className={vendor.flagged ? 'bg-red-50' : ''}>
                      <TableCell>
                        <Button 
                          variant="link" 
                          onClick={() => setSelectedVendor(vendor)}
                          className="p-0 h-auto font-medium text-blue-600 hover:text-blue-800"
                        >
                          {vendor.name}
                        </Button>
                        {vendor.flagged && <Badge variant="warning" className="ml-2">Flagged</Badge>}
                      </TableCell>
                      <TableCell>{getOnTimeBadge(vendor.on_time_percentage)}</TableCell>
                      <TableCell>{getVarianceBadge(vendor.variance_percentage)}</TableCell>
                      <TableCell>{getDefectBadge(vendor.defect_rate)}</TableCell>
                      <TableCell className="flex space-x-2">
                        <div className="text-center">
                          <div className="text-xs text-gray-500 mb-1">On-Time</div>
                          {renderTrendSparkline(vendor, 'on_time')}
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-gray-500 mb-1">Variance</div>
                          {renderTrendSparkline(vendor, 'variance')}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            
            {selectedVendor && renderVendorDetail()}
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-md">
                <h3 className="text-sm font-medium mb-2">Overall Vendor Performance</h3>
                <Plot
                  data={[
                    {
                      type: 'indicator',
                      mode: 'gauge+number',
                      value: data.average_on_time,
                      title: { text: 'On-Time %', font: { size: 14 } },
                      gauge: {
                        axis: { range: [0, 100], tickwidth: 1 },
                        bar: { color: 'rgba(16, 185, 129, 0.8)' },
                        steps: [
                          { range: [0, 70], color: 'rgba(239, 68, 68, 0.2)' },
                          { range: [70, 85], color: 'rgba(245, 158, 11, 0.2)' },
                          { range: [85, 95], color: 'rgba(16, 185, 129, 0.2)' },
                          { range: [95, 100], color: 'rgba(16, 185, 129, 0.4)' }
                        ],
                        threshold: {
                          line: { color: 'red', width: 2 },
                          thickness: 0.75,
                          value: 90
                        }
                      }
                    } as any
                  ]}
                  layout={{
                    height: 150,
                    margin: { t: 25, r: 25, l: 25, b: 25 },
                  } as any}
                  config={{
                    responsive: true,
                    displayModeBar: false
                  }}
                />
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md">
                <h3 className="text-sm font-medium mb-2">Top Variances from PO</h3>
                <ul className="space-y-2 text-sm">
                  {data.vendors
                    .sort((a, b) => b.variance_percentage - a.variance_percentage)
                    .slice(0, 3)
                    .map(vendor => (
                      <li key={vendor.id} className="flex justify-between">
                        <span>{vendor.name}</span>
                        <span className={vendor.variance_percentage > 5 ? 'text-red-600 font-medium' : ''}>
                          {vendor.variance_percentage}%
                        </span>
                      </li>
                    ))}
                </ul>
                <div className="mt-3 pt-3 border-t text-xs text-gray-500">
                  Average variance: {data.average_variance}%
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md">
                <h3 className="text-sm font-medium mb-2">Vendor Quality Rating</h3>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm">Top Performers ({data.top_performers.length})</span>
                  <Badge variant="success">{Math.round(data.top_performers.length / data.vendors.length * 100)}%</Badge>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm">Acceptable ({data.vendors.length - data.top_performers.length - data.flagged_vendors.length})</span>
                  <Badge variant="outline" className="bg-green-50">
                    {Math.round((data.vendors.length - data.top_performers.length - data.flagged_vendors.length) / data.vendors.length * 100)}%
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Flagged ({data.flagged_vendors.length})</span>
                  <Badge variant="destructive">{Math.round(data.flagged_vendors.length / data.vendors.length * 100)}%</Badge>
                </div>
                <div className="mt-3 pt-3 border-t text-xs text-gray-500">
                  Based on combined performance metrics
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No vendor data available
          </div>
        )}
      </CardContent>
    </Card>
  );
}