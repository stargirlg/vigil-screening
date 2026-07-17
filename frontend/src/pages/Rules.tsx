import { useEffect, useState } from 'react'
import API from '../api/client'

export default function Rules() {
  const [rules, setRules]   = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const role = localStorage.getItem('role')

  useEffect(() => {
    API.get('/rules').then(r => {
      setRules(r.data)
      setLoading(false)
    }).catch(console.error)
  }, [])

  const approve = async (id: string, approved: boolean) => {
    try {
      await API.post(`/rules/${id}/approve`, {
        approved,
        notes: approved ? 'Approved by CO' : 'Rejected by CO',
      })
      const r = await API.get('/rules')
      setRules(r.data)
    } catch (e) { console.error(e) }
  }

  const STATUS_COLOR: Record<string, { bg: string; color: string }> = {
    ACTIVE:   { bg: '#EDF2E8', color: '#495844' },
    DRAFT:    { bg: '#EEF2FF', color: '#4338CA' },
    REJECTED: { bg: '#F5E8E8', color: '#8B4040' },
    INACTIVE: { bg: '#F6F3EE', color: '#8B9388' },
  }

  return (
    <div style={{ flex: 1, padding: '24px', background: '#F4F1EA', overflowY: 'auto' }}>

      <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: '16px', fontWeight: 500, color: '#2D2D2D' }}>Rule engine</div>
          <div style={{ fontSize: '12px', color: '#8B9388', marginTop: '2px' }}>
            Maker-checker · Admin creates → CO approves → Rule goes live
          </div>
        </div>
        <div style={{ fontSize: '11px', color: '#8B9388', background: '#F6F3EE', padding: '6px 12px', borderRadius: '6px', border: '0.5px solid #DDD6C9' }}>
          {rules.filter(r => r.status === 'ACTIVE').length} active · {rules.filter(r => r.status === 'DRAFT').length} pending approval
        </div>
      </div>

      <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', overflow: 'hidden' }}>
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 100px 70px 80px 120px 160px',
          gap: '8px', padding: '8px 16px',
          fontSize: '10px', color: '#8B9388',
          letterSpacing: '0.05em', textTransform: 'uppercase',
          borderBottom: '0.5px solid #DDD6C9',
        }}>
          <div>Rule name</div><div>Parameter</div><div>Weight</div><div>Status</div><div>Version</div><div>Actions</div>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>Loading rules...</div>
        ) : (
          rules.map(r => {
            const s = STATUS_COLOR[r.status] || STATUS_COLOR.INACTIVE
            return (
              <div key={r.id} style={{
                display: 'grid', gridTemplateColumns: '1fr 100px 70px 80px 120px 160px',
                gap: '8px', padding: '10px 16px', alignItems: 'center',
                borderBottom: '0.5px solid #F0ECE4', fontSize: '12px',
              }}>
                <div>
                  <div style={{ fontWeight: 500, color: '#2D2D2D' }}>{r.name}</div>
                  {r.description && <div style={{ fontSize: '10px', color: '#8B9388', marginTop: '1px' }}>{r.description}</div>}
                </div>
                <div style={{ color: '#495844', fontFamily: "'DM Mono', monospace", fontSize: '11px' }}>{r.param}</div>
                <div style={{ color: '#2D2D2D', fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>{r.weight}</div>
                <div>
                  <span style={{ fontSize: '10px', fontWeight: 500, padding: '2px 6px', borderRadius: '3px', background: s.bg, color: s.color }}>
                    {r.status}
                  </span>
                </div>
                <div style={{ color: '#8B9388', fontSize: '10px' }}>
                  v{r.version} · {r.rule_set_version}
                  <div style={{ marginTop: '1px' }}>{r.approved_by_email?.split('@')[0] || r.created_by_email?.split('@')[0]}</div>
                </div>
                <div style={{ display: 'flex', gap: '5px' }}>
                  {r.status === 'DRAFT' && role === 'CO' && (
                    <>
                      <button onClick={() => approve(r.id, true)} style={{
                        padding: '4px 8px', fontSize: '10px', fontWeight: 500,
                        border: 'none', borderRadius: '4px', background: '#73856E',
                        color: 'white', cursor: 'pointer', fontFamily: 'inherit',
                      }}>Approve</button>
                      <button onClick={() => approve(r.id, false)} style={{
                        padding: '4px 8px', fontSize: '10px',
                        border: '0.5px solid #DDD6C9', borderRadius: '4px',
                        background: 'none', color: '#8B4040', cursor: 'pointer', fontFamily: 'inherit',
                      }}>Reject</button>
                    </>
                  )}
                  {r.status === 'DRAFT' && role !== 'CO' && (
                    <span style={{ fontSize: '10px', color: '#8B9388' }}>Awaiting CO</span>
                  )}
                  {r.status === 'ACTIVE' && (
                    <span style={{ fontSize: '10px', color: '#495844' }}>✓ Live</span>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}