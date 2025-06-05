import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Database = {
  public: {
    Tables: {
      projects: {
        Row: {
          id: number
          name: string
          status: string
          total_revenue: number
          start_date: string
          updated_at: string
        }
      }
      collections: {
        Row: {
          id: number
          project_id: number
          amount: number
          confidence_percentage: number
        }
      }
      leading_indicators: {
        Row: {
          id: number
          kpi_code: string
          value: number
          captured_at: string
          rule_breached: any
        }
      }
    }
  }
} 