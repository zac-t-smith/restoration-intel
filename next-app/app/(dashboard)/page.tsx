import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { AlertBanner } from '@/components/shared/AlertBanner'
import { Plot } from '@/components/charts/Plot'

export default async function DashboardPage() {
  const supabase = createServerComponentClient({ cookies })
  
  const { data: alerts } = await supabase
    .from('alerts')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(5)
  
  const { data: trends } = await supabase
    .from('trends')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(5)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Recent Alerts</h2>
          {alerts?.map((alert) => (
            <AlertBanner
              key={alert.id}
              type={alert.type}
              message={alert.message}
              details={alert.details}
            />
          ))}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Trends</h2>
          {trends?.map((trend) => (
            <div
              key={trend.id}
              className={`p-4 rounded-lg mb-4 ${
                trend.direction === 'improving'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              <p className="font-medium">{trend.message}</p>
              <p className="text-sm mt-1">{trend.details}</p>
            </div>
          ))}
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-4">Performance Metrics</h2>
        <Plot />
      </div>
    </div>
  )
} 