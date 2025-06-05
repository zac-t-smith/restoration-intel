/**
 * Badge Component
 *
 * Used for displaying status labels, tags, or categories
 */

import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "danger" | "destructive";
}

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        {
        "bg-gray-900 text-white hover:bg-gray-800": variant === "default",
        "bg-gray-100 text-gray-900 hover:bg-gray-200": variant === "secondary",
        "border border-gray-200 text-gray-900 hover:bg-gray-100": variant === "outline",
        "bg-green-100 text-green-800 hover:bg-green-200": variant === "success",
        "bg-yellow-100 text-yellow-800 hover:bg-yellow-200": variant === "warning",
        "bg-red-100 text-red-800 hover:bg-red-200": variant === "danger",
        "bg-red-500 text-white hover:bg-red-600": variant === "destructive",
        },
        className
      )}
      {...props}
    />
  );
}