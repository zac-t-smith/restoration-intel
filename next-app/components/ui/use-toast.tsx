/**
 * useToast Hook
 *
 * Hook for displaying toast notifications
 */

import { useToast as useToastInternal } from "./toast";

export { useToast } from "./toast";

export type ToastProps = {
  variant?: "default" | "success" | "error" | "warning";
  title?: string;
  description?: string;
  action?: React.ReactNode;
  duration?: number;
};