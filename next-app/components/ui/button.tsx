/**
 * Button Component
 *
 * A versatile button component with various styles and sizes.
 */

import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link";
  size?: "default" | "sm" | "lg" | "icon";
  isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", isLoading = false, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-blue-600 text-white hover:bg-blue-700": variant === "default",
            "bg-red-600 text-white hover:bg-red-700": variant === "destructive",
            "border border-gray-300 bg-white hover:bg-gray-50 text-gray-900": variant === "outline",
            "bg-gray-100 text-gray-900 hover:bg-gray-200": variant === "secondary",
            "hover:bg-gray-100 hover:text-gray-900": variant === "ghost",
            "text-blue-600 underline-offset-4 hover:underline": variant === "link",
            "h-10 px-4 py-2": size === "default",
            "h-9 rounded-md px-3": size === "sm",
            "h-11 rounded-md px-8": size === "lg",
            "h-10 w-10": size === "icon",
          },
          className
        )}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-white" />
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button };