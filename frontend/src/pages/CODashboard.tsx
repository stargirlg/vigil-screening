import { useEffect, useState } from 'react'
import { getDashboardStats } from '../api/client'
import API from '../api/client'

export default function CODashboard() {
  const [stats, setStats]   = useState<any>(null)
  const [cases, setCases]   = useState<any[]>([])
  const [rules, setRules]   = useState<any[]>([])

  useEffect(() => {
    getDashboardStats().then(r => setStats(r.data)).catch(console.error)

    API.get('/cases?status=PENDING_CO').then(r => setCases(r.data)).catch(console.error)
    API.get('/rules').then(r => {
      setRules(r.data.filter((rule: any) => rule.status === 'DRAFT'))
    }).catch(console.error)
  }, [])

  return (
    <div style={{ flex: 1, padding: '24px', background: '#F4F1EA', overflowY: 'auto' }}>

      {/* CO Banner */}
      <div style={{
        background: '#F5EFE0', border: '0.5px solid #DDD6C9',
        borderRadius: '10px', padding: '14px 20px', marginBottom: '20px',
        display: 'flex', alignItems: 'center', gap: '12px',
      }}>
        <i className="ti ti-shield-check" style={{ color: '#7A5C2E', fontSize: '20px' }} />
        <div>
          <div style={{ fontSize: '13px', fontWeight: 500, color: '#7A5C2E' }}>Compliance Officer Dashboard</div>
          <div style={{ fontSize: '11px', color: '#8B9388' }}>Final decision authority · SAR filing · Rule approval</div>
        </div>
      </div>

      {/* Action cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '24px' }}>
        {[
          { icon: 'ti-folder-open',   label: 'Cases pending CO',   value: stats?.case_stats.pending_co || 0,          color: '#7A5C2E', bg: '#F5EFE0', desc: 'Require your decision' },
          { icon: 'ti-checklist',     label: 'Rules to approve',   value: rules.length,                                color: '#4338CA', bg: '#EEF2FF', desc: 'Pending maker-checker' },
          { icon: 'ti-file-invoice',  label: 'SAR required',       value: stats?.case_stats.sar_filed || 0,            color: '#8B4040', bg: '#F5E8E8', desc: 'FIU-IND filing needed' },
        ].map(card => (
          <div key={card.label} style={{
            background: card.bg, border: '0.5px solid #DDD6C9',
            borderRadius: '10px', padding: '16px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <i className={`ti ${card.icon}`} style={{ color: card.color, fontSize: '18px' }} />
              <div style={{ fontSize: '11px', color: '#8B9388' }}>{card.label}</div>
            </div>
            <div style={{ fontSize: '28px', fontWeight: 500, color: card.color, fontFamily: "'DM Mono', monospace" }}>
              {card.value}
            </div>
            <div style={{ fontSize: '11px', color: '#8B9388', marginTop: '4px' }}>{card.desc}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

        {/* Cases pending CO */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '0.5px solid #DDD6C9', display: 'flex', justifyContent: 'space-between' }}>
            <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D' }}>Cases awaiting decision</div>
            <span style={{ fontSize: '10px', color: '#8B9388' }}>{cases.length} pending</span>
          </div>
          {cases.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: '#8B9388', fontSize: '12px' }}>
              No cases pending CO decision
            </div>
          ) : (
            cases.map(c => (
              <div key={c.id} style={{
                padding: '12px 16px', borderBottom: '0.5px solid #F0ECE4',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', fontFamily: "'DM Mono', monospace" }}>
                    {c.case_number}
                  </div>
                  <div style={{ fontSize: '10px', color: '#8B9388', marginTop: '2px' }}>
                    Analyst: {c.analyst_recommendation || 'Pending'} · {c.assigned_email || '—'}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button style={{
                    padding: '4px 10px', fontSize: '11px', border: '0.5px solid #73856E',
                    borderRadius: '5px', background: '#73856E', color: 'white',
                    cursor: 'pointer', fontFamily: 'inherit',
                  }}>
                    Review
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Rules pending approval */}
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '0.5px solid #DDD6C9', display: 'flex', justifyContent: 'space-between' }}>
            <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D' }}>Rules pending approval</div>
            <span style={{ fontSize: '10px', color: '#8B9388' }}>{rules.length} draft</span>
          </div>
          {rules.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: '#8B9388', fontSize: '12px' }}>
              No rules pending approval
            </div>
          ) : (
            rules.map(r => (
              <div key={r.id} style={{
                padding: '12px 16px', borderBottom: '0.5px solid #F0ECE4',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D' }}>{r.name}</div>
                  <div style={{ fontSize: '10px', color: '#8B9388', marginTop: '2px' }}>
                    {r.param} · weight: {r.weight} · by {r.created_by_email}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '5px' }}>
                  <button style={{
                    padding: '4px 8px', fontSize: '10px', border: '0.5px solid #73856E',
                    borderRadius: '4px', background: '#73856E', color: 'white',
                    cursor: 'pointer', fontFamily: 'inherit',
                  }}>
                    Approve
                  </button>
                  <button style={{
                    padding: '4px 8px', fontSize: '10px', border: '0.5px solid #DDD6C9',
                    borderRadius: '4px', background: 'none', color: '#8B4040',
                    cursor: 'pointer', fontFamily: 'inherit',
                  }}>
                    Reject
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Performance metrics */}
      {stats && (
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px', marginTop: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '12px' }}>System performance</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
            {[
              { label: 'Total customers', value: stats.total_customers },
              { label: 'Total alerts',    value: stats.total_alerts },
              { label: 'Auto-closed',     value: stats.alert_breakdown.auto_closed },
              { label: 'Load reduction',  value: `${stats.performance.analyst_load_reduction_pct}%` },
            ].map(m => (
              <div key={m.label} style={{ padding: '10px', background: '#F6F3EE', borderRadius: '7px' }}>
                <div style={{ fontSize: '10px', color: '#8B9388', marginBottom: '4px' }}>{m.label}</div>
                <div style={{ fontSize: '18px', fontWeight: 500, color: '#495844', fontFamily: "'DM Mono', monospace" }}>{m.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}