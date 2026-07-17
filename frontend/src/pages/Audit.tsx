import { useEffect, useState } from 'react'
import API from '../api/client'

const ACTION_COLOR: Record<string, string> = {
  ALERT_REVIEWED:                '#495844',
  WATCHLIST_ENTRY_ADDED:         '#7A5C2E',
  ANALYST_RECOMMENDATION_SUBMITTED: '#4338CA',
  CO_DECISION_MADE:              '#8B4040',
  RULE_CREATED:                  '#73856E',
  RULE_APPROVED:                 '#495844',
  RULE_REJECTED:                 '#8B4040',
  SLA_BREACHED:                  '#8B4040',
}

export default function Audit() {
  const [logs, setLogs]     = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    API.get('/audit').then(r => {
      setLogs(r.data)
      setLoading(false)
    }).catch(console.error)
  }, [])

  const downloadPDF = async () => {
  setDownloading(true)
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/reports/audit', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `VIGIL-Audit-${new Date().toISOString().slice(0,10)}.pdf`
    a.click()
  } finally { setDownloading(false) }
}













  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#F4F1EA', height: 'calc(100vh - 48px)' }}>

      {/* Header */}
      <div style={{ padding: '12px 20px', borderBottom: '0.5px solid #DDD6C9', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 500, color: '#2D2D2D' }}>Audit trail</div>
          <div style={{ fontSize: '11px', color: '#8B9388', marginTop: '1px' }}>Immutable compliance log · {logs.length} entries</div>
        </div>
        <button onClick={downloadPDF} disabled={downloading} style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          padding: '7px 14px', fontSize: '12px', fontWeight: 500,
          border: 'none', borderRadius: '6px', background: '#495844',
          color: 'white', cursor: 'pointer', fontFamily: 'inherit',
        }}>
          <i className="ti ti-download" style={{ fontSize: '13px' }} />
          {downloading ? 'Downloading...' : 'Export PDF'}
        </button>
      </div>

      {/* Log list */}
      <div style={{ flex: 1, overflowY: 'auto', background: 'white' }}>
        <div style={{
          display: 'grid', gridTemplateColumns: '160px 180px 200px 1fr',
          gap: '8px', padding: '8px 20px',
          fontSize: '10px', color: '#8B9388',
          letterSpacing: '0.05em', textTransform: 'uppercase',
          borderBottom: '0.5px solid #DDD6C9',
          position: 'sticky', top: 0, background: 'white',
        }}>
          <div>Timestamp</div><div>User</div><div>Action</div><div>Entity</div>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>Loading audit logs...</div>
        ) : logs.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>No audit logs yet</div>
        ) : (
          logs.map((log, i) => (
            <div key={log.id || i} style={{
              display: 'grid', gridTemplateColumns: '160px 180px 200px 1fr',
              gap: '8px', padding: '9px 20px', alignItems: 'center',
              borderBottom: '0.5px solid #F0ECE4',
              fontSize: '11px',
            }}>
              <div style={{ color: '#8B9388', fontFamily: "'DM Mono', monospace", fontSize: '10px' }}>
                {log.timestamp?.slice(0, 16).replace('T', ' ')}
              </div>
              <div style={{ color: '#495844', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {log.user_email || 'system'}
              </div>
              <div>
                <span style={{
                  fontSize: '10px', fontWeight: 500, padding: '2px 6px', borderRadius: '3px',
                  background: '#F6F3EE', color: ACTION_COLOR[log.action] || '#8B9388',
                }}>
                  {log.action?.replace(/_/g, ' ')}
                </span>
              </div>
              <div style={{ color: '#8B9388', fontFamily: "'DM Mono', monospace", fontSize: '10px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {log.entity_type} · {log.entity_id?.slice(0, 16)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}