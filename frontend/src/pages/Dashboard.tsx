import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import KpiCards from '../components/KpiCards'
import { getDashboardStats, getAlertTrend } from '../api/client'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const [trend, setTrend] = useState<any[]>([])

  useEffect(() => {
    getDashboardStats().then(r => setStats(r.data)).catch(console.error)
    getAlertTrend(7).then(r => setTrend(r.data.trend)).catch(console.error)
  }, [])

  if (!stats) return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8B9388', fontSize: '13px' }}>
      Loading...
    </div>
  )

  const distData = [
    { name: 'Critical', value: stats.risk_distribution.critical, fill: '#8B4040' },
    { name: 'High',     value: stats.risk_distribution.high,     fill: '#7A5C2E' },
    { name: 'Medium',   value: stats.risk_distribution.medium,   fill: '#73856E' },
    { name: 'Low',      value: stats.risk_distribution.low,      fill: '#8B9388' },
  ]

  return (
    <div style={{ flex: 1, padding: '24px', overflowY: 'auto', background: '#F4F1EA' }}>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '16px', fontWeight: 500, color: '#2D2D2D' }}>Executive overview</div>
        <div style={{ fontSize: '12px', color: '#8B9388', marginTop: '2px' }}>
          AML screening summary · {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
        </div>
      </div>

      <KpiCards stats={stats} />

      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '14px', marginBottom: '14px' }}>

        {/* Trend */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#495844', marginBottom: '14px' }}>Alert trend — 7 days</div>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={trend}>
              <XAxis dataKey="date" tick={{ fill: '#8B9388', fontSize: 9 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: '#8B9388', fontSize: 9 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '6px', fontSize: '11px' }} />
              <Line type="monotone" dataKey="total"       stroke="#73856E" strokeWidth={1.5} dot={false} name="Total" />
              <Line type="monotone" dataKey="high"        stroke="#7A5C2E" strokeWidth={1.5} dot={false} name="High" />
              <Line type="monotone" dataKey="auto_closed" stroke="#8B9388" strokeWidth={1.5} dot={false} strokeDasharray="3 3" name="Auto closed" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Distribution */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#495844', marginBottom: '14px' }}>Risk distribution</div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={distData} barSize={28}>
              <XAxis dataKey="name" tick={{ fill: '#8B9388', fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: '#8B9388', fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '6px', fontSize: '11px' }} />
              <Bar dataKey="value" radius={[3, 3, 0, 0]} fill="#73856E" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Performance */}
      <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
        <div style={{ fontSize: '12px', fontWeight: 500, color: '#495844', marginBottom: '14px' }}>Performance metrics</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '10px' }}>
          {[
            { label: 'Analyst load reduction', value: `${stats.performance.analyst_load_reduction_pct}%`, desc: 'alerts auto-closed' },
            { label: 'False positive rate',    value: `${stats.performance.false_positive_rate_pct}%`,    desc: 'of reviewed alerts' },
            { label: 'Avg TAT',                value: stats.performance.avg_tat_minutes ? `${Math.round(stats.performance.avg_tat_minutes)}m` : '—', desc: 'to resolution' },
            { label: 'Confirmed match rate',   value: `${stats.performance.confirmed_match_rate_pct}%`,  desc: 'of reviewed alerts' },
          ].map(m => (
            <div key={m.label} style={{ padding: '12px 14px', background: '#F6F3EE', borderRadius: '8px' }}>
              <div style={{ fontSize: '10px', color: '#8B9388', marginBottom: '6px' }}>{m.label}</div>
              <div style={{ fontSize: '22px', fontWeight: 500, color: '#495844', fontFamily: "'DM Mono', monospace" }}>{m.value}</div>
              <div style={{ fontSize: '10px', color: '#8B9388', marginTop: '3px' }}>{m.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}