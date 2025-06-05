/**
 * Alert Dialog Component
 *
 * A modal dialog for confirmations with destructive actions
 */

import * as React from "react";
import { cn } from "@/lib/utils";

interface AlertDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

const AlertDialog = ({ children, ...props }: AlertDialogProps) => {
  return <div {...props}>{children}</div>;
};
AlertDialog.displayName = "AlertDialog";

interface AlertDialogTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const AlertDialogTrigger = React.forwardRef<HTMLButtonElement, AlertDialogTriggerProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn("inline-flex items-center justify-center", className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);
AlertDialogTrigger.displayName = "AlertDialogTrigger";

interface AlertDialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const AlertDialogContent = React.forwardRef<HTMLDivElement, AlertDialogContentProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-all"
          onClick={() => {
            // Handle backdrop click if needed
          }}
        />
        <div
          ref={ref}
          className={cn(
            "fixed z-50 w-full max-w-md overflow-hidden rounded-lg bg-white p-6 shadow-lg",
            "animate-in fade-in-90 slide-in-from-bottom-10",
            "sm:zoom-in-90 sm:slide-in-from-bottom-0",
            className
          )}
          {...props}
        >
          {children}
        </div>
      </div>
    );
  }
);
AlertDialogContent.displayName = "AlertDialogContent";

interface AlertDialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const AlertDialogHeader = ({ className, children, ...props }: AlertDialogHeaderProps) => {
  return (
    <div
      className={cn("mb-4 flex flex-col space-y-1.5 text-center sm:text-left", className)}
      {...props}
    >
      {children}
    </div>
  );
};
AlertDialogHeader.displayName = "AlertDialogHeader";

interface AlertDialogTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

const AlertDialogTitle = React.forwardRef<HTMLHeadingElement, AlertDialogTitleProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <h2
        ref={ref}
        className={cn("text-lg font-semibold", className)}
        {...props}
      >
        {children}
      </h2>
    );
  }
);
AlertDialogTitle.displayName = "AlertDialogTitle";

interface AlertDialogDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

const AlertDialogDescription = React.forwardRef<HTMLParagraphElement, AlertDialogDescriptionProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn("text-sm text-gray-500", className)}
        {...props}
      >
        {children}
      </p>
    );
  }
);
AlertDialogDescription.displayName = "AlertDialogDescription";

interface AlertDialogFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const AlertDialogFooter = ({ className, children, ...props }: AlertDialogFooterProps) => {
  return (
    <div
      className={cn("mt-4 flex justify-end space-x-2", className)}
      {...props}
    >
      {children}
    </div>
  );
};
AlertDialogFooter.displayName = "AlertDialogFooter";

interface AlertDialogActionProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const AlertDialogAction = React.forwardRef<HTMLButtonElement, AlertDialogActionProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex h-10 items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white",
          "hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
          "disabled:pointer-events-none disabled:opacity-50",
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
AlertDialogAction.displayName = "AlertDialogAction";

interface AlertDialogCancelProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const AlertDialogCancel = React.forwardRef<HTMLButtonElement, AlertDialogCancelProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex h-10 items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium",
          "hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
          "disabled:pointer-events-none disabled:opacity-50",
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
AlertDialogCancel.displayName = "AlertDialogCancel";

export {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
  AlertDialogCancel
};