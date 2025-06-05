/**
 * Operations Capacity Heat-Map Component
 * 
 * Displays a calendar heat-map of crew-hours vs booked jobs
 * Alerts when capacity is ≥85% for 2+ weeks
 */

'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[400px] flex items-center justify-center">
      <Skeleton className="w-full h-full" />
    </div>
  )
});

interface CapacityData {
  weeks: string[];
  crews: string[];
  utilization: number[][]; // 2D array [crews][weeks]
  overCapacityWarning: boolean;
  overCapacityWeeks: string[];
  totalBookedHours: number;
  totalAvailableHours: number;
  utilizationRate: number;
}

// Sample data for development (would come from API in production)
const sampleData: CapacityData = {
  weeks: ['Jun 3-9', 'Jun 10-16', 'Jun 17-23', 'Jun 24-30', 'Jul 1-7', 'Jul 8-14', 'Jul 15-21', 'Jul 22-28'],
  crews: ['Crew A', 'Crew B', 'Crew C', 'Crew D', 'Crew E'],
  utilization: [
    [65, 78, 82, 91, 87, 75, 60, 55],  // Crew A
    [70, 75, 88, 92, 95, 89, 72, 68],  // Crew B
    [55, 60, 72, 80, 85, 88, 75, 65],  // Crew C
    [50, 65, 75, 80, 82, 78, 70, 60],  // Crew D
    [60, 75, 85, 90, 88, 82, 70, 65],  // Crew E
  ],
  overCapacityWarning: true,
  overCapacityWeeks: ['Jun 24-30', 'Jul 1-7', 'Jul 8-14'],
  totalBookedHours: 1250,
  totalAvailableHours: 1600,
  utilizationRate: 78.1
};

