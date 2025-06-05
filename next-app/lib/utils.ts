/**
 * Utility functions for the application
 */

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges class names with tailwind classes
 * 
 * This function combines clsx and tailwind-merge to provide a utility for
 * conditionally applying Tailwind CSS classes and resolving conflicts.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format currency values
 * 
 * @param value - Numeric value to format as currency
 * @param currency - Currency code (default: 'USD')
 * @returns Formatted currency string
 */
export function formatCurrency(value: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(value);
}

/**
 * Format date values
 * 
 * @param date - Date to format
 * @param options - Date formatting options
 * @returns Formatted date string
 */
export function formatDate(
  date: Date | string,
  options: Intl.DateTimeFormatOptions = { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  }
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('en-US', options).format(dateObj);
}

/**
 * Calculate days until a future date
 * 
 * @param targetDate - Future date
 * @returns Number of days until the date, or 0 if date is in the past
 */
export function daysUntil(targetDate: Date | string): number {
  const target = typeof targetDate === 'string' ? new Date(targetDate) : targetDate;
  const today = new Date();
  
  // Reset time to midnight for accurate day calculation
  today.setHours(0, 0, 0, 0);
  const targetWithoutTime = new Date(target);
  targetWithoutTime.setHours(0, 0, 0, 0);
  
  const diffTime = targetWithoutTime.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays > 0 ? diffDays : 0;
}

/**
 * Truncate text with ellipsis
 * 
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncating
 * @returns Truncated text with ellipsis if necessary
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
}

/**
 * Safe division to avoid division by zero errors
 * 
 * @param numerator - Top value in division
 * @param denominator - Bottom value in division
 * @param fallback - Value to return if denominator is zero (default: 0)
 * @returns Result of division or fallback value
 */
export function safeDivide(numerator: number, denominator: number, fallback: number = 0): number {
  if (denominator === 0) return fallback;
  return numerator / denominator;
}

/**
 * Calculate percentage
 * 
 * @param value - Current value
 * @param total - Total value
 * @param decimals - Number of decimal places (default: 1)
 * @returns Percentage as a number
 */
export function calculatePercentage(value: number, total: number, decimals: number = 1): number {
  if (total === 0) return 0;
  return parseFloat(((value / total) * 100).toFixed(decimals));
}

/**
 * Get initials from a name
 * 
 * @param name - Full name
 * @returns Initials (up to 2 characters)
 */
export function getInitials(name: string): string {
  if (!name) return '';
  
  const parts = name.split(' ').filter(Boolean);
  if (parts.length === 0) return '';
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}