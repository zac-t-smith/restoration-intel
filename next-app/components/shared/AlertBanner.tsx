interface AlertBannerProps {
  type: 'critical' | 'warning' | 'info'
  message: string
  details?: string
}

export function AlertBanner({ type, message, details }: AlertBannerProps) {
  const bgColor = {
    critical: 'bg-red-50 text-red-700',
    warning: 'bg-yellow-50 text-yellow-700',
    info: 'bg-blue-50 text-blue-700',
  }[type]

  return (
    <div className={`p-4 rounded-lg mb-4 ${bgColor}`}>
      <p className="font-medium">{message}</p>
      {details && <p className="text-sm mt-1">{details}</p>}
    </div>
  )
} 