export default function OpsCapacityHeatMap() {
  const [data, setData] = useState<CapacityData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<'heatmap' | 'crew' | 'week'>('heatmap');
  
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
  
  // Calculate color scale ranges
  const getColorForValue = (value: number) => {
    if (value < 60) return 'bg-green-100';
    if (value < 75) return 'bg-green-200';
    if (value < 85) return 'bg-yellow-100';
    if (value < 95) return 'bg-orange-100';
    return 'bg-red-100';
  };
  
  // Calculate week average utilization
  const calculateWeeklyAverage = (weekIndex: number): number => {
    if (!data) return 0;
    
    let sum = 0;
    for (let i = 0; i < data.crews.length; i++) {
      sum += data.utilization[i][weekIndex];
    }
    return sum / data.crews.length;
  };
  
  // Calculate crew average utilization
  const calculateCrewAverage = (crewIndex: number): number => {
    if (!data) return 0;
    
    let sum = 0;
    for (let i = 0; i < data.weeks.length; i++) {
      sum += data.utilization[crewIndex][i];
    }
    return sum / data.weeks.length;
  };
  
  // Get badge for utilization
  const getUtilizationBadge = (value: number) => {
    if (value < 60) return <Badge variant="outline" className="bg-green-50">Low ({value.toFixed(0)}%)</Badge>;
    if (value < 75) return <Badge variant="outline" className="bg-green-100">Good ({value.toFixed(0)}%)</Badge>;
    if (value < 85) return <Badge variant="outline" className="bg-yellow-100">High ({value.toFixed(0)}%)</Badge>;
    if (value < 95) return <Badge variant="destructive" className="bg-orange-100">Critical ({value.toFixed(0)}%)</Badge>;
    return <Badge variant="destructive" className="bg-red-100">Overbooked ({value.toFixed(0)}%)</Badge>;
  };
  
  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Ops Capacity Heat-Map</CardTitle>
            <CardDescription>
              Crew capacity utilization over the next 8 weeks
            </CardDescription>
          </div>
          
          <div className="flex space-x-2">
            <Button 
              variant={viewMode === 'heatmap' ? 'default' : 'outline'} 
              size="sm"
              onClick={() => setViewMode('heatmap')}
            >
              Heat Map
            </Button>
            <Button 
              variant={viewMode === 'crew' ? 'default' : 'outline'} 
              size="sm"
              onClick={() => setViewMode('crew')}
            >
              By Crew
            </Button>
            <Button 
              variant={viewMode === 'week' ? 'default' : 'outline'} 
              size="sm"
              onClick={() => setViewMode('week')}
            >
              By Week
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {data?.overCapacityWarning && (
          <Alert variant="destructive" className="mb-4">
            <AlertTitle>Capacity Alert</AlertTitle>
            <AlertDescription>
              Crew capacity exceeds 85% for {data.overCapacityWeeks.length} consecutive weeks ({data.overCapacityWeeks.join(', ')}). 
              Consider adjusting job schedules or adding temporary staff.
            </AlertDescription>
          </Alert>
        )}
        
        {loading ? (
          <div className="w-full h-[400px] flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : data ? (
          <>
            {viewMode === 'heatmap' && (
              <>
                <Plot
                  data={[
                    {
                      z: data.utilization,
                      x: data.weeks,
                      y: data.crews,
                      type: 'heatmap',
                      colorscale: [
                        [0, 'rgb(0, 255, 0)'],     // 0% = green
                        [0.6, 'rgb(220, 255, 0)'],  // 60% = yellow-green
                        [0.85, 'rgb(255, 165, 0)'], // 85% = orange
                        [1, 'rgb(255, 0, 0)']       // 100% = red
                      ],
                      showscale: true,
                      colorbar: {
                        title: 'Utilization %',
                        titleside: 'right',
                      },
                      hovertemplate: 'Crew: %{y}<br>Week: %{x}<br>Utilization: %{z}%<extra></extra>'
                    } as any
                  ]}
                  layout={{
                    title: 'Crew Capacity Utilization',
                    height: 400,
                    margin: {
                      l: 50,
                      r: 20,
                      t: 50,
                      b: 80
                    },
                    yaxis: {
                      title: 'Crews'
                    },
                    xaxis: {
                      title: 'Weeks'
                    },
                    annotations: data.overCapacityWeeks.map((week, i) => {
                      const weekIndex = data.weeks.indexOf(week);
                      return {
                        x: week,
                        y: data.crews.length - 1 + 0.5,
                        text: '⚠️',
                        showarrow: false,
                        font: {
                          size: 16
                        }
                      };
                    })
                  } as any}
                  config={{
                    responsive: true,
                    displayModeBar: false
                  }}
                  className="w-full"
                />
                
                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-md">
                    <div className="text-sm font-medium">Total Booked Hours</div>
                    <div className="text-2xl font-bold">{data.totalBookedHours}</div>
                    <div className="text-sm text-gray-500">out of {data.totalAvailableHours} available</div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-md">
                    <div className="text-sm font-medium">Overall Utilization</div>
                    <div className="text-2xl font-bold">{data.utilizationRate.toFixed(1)}%</div>
                    <div className="text-sm text-gray-500">target: 75-80%</div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-md">
                    <div className="text-sm font-medium">Capacity Warning</div>
                    <div className="text-2xl font-bold flex items-center">
                      {data.overCapacityWeeks.length > 0 ? (
                        <span className="text-red-500">Active</span>
                      ) : (
                        <span className="text-green-500">None</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {data.overCapacityWeeks.length > 0 
                        ? `${data.overCapacityWeeks.length} weeks over 85%` 
                        : 'All weeks under 85%'}
                    </div>
                  </div>
                </div>
              </>
            )}
            
            {viewMode === 'crew' && (
              <div className="space-y-4">
                <h3 className="font-medium text-lg">Utilization by Crew</h3>
                {data.crews.map((crew, crewIndex) => {
                  const avgUtilization = calculateCrewAverage(crewIndex);
                  return (
                    <div key={crew} className="border rounded-md p-4">
                      <div className="flex justify-between items-center mb-2">
                        <div className="font-medium">{crew}</div>
                        <div>{getUtilizationBadge(avgUtilization)}</div>
                      </div>
                      <div className="grid grid-cols-8 gap-1">
                        {data.utilization[crewIndex].map((value, weekIndex) => (
                          <div key={weekIndex} className="text-center">
                            <div className={`${getColorForValue(value)} rounded-md p-2 text-xs font-medium`}>
                              {value}%
                            </div>
                            <div className="text-xs mt-1 text-gray-500">
                              {data.weeks[weekIndex]}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            
            {viewMode === 'week' && (
              <div className="space-y-4">
                <h3 className="font-medium text-lg">Utilization by Week</h3>
                {data.weeks.map((week, weekIndex) => {
                  const avgUtilization = calculateWeeklyAverage(weekIndex);
                  const isOverCapacity = data.overCapacityWeeks.includes(week);
                  
                  return (
                    <div key={week} className={`border rounded-md p-4 ${isOverCapacity ? 'border-red-300' : ''}`}>
                      <div className="flex justify-between items-center mb-2">
                        <div className="font-medium flex items-center">
                          {week} 
                          {isOverCapacity && (
                            <span className="ml-2 text-red-500 text-sm">⚠️ Over Capacity</span>
                          )}
                        </div>
                        <div>{getUtilizationBadge(avgUtilization)}</div>
                      </div>
                      <div className="grid grid-cols-5 gap-1">
                        {data.crews.map((crew, crewIndex) => {
                          const value = data.utilization[crewIndex][weekIndex];
                          return (
                            <div key={crewIndex} className="text-center">
                              <div className={`${getColorForValue(value)} rounded-md p-2 text-xs font-medium`}>
                                {value}%
                              </div>
                              <div className="text-xs mt-1 text-gray-500">
                                {crew}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            
            <div className="mt-6">
              <h3 className="font-medium mb-2">Capacity Planning Recommendations</h3>
              <ul className="list-disc pl-5 space-y-1 text-sm">
                <li>
                  {data.overCapacityWeeks.length > 0 ? (
                    <span>
                      <span className="font-medium">High Priority:</span> Redistribute jobs from {data.overCapacityWeeks.join(', ')} to earlier or later weeks if possible.
                    </span>
                  ) : (
                    <span>
                      <span className="font-medium">Good Capacity Balance:</span> Current job distribution is within optimal parameters.
                    </span>
                  )}
                </li>
                <li>
                  <span className="font-medium">Crew Balancing:</span> Consider redistributing work from {data.crews[1]} to {data.crews[0]} or {data.crews[2]} to achieve better balance.
                </li>
                <li>
                  <span className="font-medium">Long-term Planning:</span> Current booking rate suggests need for additional crew by {data.weeks[5]}.
                </li>
              </ul>
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No capacity data available
          </div>
        )}
      </CardContent>
    </Card>
  );
}