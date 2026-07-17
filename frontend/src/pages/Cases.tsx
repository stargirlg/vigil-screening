import { useEffect, useState } from 'react'
import API from '../api/client'

const STATUS_COLOR: Record<string, { bg: string; color: string }> = {
  OPEN:          { bg: '#EEF2FF', color: '#4338CA' },
  INVESTIGATING: { bg: '#FFF7ED', color: '#EA580C' },
  PENDING_CO:    { bg: '#F5EFE0', color: '#7A5C2E' },
  CLOSED:        { bg: '#EDF2E8', color: '#495844' },
}

export default function Cases() {
  const [cases, setCases]     = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<any>(null)
  const [notes, setNotes]     = useState<any[]>([])
  const [filter, setFilter]   = useState('ALL')

  useEffect(() => {
    API.get('/cases').then(r => {
      setCases(r.data)
      setLoading(false)
    }).catch(console.error)
  }, [])

  const selectCase = async (c: any) => {
    setSelected(c)
    try {
      const r = await API.get(`/cases/${c.id}/notes`)
      setNotes(r.data)
    } catch { setNotes([]) }
  }

  const filtered = cases.filter(c => filter === 'ALL' || c.status === filter)

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#F4F1EA', height: 'calc(100vh - 48px)' }}>

      {/* Header */}
      <div style={{ padding: '12px 20px', borderBottom: '0.5px solid #DDD6C9', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 500, color: '#2D2D2D' }}>Cases</div>
          <div style={{ fontSize: '11px', color: '#8B9388', marginTop: '1px' }}>{cases.length} total cases</div>
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          {['ALL', 'OPEN', 'INVESTIGATING', 'PENDING_CO', 'CLOSED'].map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{
              padding: '4px 10px', borderRadius: '20px', fontSize: '11px',
              cursor: 'pointer', border: '0.5px solid', fontFamily: 'inherit',
              background: filter === f ? '#73856E' : 'none',
              borderColor: filter === f ? '#73856E' : '#DDD6C9',
              color: filter === f ? 'white' : '#8B9388',
            }}>
              {f.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* Case list */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <div style={{
            display: 'grid', gridTemplateColumns: '140px 1fr 100px 100px 80px',
            gap: '8px', padding: '8px 20px',
            fontSize: '10px', color: '#8B9388',
            letterSpacing: '0.05em', textTransform: 'uppercase',
            borderBottom: '0.5px solid #DDD6C9', background: 'white',
          }}>
            <div>Case No.</div><div>Customer</div><div>Status</div><div>SLA</div><div>SAR</div>
          </div>

          {loading ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>Loading cases...</div>
          ) : filtered.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>
              No cases found. Create a case from the Alert Queue.
            </div>
          ) : (
            filtered.map(c => {
              const s = STATUS_COLOR[c.status] || { bg: '#F6F3EE', color: '#8B9388' }
              const slaBreached = c.sla_deadline && new Date(c.sla_deadline) < new Date() && c.status !== 'CLOSED'
              return (
                <div key={c.id}
                  onClick={() => selectCase(c)}
                  style={{
                    display: 'grid', gridTemplateColumns: '140px 1fr 100px 100px 80px',
                    gap: '8px', padding: '10px 20px', alignItems: 'center',
                    borderBottom: '0.5px solid #F0ECE4', cursor: 'pointer',
                    background: selected?.id === c.id ? '#F6F3EE' : 'white',
                    borderLeft: selected?.id === c.id ? '2px solid #73856E' : '2px solid transparent',
                  }}
                  onMouseOver={e => { if (selected?.id !== c.id) e.currentTarget.style.background = '#FAFAF8' }}
                  onMouseOut={e  => { if (selected?.id !== c.id) e.currentTarget.style.background = 'white' }}
                >
                  <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', fontFamily: "'DM Mono', monospace" }}>{c.case_number}</div>
                  <div style={{ fontSize: '11px', color: '#4A5568', fontFamily: "'DM Mono', monospace" }}>{c.customer_id?.slice(0, 12)}…</div>
                  <div>
                    <span style={{ fontSize: '10px', fontWeight: 500, padding: '2px 6px', borderRadius: '3px', background: s.bg, color: s.color }}>
                      {c.status?.replace('_', ' ')}
                    </span>
                  </div>
                  <div style={{ fontSize: '10px', color: slaBreached ? '#8B4040' : '#8B9388' }}>
                    {c.sla_deadline ? new Date(c.sla_deadline).toLocaleDateString('en-IN') : '—'}
                    {slaBreached && ' ⚠'}
                  </div>
                  <div style={{ fontSize: '10px', color: c.sar_required ? '#8B4040' : '#8B9388' }}>
                    {c.sar_required ? '⚑ YES' : 'NO'}
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Detail panel */}
        {selected ? (
          <div style={{ width: '300px', flexShrink: 0, borderLeft: '0.5px solid #DDD6C9', background: '#FAFAF8', padding: '16px', overflowY: 'auto' }}>
            <div style={{ fontSize: '13px', fontWeight: 500, color: '#2D2D2D', fontFamily: "'DM Mono', monospace", marginBottom: '4px' }}>{selected.case_number}</div>

            {[
              { label: 'Status',      value: selected.status?.replace('_', ' ') },
              { label: 'Rule version', value: selected.rule_version },
              { label: 'SAR required', value: selected.sar_required ? 'YES' : 'NO' },
              { label: 'Decision locked', value: selected.decision_locked ? 'YES' : 'NO' },
              { label: 'Created',     value: selected.created_at?.slice(0, 10) },
              { label: 'Closed',      value: selected.closed_at?.slice(0, 10) || '—' },
            ].map(f => (
              <div key={f.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '0.5px solid #F0ECE4', fontSize: '12px' }}>
                <span style={{ color: '#8B9388' }}>{f.label}</span>
                <span style={{ color: '#2D2D2D', fontWeight: 500 }}>{f.value}</span>
              </div>
            ))}

            {selected.analyst_recommendation && (
              <>
                <div style={{ fontSize: '10px', color: '#8B9388', textTransform: 'uppercase', letterSpacing: '0.06em', margin: '14px 0 8px' }}>Analyst recommendation</div>
                <div style={{ fontSize: '12px', color: '#495844', background: '#EDF2E8', padding: '8px 10px', borderRadius: '6px', marginBottom: '8px' }}>
                  {selected.analyst_recommendation}
                </div>
                {selected.analyst_notes && (
                  <div style={{ fontSize: '11px', color: '#4A5568' }}>{selected.analyst_notes}</div>
                )}
              </>
            )}

            {selected.co_decision && (
              <>
                <div style={{ fontSize: '10px', color: '#8B9388', textTransform: 'uppercase', letterSpacing: '0.06em', margin: '14px 0 8px' }}>CO decision</div>
                <div style={{ fontSize: '12px', color: '#7A5C2E', background: '#F5EFE0', padding: '8px 10px', borderRadius: '6px', marginBottom: '8px' }}>
                  {selected.co_decision}
                </div>
              </>
            )}

            {notes.length > 0 && (
              <>
                <div style={{ fontSize: '10px', color: '#8B9388', textTransform: 'uppercase', letterSpacing: '0.06em', margin: '14px 0 8px' }}>
                  Notes ({notes.length})
                </div>
                {notes.map(n => (
                  <div key={n.id} style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '6px', padding: '8px 10px', marginBottom: '6px' }}>
                    <div style={{ fontSize: '10px', color: '#8B9388', marginBottom: '4px' }}>
                      {n.author_email} · {n.note_type} · {n.created_at?.slice(0, 10)}
                    </div>
                    <div style={{ fontSize: '12px', color: '#2D2D2D' }}>{n.note}</div>
                  </div>
                ))}
              </>
            )}

            {/* Download report */}
            <div style={{ marginTop: '16px', display: 'flex', gap: '6px' }}>
              <button
               onClick={async () => {
  const token = localStorage.getItem('token')
  const res = await fetch(`/api/reports/case/${selected.id}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank')
}}





                style={{
                  flex: 1, padding: '7px', fontSize: '11px', fontWeight: 500,
                  border: '0.5px solid #73856E', borderRadius: '6px',
                  background: '#73856E', color: 'white', cursor: 'pointer', fontFamily: 'inherit',
                }}>
                <i className="ti ti-download" style={{ marginRight: '4px' }} />
                Case PDF
              </button>
              {selected.sar_required && (
                <button
                 onClick={async () => {
  const token = localStorage.getItem('token')
  const res = await fetch(`/api/reports/case/${selected.id}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank')
}}
                




                  style={{
                    flex: 1, padding: '7px', fontSize: '11px', fontWeight: 500,
                    border: '0.5px solid #8B4040', borderRadius: '6px',
                    background: '#8B4040', color: 'white', cursor: 'pointer', fontFamily: 'inherit',
                  }}>
                  <i className="ti ti-file-invoice" style={{ marginRight: '4px' }} />
                  SAR PDF
                </button>
              )}
            </div>
          </div>
        ) : (
          <div style={{ width: '300px', flexShrink: 0, borderLeft: '0.5px solid #DDD6C9', background: '#FAFAF8', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#8B9388', gap: '8px' }}>
            <i className="ti ti-folder" style={{ fontSize: '32px', color: '#DDD6C9' }} />
            <div style={{ fontSize: '13px' }}>Select a case</div>
          </div>
        )}
      </div>
    </div>
  )
}