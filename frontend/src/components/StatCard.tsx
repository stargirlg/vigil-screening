interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  color?: string
  icon?: React.ReactNode
}

export default function StatCard({ title, value, subtitle, color = '#1A4FB3', icon }: StatCardProps) {
  return (
    <div style={{
      background: 'white',
      border: '0.5px solid #E8ECF2',
      borderRadius: '10px',
      padding: '16px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ fontSize: '11px', color: '#8D99AE', fontWeight: 500 }}>{title}</div>
        {icon && <div style={{ color: '#CDD3DE' }}>{icon}</div>}
      </div>
      <div style={{ fontSize: '24px', fontWeight: 600, color, fontFamily: "'DM Mono', monospace" }}>
        {value}
      </div>
      {subtitle && (
        <div style={{ fontSize: '11px', color: '#8D99AE', marginTop: '4px' }}>{subtitle}</div>
      )}
    </div>
  )
}