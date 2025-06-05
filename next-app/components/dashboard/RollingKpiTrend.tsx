/**
 * Rolling KPI Trend Component
 * 
 * Displays 12-month trends for key performance metrics including:
 * - Gross Profit Margin Trend
 * - Lead Conversion Rate Trend
 * - Monthly Revenue Trend
 */

"use client";

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[350px] flex items-center justify-center">
      <Skeleton className="w-full h-full" />
    </div>
  )
});

interface MonthlyData {
  month: string;
  grossProfitMargin: number;
  leadConversionRate: number;
  revenue: number;
}

interface RollingKpiTrendProps {
  data?: MonthlyData[];
  loading?: boolean;
}

export default function RollingKpiTrend({
  data,
  loading = false
}: RollingKpiTrendProps) {
  // Default data for demonstration (last 12 months)
  const defaultData: MonthlyData[] = [
    { month: 'Jun 2024', grossProfitMargin: 42, leadConversionRate: 68, revenue: 245000 },
    { month: 'May 2024', grossProfitMargin: 40, leadConversionRate: 65, revenue: 231000 },
    { month: 'Apr 2024', grossProfitMargin: 39, leadConversionRate: 62, revenue: 210000 },
    { month: 'Mar 2024', grossProfitMargin: 41, leadConversionRate: 64, revenue: 225000 },
    { month: 'Feb 2024', grossProfitMargin: 38, leadConversionRate: 60, revenue: 198000 },
    { month: 'Jan 2024', grossProfitMargin: 36, leadConversionRate: 59, revenue: 186000 },
    { month: 'Dec 2023', grossProfitMargin: 43, leadConversionRate: 70, revenue: 252000 },
    { month: 'Nov 2023', grossProfitMargin: 41, leadConversionRate: 67, revenue: 237000 },
    { month: 'Oct 2023', grossProfitMargin: 39, leadConversionRate: 63, revenue: 215000 },
    { month: 'Sep 2023', grossProfitMargin: 38, leadConversionRate: 62, revenue: 207000 },
    { month: 'Aug 2023', grossProfitMargin: 37, leadConversionRate: 61, revenue: 195000 },
    { month: 'Jul 2023', grossProfitMargin: 36, leadConversionRate: 59, revenue: 185000 }
  ];

  // Use real data if provided, otherwise use default data
  const chartData = data || defaultData;
  
  // Sort data chronologically
  const sortedData = [...chartData].sort((a, b) => {
    return new Date(a.month).getTime() - new Date(b.month).getTime();
  });
  
  // Extract month labels and values for the charts
  const months = sortedData.map(d => d.month);
  const grossProfitMargins = sortedData.map(d => d.grossProfitMargin);
  const leadConversionRates = sortedData.map(d => d.leadConversionRate);
  const revenues = sortedData.map(d => d.revenue);

  // Calculate trends
  const calcTrend = (values: number[]) => {
    if (values.length >= 2) {
      const firstValue = values[0];
      const lastValue = values[values.length - 1];
      return ((lastValue - firstValue) / firstValue) * 100;
    }
    return 0;
  };

  const marginTrend = calcTrend(grossProfitMargins);
  const conversionTrend = calcTrend(leadConversionRates);
  const revenueTrend = calcTrend(revenues);

  // Format trend display with + or - sign and color
  const formatTrend = (trend: number) => {
    const sign = trend >= 0 ? '+' : '';
    return `${sign}${trend.toFixed(1)}%`;
  };

  // Determine color class based on trend value
  const getTrendColorClass = (trend: number) => {
    return trend >= 0 ? 'text-green-500' : 'text-red-500';
  };

  // Prepare charts
  const grossProfitMarginPlot = {
    data: [{
      x: months,
      y: grossProfitMargins,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Gross Profit Margin',
      line: {
        color: 'rgba(16, 185, 129, 1)', // green-500
        width: 2
      },
      marker: {
        color: 'rgba(16, 185, 129, 1)',
        size: 6
      }
    }],
    layout: {
      title: {
        text: 'Gross Profit Margin Trend',
        font: {
          size: 16
        }
      },
      height: 250,
      margin: {
        l: 40,
        r: 20,
        t: 40,
        b: 40
      },
      xaxis: {
        title: ''
      },
      yaxis: {
        title: 'Margin %',
        ticksuffix: '%'
      },
      autosize: true
    }
  };

  const leadConversionRatePlot = {
    data: [{
      x: months,
      y: leadConversionRates,
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Lead Conversion Rate',
      line: {
        color: 'rgba(59, 130, 246, 1)', // blue-500
        width: 2
      },
      marker: {
        color: 'rgba(59, 130, 246, 1)',
        size: 6
      }
    }],
    layout: {
      title: {
        text: 'Lead Conversion Rate Trend',
        font: {
          size: 16
        }
      },
      height: 250,
      margin: {
        l: 40,
        r: 20,
        t: 40,
        b: 40
      },
      xaxis: {
        title: ''
      },
      yaxis: {
        title: 'Conversion %',
        ticksuffix: '%'
      },
      autosize: true
    }
  };

  const revenuePlot = {
    data: [{
      x: months,
      y: revenues,
      type: 'bar',
      name: 'Monthly Revenue',
      marker: {
        color: 'rgba(99, 102, 241, 0.8)' // indigo-500 with opacity
      }
    }],
    layout: {
      title: {
        text: 'Monthly Revenue Trend',
        font: {
          size: 16
        }
      },
      height: 250,
      margin: {
        l: 50,
        r: 20,
        t: 40,
        b: 40
      },
      xaxis: {
        title: ''
      },
      yaxis: {
        title: 'Revenue ($)',
        tickprefix: '$',
        tickformat: ',.0f'
      },
      autosize: true
    }
  };

  const config = {
    responsive: true,
    displayModeBar: false
  };

  if (loading) {
    return (
      <Card className="shadow-md">
        <CardHeader>
          <CardTitle>Rolling 12-Month KPI Trends</CardTitle>
          <CardDescription>Historical performance metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6">
            <Skeleton className="w-full h-[250px]" />
            <Skeleton className="w-full h-[250px]" />
            <Skeleton className="w-full h-[250px]" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-md">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Rolling 12-Month KPI Trends</CardTitle>
            <CardDescription>Historical performance metrics</CardDescription>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Margin</p>
              <p className={`text-sm font-bold ${getTrendColorClass(marginTrend)}`}>
                {formatTrend(marginTrend)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Conversion</p>
              <p className={`text-sm font-bold ${getTrendColorClass(conversionTrend)}`}>
                {formatTrend(conversionTrend)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Revenue</p>
              <p className={`text-sm font-bold ${getTrendColorClass(revenueTrend)}`}>
                {formatTrend(revenueTrend)}
              </p>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6">
          <Plot
            data={grossProfitMarginPlot.data}
            layout={grossProfitMarginPlot.layout}
            config={config}
            className="w-full"
          />
          <Plot
            data={leadConversionRatePlot.data}
            layout={leadConversionRatePlot.layout}
            config={config}
            className="w-full"
          />
          <Plot
            data={revenuePlot.data}
            layout={revenuePlot.layout}
            config={config}
            className="w-full"
          />
        </div>
      </CardContent>
    </Card>
  );
}