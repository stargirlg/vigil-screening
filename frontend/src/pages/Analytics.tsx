import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { getDashboardStats, getAlertTrend } from '../api/client'

export default function Analytics() {
  const [stats, setStats] = useState<any>(null)
  const [trend, setTrend] = useState<any[]>([])

  useEffect(() => {
    getDashboardStats().then(r => setStats(r.data)).catch(console.error)
    getAlertTrend(30).then(r => setTrend(r.data.trend)).catch(console.error)
  }, [])

  if (!stats) return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8B9388', fontSize: '13px' }}>
      Loading analytics...
    </div>
  )

  const riskData = [
    { name: 'Critical', value: stats.risk_distribution.critical, color: '#8B4040' },
    { name: 'High',     value: stats.risk_distribution.high,     color: '#7A5C2E' },
    { name: 'Medium',   value: stats.risk_distribution.medium,   color: '#73856E' },
    { name: 'Low',      value: stats.risk_distribution.low,      color: '#8B9388' },
  ]

  const alertData = [
    { name: 'Auto closed',  value: stats.alert_breakdown.auto_closed,         color: '#73856E' },
    { name: 'Pending',      value: stats.alert_breakdown.pending_review,       color: '#7A5C2E' },
    { name: 'Confirmed',    value: stats.alert_breakdown.confirmed_matches,    color: '#8B4040' },
    { name: 'Cleared',      value: stats.alert_breakdown.cleared,              color: '#495844' },
    { name: 'Escalated',    value: stats.alert_breakdown.escalated,            color: '#4338CA' },
  ]

  return (
    <div style={{ flex: 1, padding: '24px', background: '#F4F1EA', overflowY: 'auto' }}>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '16px', fontWeight: 500, color: '#2D2D2D' }}>Analytics</div>
        <div style={{ fontSize: '12px', color: '#8B9388', marginTop: '2px' }}>Screening trends and performance metrics</div>
      </div>

      {/* KPI row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '20px' }}>
        {[
          { label: 'Load reduction',   value: `${stats.performance.analyst_load_reduction_pct}%`, color: '#495844' },
          { label: 'False positive',   value: `${stats.performance.false_positive_rate_pct}%`,    color: '#7A5C2E' },
          { label: 'Match rate',       value: `${stats.performance.confirmed_match_rate_pct}%`,   color: '#8B4040' },
          { label: 'Avg TAT',          value: stats.performance.avg_tat_minutes ? `${Math.round(stats.performance.avg_tat_minutes)}m` : '—', color: '#73856E' },
        ].map(m => (
          <div key={m.label} style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '14px' }}>
            <div style={{ fontSize: '11px', color: '#8B9388', marginBottom: '8px' }}>{m.label}</div>
            <div style={{ fontSize: '26px', fontWeight: 500, color: m.color, fontFamily: "'DM Mono', monospace" }}>{m.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '16px', marginBottom: '16px' }}>

        {/* 30 day trend */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#495844', marginBottom: '14px' }}>Alert trend — 30 days</div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={trend}>
              <XAxis dataKey="date" tick={{ fill: '#8B9388', fontSize: 9 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: '#8B9388', fontSize: 9 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '6px', fontSize: '11px' }} />
              <Line type="monotone" dataKey="total"       stroke="#73856E" strokeWidth={1.5} dot={false} name="Total" />
              <Line type="monotone" dataKey="high"        stroke="#8B4040" strokeWidth={1.5} dot={false} name="High/Critical" />
              <Line type="monotone" dataKey="auto_closed" stroke="#8B9388" strokeWidth={1.5} dot={false} strokeDasharray="3 3" name="Auto closed" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk pie */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#495844', marginBottom: '14px' }}>Risk distribution</div>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, value }) => `${name}: ${value}`} labelLine={false} fontSize={10}>
                {riskData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '6px', fontSize: '11px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alert breakdown bar */}
      <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
        <div style={{ fontSize: '12px', fontWeight: 500, color: '#495844', marginBottom: '14px' }}>Alert breakdown</div>
        <ResponsiveContainer width="100%" height={140}>
          <BarChart data={alertData} barSize={32}>
            <XAxis dataKey="name" tick={{ fill: '#8B9388', fontSize: 10 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fill: '#8B9388', fontSize: 10 }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '6px', fontSize: '11px' }} />
            <Bar dataKey="value" radius={[3, 3, 0, 0]} fill="#73856E" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}