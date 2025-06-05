/**
 * Dashboard Page
 * 
 * The central dashboard for the PE roll-up team to monitor business performance
 */

import React from 'react';
import { Suspense } from 'react';
import { PageHeader } from '@/components/ui/page-header';
import { Skeleton } from '@/components/ui/skeleton';
import DashboardContent from './components/DashboardContent';

export const metadata = {
  title: 'Executive Dashboard | Restoration-Intel',
  description: 'Key business metrics and insights for Restoration-Intel',
};

export default function DashboardPage() {
  return (
    <div className="container mx-auto px-4 py-6">
      <PageHeader
        heading="Executive Dashboard"
        subheading="Real-time business performance metrics and KPIs"
      />
      
      <Suspense fallback={<DashboardSkeleton />}>
        <DashboardContent />
      </Suspense>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* KPI Cards Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <Skeleton className="h-4 w-1/3 mb-2" />
            <Skeleton className="h-8 w-1/2 mb-2" />
            <Skeleton className="h-3 w-1/4" />
          </div>
        ))}
      </div>
      
      {/* Lead-to-Revenue Funnel Skeleton */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <Skeleton className="h-6 w-1/4 mb-2" />
        <Skeleton className="h-4 w-1/3 mb-4" />
        <Skeleton className="h-[350px] w-full" />
      </div>
      
      {/* Rolling KPI Trend Skeleton */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <Skeleton className="h-6 w-1/4 mb-2" />
        <Skeleton className="h-4 w-1/3 mb-4" />
        <Skeleton className="h-[250px] w-full mb-4" />
        <Skeleton className="h-[250px] w-full mb-4" />
        <Skeleton className="h-[250px] w-full" />
      </div>
    </div>
  );
}