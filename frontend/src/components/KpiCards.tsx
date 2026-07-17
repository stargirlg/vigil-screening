interface KpiCardsProps {
  stats: any
}

export default function KpiCards({ stats }: KpiCardsProps) {
  const cards = [
    {
      label: 'Customers screened',
      value: stats.total_customers,
      sub: 'total in system',
      color: '#495844',
    },
    {
      label: 'Pending review',
      value: stats.alert_breakdown.pending_review,
      sub: 'in analyst queue',
      color: '#73856E',
    },
    {
      label: 'Auto-closed',
      value: stats.alert_breakdown.auto_closed,
      sub: `${stats.performance.analyst_load_reduction_pct}% load reduction`,
      color: '#495844',
    },
    {
      label: 'Confirmed matches',
      value: stats.alert_breakdown.confirmed_matches,
      sub: 'sanctioned entities',
      color: '#8B4040',
    },
    {
      label: 'Open cases',
      value: stats.case_stats.open,
      sub: 'under investigation',
      color: '#73856E',
    },
    {
      label: 'SLA breached',
      value: stats.case_stats.sla_breached,
      sub: 'need immediate action',
      color: stats.case_stats.sla_breached > 0 ? '#8B4040' : '#495844',
    },
  ]

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
      gap: '10px',
      marginBottom: '24px',
    }}>
      {cards.map(c => (
        <div key={c.label} style={{
          background: '#F6F3EE',
          border: '0.5px solid #DDD6C9',
          borderRadius: '10px',
          padding: '14px 16px',
        }}>
          <div style={{ fontSize: '11px', color: '#8B9388', marginBottom: '8px' }}>{c.label}</div>
          <div style={{
            fontSize: '26px', fontWeight: 500, color: c.color,
            fontFamily: "'DM Mono', monospace", lineHeight: 1,
          }}>
            {c.value}
          </div>
          <div style={{ fontSize: '11px', color: '#8B9388', marginTop: '5px' }}>{c.sub}</div>
        </div>
      ))}
    </div>
  )
}