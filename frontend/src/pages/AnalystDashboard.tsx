import { useEffect, useState } from 'react'
import { getDashboardStats } from '../api/client'
import AlertQueue from './AlertQueue'

export default function AnalystDashboard() {
  const [stats, setStats] = useState<any>(null)
  const [view, setView]   = useState<'dashboard' | 'queue'>('dashboard')

  useEffect(() => {
    getDashboardStats().then(r => setStats(r.data)).catch(console.error)
  }, [])

  if (view === 'queue') return (
    <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '8px 16px', background: '#EEF2FF', borderBottom: '0.5px solid #C7D2FE', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button onClick={() => setView('dashboard')} style={{ fontSize: '11px', color: '#4338CA', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <i className="ti ti-arrow-left" /> Back to Dashboard
        </button>
      </div>
      <AlertQueue />
    </div>
  )

  return (
    <div style={{ flex: 1, padding: '24px', background: '#F4F1EA', overflowY: 'auto' }}>

      {/* Analyst banner */}
      <div style={{
        background: '#EEF2FF', border: '0.5px solid #C7D2FE',
        borderRadius: '10px', padding: '14px 20px', marginBottom: '20px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <i className="ti ti-search" style={{ color: '#4338CA', fontSize: '20px' }} />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 500, color: '#4338CA' }}>
              Analyst Dashboard
            </div>
            <div style={{ fontSize: '11px', color: '#6366F1' }}>
              Review alerts · Add notes · Recommend decisions
            </div>
          </div>
        </div>
        <button onClick={() => setView('queue')} style={{
          padding: '7px 16px', fontSize: '12px', fontWeight: 500,
          background: '#4338CA', color: 'white', border: 'none',
          borderRadius: '6px', cursor: 'pointer', fontFamily: 'inherit',
          display: 'flex', alignItems: 'center', gap: '6px',
        }}>
          <i className="ti ti-shield-check" />
          Open Alert Queue
        </button>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
        {[
          { label: 'Pending Reviews',  value: stats?.alert_breakdown.pending_review || 0,   color: '#4338CA', bg: '#EEF2FF', icon: 'ti-clock' },
          { label: 'Critical Alerts',  value: stats?.risk_distribution.critical || 0,        color: '#8B4040', bg: '#F5E8E8', icon: 'ti-alert-triangle' },
          { label: 'High Alerts',      value: stats?.risk_distribution.high || 0,            color: '#7A5C2E', bg: '#F5EFE0', icon: 'ti-alert-circle' },
          { label: 'Confirmed Matches',value: stats?.alert_breakdown.confirmed_matches || 0, color: '#495844', bg: '#EDF2E8', icon: 'ti-circle-check' },
        ].map(card => (
          <div key={card.label} style={{
            background: card.bg, border: '0.5px solid #DDD6C9',
            borderRadius: '10px', padding: '16px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <i className={`ti ${card.icon}`} style={{ color: card.color, fontSize: '18px' }} />
              <div style={{ fontSize: '11px', color: '#8B9388' }}>{card.label}</div>
            </div>
            <div style={{ fontSize: '28px', fontWeight: 600, color: card.color, fontFamily: "'DM Mono', monospace" }}>
              {card.value}
            </div>
          </div>
        ))}
      </div>

      {/* My Work Queue */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>

        {/* Quick actions */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '14px' }}>
            Quick actions
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              { label: 'Review pending alerts', icon: 'ti-shield-check', color: '#4338CA', action: () => setView('queue') },
              { label: 'View critical alerts',  icon: 'ti-alert-triangle', color: '#8B4040', action: () => setView('queue') },
              { label: 'Check SLA breaches',    icon: 'ti-clock', color: '#7A5C2E', action: () => setView('queue') },
            ].map(item => (
              <button key={item.label} onClick={item.action} style={{
                display: 'flex', alignItems: 'center', gap: '10px',
                padding: '10px 12px', borderRadius: '7px',
                background: '#F6F3EE', border: '0.5px solid #DDD6C9',
                cursor: 'pointer', fontFamily: 'inherit', textAlign: 'left', width: '100%',
              }}>
                <i className={`ti ${item.icon}`} style={{ color: item.color, fontSize: '16px' }} />
                <span style={{ fontSize: '12px', color: '#2D2D2D' }}>{item.label}</span>
                <i className="ti ti-chevron-right" style={{ marginLeft: 'auto', color: '#8B9388', fontSize: '13px' }} />
              </button>
            ))}
          </div>
        </div>

        {/* System stats */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '14px' }}>
            System overview
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[
              { label: 'Total customers',   value: stats?.total_customers || 0,                              color: '#495844' },
              { label: 'Total alerts',      value: stats?.total_alerts || 0,                                 color: '#4A5568' },
              { label: 'Auto-closed',       value: stats?.alert_breakdown.auto_closed || 0,                  color: '#495844' },
              { label: 'Load reduction',    value: `${stats?.performance.analyst_load_reduction_pct || 0}%`, color: '#73856E' },
              { label: 'False positive %',  value: `${stats?.performance.false_positive_rate_pct || 0}%`,    color: '#7A5C2E' },
              { label: 'Open cases',        value: stats?.case_stats.open || 0,                              color: '#4338CA' },
            ].map(item => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 0', borderBottom: '0.5px solid #F0ECE4' }}>
                <span style={{ fontSize: '12px', color: '#8B9388' }}>{item.label}</span>
                <span style={{ fontSize: '13px', fontWeight: 600, color: item.color, fontFamily: "'DM Mono', monospace" }}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent activity */}
      <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
        <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '12px' }}>
          Risk distribution
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
          {[
            { label: 'CRITICAL', value: stats?.risk_distribution.critical || 0, bg: '#F5E8E8', color: '#8B4040', border: '#F5C6C6' },
            { label: 'HIGH',     value: stats?.risk_distribution.high || 0,     bg: '#F5EFE0', color: '#7A5C2E', border: '#E8D5B0' },
            { label: 'MEDIUM',   value: stats?.risk_distribution.medium || 0,   bg: '#FEFCE8', color: '#854D0E', border: '#FEF08A' },
            { label: 'LOW',      value: stats?.risk_distribution.low || 0,      bg: '#EDF2E8', color: '#495844', border: '#D4E3CC' },
          ].map(r => (
            <div key={r.label} style={{
              background: r.bg, border: `0.5px solid ${r.border}`,
              borderRadius: '8px', padding: '14px', textAlign: 'center',
            }}>
              <div style={{ fontSize: '10px', fontWeight: 500, color: r.color, marginBottom: '6px', letterSpacing: '0.05em' }}>{r.label}</div>
              <div style={{ fontSize: '28px', fontWeight: 600, color: r.color, fontFamily: "'DM Mono', monospace" }}>{r.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}