/**
 * Toast Component
 *
 * A notification component for displaying messages
 */

import * as React from "react";
import { cn } from "@/lib/utils";

interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "error" | "warning";
  title?: string;
  description?: string;
  action?: React.ReactNode;
  duration?: number;
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ className, variant = "default", title, description, action, ...props }, ref) => {
    const variantStyles = {
      default: "bg-white border-gray-200",
      success: "bg-green-50 border-green-200",
      error: "bg-red-50 border-red-200",
      warning: "bg-yellow-50 border-yellow-200",
    };

    return (
      <div
        ref={ref}
        className={cn(
          "pointer-events-auto relative flex w-full max-w-sm items-center overflow-hidden rounded-lg border p-4 shadow-md",
          variantStyles[variant],
          className
        )}
        {...props}
      >
        <div className="grid gap-1">
          {title && <div className="text-sm font-semibold">{title}</div>}
          {description && <div className="text-sm text-gray-500">{description}</div>}
        </div>
        {action && <div className="ml-auto">{action}</div>}
      </div>
    );
  }
);
Toast.displayName = "Toast";

interface ToastViewportProps extends React.HTMLAttributes<HTMLDivElement> {}

const ToastViewport = React.forwardRef<HTMLDivElement, ToastViewportProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "fixed bottom-0 right-0 z-50 flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]",
          className
        )}
        {...props}
      />
    );
  }
);
ToastViewport.displayName = "ToastViewport";

// Toast provider context
type ToastContextValue = {
  toasts: ToastProps[];
  addToast: (toast: ToastProps) => void;
  removeToast: (toastId: string) => void;
};

const ToastContext = React.createContext<ToastContextValue | undefined>(undefined);

interface ToastProviderProps {
  children: React.ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = React.useState<(ToastProps & { id: string })[]>([]);
  
  const addToast = React.useCallback((toast: ToastProps) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast = { ...toast, id };
    
    setToasts((prevToasts) => [...prevToasts, newToast]);
    
    // Auto-dismiss toast after duration
    if (toast.duration !== undefined && toast.duration > 0) {
      setTimeout(() => {
        setToasts((prevToasts) => prevToasts.filter((t) => t.id !== id));
      }, toast.duration);
    }
  }, []);
  
  const removeToast = React.useCallback((id: string) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  }, []);
  
  return (
    <ToastContext.Provider value={{ toasts: toasts as ToastProps[], addToast, removeToast }}>
      {children}
      <ToastViewport>
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            variant={toast.variant}
            title={toast.title}
            description={toast.description}
            action={toast.action}
            className="mb-2"
          />
        ))}
      </ToastViewport>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = React.useContext(ToastContext);
  
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  
  return {
    toast: context.addToast,
    dismiss: context.removeToast,
  };
}

export { Toast, ToastViewport };