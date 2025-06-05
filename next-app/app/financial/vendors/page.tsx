/**
 * Vendors Management Page
 *
 * Displays a list of vendors and provides functionality for managing them.
 */

import { Suspense } from 'react';
import VendorsDataTable from './components/VendorsDataTable';
import { PageHeader } from '@/components/ui/page-header';
import { VendorCreateButton } from './components/VendorCreateButton';
import { Skeleton } from '@/components/ui/skeleton';

export const metadata = {
  title: 'Vendor Management | Restoration Intel',
  description: 'Manage vendor relationships, payment terms, and performance metrics',
};

export default function VendorsPage() {
  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <PageHeader
          heading="Vendor Management"
          subheading="Manage vendor relationships, payment terms, and performance"
        />
        <VendorCreateButton />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <Suspense fallback={<VendorsTableSkeleton />}>
          <VendorsDataTable />
        </Suspense>
      </div>
    </div>
  );
}

function VendorsTableSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-10 w-[250px]" />
        <Skeleton className="h-10 w-[200px]" />
      </div>
      <Skeleton className="h-[450px] w-full" />
    </div>
  );
}