import { useEffect, useState } from 'react'
import { getDashboardStats } from '../api/client'
import AlertQueue from './AlertQueue'

export default function CheckerDashboard() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    getDashboardStats().then(r => setStats(r.data)).catch(console.error)
  }, [])

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'white', overflow: 'hidden' }}>

      {/* Checker banner */}
      <div style={{
        background: '#FEFCE8', borderBottom: '0.5px solid #FEF08A',
        padding: '10px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <i className="ti ti-checks" style={{ color: '#854D0E', fontSize: '16px' }} />
          <div>
            <div style={{ fontSize: '12px', fontWeight: 500, color: '#854D0E' }}>Checker Workspace</div>
            <div style={{ fontSize: '11px', color: '#92400E' }}>
              Second review · Four-eyes control · Escalate to CO
            </div>
          </div>
        </div>
        {stats && (
          <div style={{ display: 'flex', gap: '20px' }}>
            {[
              { label: 'Pending',  value: stats.alert_breakdown.pending_review,   color: '#854D0E' },
              { label: 'Critical', value: stats.risk_distribution.critical,        color: '#8B4040' },
              { label: 'Cases',    value: stats.case_stats.total,                  color: '#495844' },
            ].map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '18px', fontWeight: 600, color: s.color, fontFamily: "'DM Mono', monospace" }}>{s.value}</div>
                <div style={{ fontSize: '10px', color: '#8B9388' }}>{s.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        <AlertQueue />
      </div>
    </div>
  )
}