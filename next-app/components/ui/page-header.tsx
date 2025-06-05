/**
 * Page Header Component
 *
 * Reusable component for consistent page headers with heading and subheading.
 */

import React from 'react';

interface PageHeaderProps {
  heading: string;
  subheading?: string;
  actions?: React.ReactNode;
}

export function PageHeader({ heading, subheading, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 md:text-3xl">
          {heading}
        </h1>
        {subheading && (
          <p className="mt-1 text-sm text-gray-500 md:text-base">
            {subheading}
          </p>
        )}
      </div>
      {actions && <div className="mt-4 flex space-x-3 md:mt-0">{actions}</div>}
    </div>
  );
}