/**
 * Lead-to-Revenue Funnel Component
 * 
 * Displays the journey from Lead → Qualified → Billable → Revenue Collected 
 * with conversion percentages between each stage
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

interface FunnelData {
  leads: number;
  qualified: number;
  billable: number;
  collected: number;
}

interface LeadToRevenueFunnelProps {
  data?: FunnelData;
  loading?: boolean;
}

export default function LeadToRevenueFunnel({ 
  data, 
  loading = false 
}: LeadToRevenueFunnelProps) {
  // Default data for demonstration
  const defaultData: FunnelData = {
    leads: 100,
    qualified: 68,
    billable: 42,
    collected: 35
  };

  const funnelData = data || defaultData;
  
  // Calculate conversion rates
  const leadToQualifiedRate = Math.round((funnelData.qualified / funnelData.leads) * 100);
  const qualifiedToBillableRate = Math.round((funnelData.billable / funnelData.qualified) * 100);
  const billableToCollectedRate = Math.round((funnelData.collected / funnelData.billable) * 100);
  const overallConversionRate = Math.round((funnelData.collected / funnelData.leads) * 100);

  // Prepare data for Plotly funnel chart
  const values = [
    funnelData.leads,
    funnelData.qualified,
    funnelData.billable,
    funnelData.collected
  ];

  const labels = [
    `Leads<br>${funnelData.leads}`,
    `Qualified<br>${funnelData.qualified}<br>(${leadToQualifiedRate}%)`,
    `Billable<br>${funnelData.billable}<br>(${qualifiedToBillableRate}%)`,
    `Revenue Collected<br>${funnelData.collected}<br>(${billableToCollectedRate}%)`
  ];

  const plotData = [{
    type: 'funnel',
    y: labels,
    x: values,
    textinfo: "value+percent initial",
    textposition: "inside",
    marker: {
      color: [
        "rgba(59, 130, 246, 0.8)",  // blue-500 with opacity
        "rgba(16, 185, 129, 0.8)",  // green-500 with opacity
        "rgba(245, 158, 11, 0.8)",  // amber-500 with opacity
        "rgba(99, 102, 241, 0.8)"   // indigo-500 with opacity
      ]
    },
    hoverinfo: "y+x+percent initial"
  }];

  const layout = {
    title: {
      text: 'Lead to Revenue Conversion',
      font: {
        size: 18
      }
    },
    height: 350,
    margin: {
      l: 150,
      r: 20,
      t: 60,
      b: 40
    },
    funnelmode: "stack",
    funnelgap: 0.1,
    autosize: true,
    annotations: [
      {
        x: 0.5,
        y: 1.05,
        xanchor: 'center',
        yanchor: 'bottom',
        text: `Overall Conversion: ${overallConversionRate}%`,
        showarrow: false,
        font: {
          size: 14,
          color: 'rgba(75, 85, 99, 1)' // gray-600
        }
      }
    ]
  };

  const config = {
    responsive: true,
    displayModeBar: false
  };

  if (loading) {
    return (
      <Card className="shadow-md">
        <CardHeader>
          <CardTitle>Lead to Revenue Funnel</CardTitle>
          <CardDescription>Conversion journey from leads to revenue</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="w-full h-[350px] flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-md">
      <CardHeader>
        <CardTitle>Lead to Revenue Funnel</CardTitle>
        <CardDescription>Conversion journey from leads to revenue</CardDescription>
      </CardHeader>
      <CardContent>
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          className="w-full"
        />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Leads</p>
            <p className="text-2xl font-bold text-blue-500">{funnelData.leads}</p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Qualified</p>
            <p className="text-2xl font-bold text-green-500">{funnelData.qualified}</p>
            <p className="text-xs text-gray-400">{leadToQualifiedRate}% conversion</p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Billable</p>
            <p className="text-2xl font-bold text-amber-500">{funnelData.billable}</p>
            <p className="text-xs text-gray-400">{qualifiedToBillableRate}% conversion</p>
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-500">Collected</p>
            <p className="text-2xl font-bold text-indigo-500">{funnelData.collected}</p>
            <p className="text-xs text-gray-400">{billableToCollectedRate}% conversion</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}