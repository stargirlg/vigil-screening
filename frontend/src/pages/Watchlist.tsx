import { useState } from 'react'
import API from '../api/client'

const STATUS_COLOR: Record<string, { bg: string; color: string }> = {
  FRAUD_CONFIRMED:     { bg: '#F5E8E8', color: '#8B4040' },
  SAR_FILED:           { bg: '#F5EFE0', color: '#7A5C2E' },
  UNDER_INVESTIGATION: { bg: '#EEF2FF', color: '#4338CA' },
  PREVIOUS_ESCALATION: { bg: '#FEFCE8', color: '#854D0E' },
  FALSE_POSITIVE:      { bg: '#EDF2E8', color: '#495844' },
}

export default function Watchlist() {
  const [customerId, setCustomerId] = useState('')
  const [entries, setEntries]       = useState<any[]>([])
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState('')

  const search = async () => {
    if (!customerId.trim()) return
    setLoading(true); setError(''); setEntries([])
    try {
      const r = await API.get(`/watchlist/${customerId.trim()}`)
      setEntries(r.data)
    } catch {
      setError('No watchlist entries found for this customer ID')
    } finally { setLoading(false) }
  }

  return (
    <div style={{ flex: 1, padding: '24px', background: '#F4F1EA', overflowY: 'auto' }}>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '16px', fontWeight: 500, color: '#2D2D2D', marginBottom: '3px' }}>Watchlist</div>
        <div style={{ fontSize: '12px', color: '#8B9388' }}>Internal risk intelligence — historical flags per customer</div>
      </div>

      {/* Search */}
      <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px', marginBottom: '16px' }}>
        <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '10px' }}>Search by customer ID</div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            placeholder="Paste customer UUID..."
            value={customerId}
            onChange={e => setCustomerId(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && search()}
            style={{
              flex: 1, padding: '8px 12px', fontSize: '12px',
              border: '0.5px solid #DDD6C9', borderRadius: '6px',
              background: '#F6F3EE', color: '#2D2D2D', outline: 'none',
              fontFamily: "'DM Mono', monospace",
            }}
          />
          <button onClick={search} style={{
            padding: '8px 16px', fontSize: '12px', fontWeight: 500,
            border: 'none', borderRadius: '6px', background: '#73856E',
            color: 'white', cursor: 'pointer', fontFamily: 'inherit',
          }}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        <div style={{ fontSize: '11px', color: '#8B9388', marginTop: '8px' }}>
          Try Raza Khan: e506847c-ea3b-4630-b229-fd5c85f10535
        </div>
      </div>

      {error && (
        <div style={{ background: '#F5E8E8', border: '0.5px solid #DDD6C9', borderRadius: '8px', padding: '12px 16px', color: '#8B4040', fontSize: '13px', marginBottom: '16px' }}>
          {error}
        </div>
      )}

      {entries.length > 0 && (
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: '0.5px solid #DDD6C9', fontSize: '12px', fontWeight: 500, color: '#2D2D2D' }}>
            {entries.length} watchlist entries found
          </div>
          {entries.map(e => {
            const s = STATUS_COLOR[e.status] || { bg: '#F6F3EE', color: '#8B9388' }
            return (
              <div key={e.id} style={{ padding: '14px 16px', borderBottom: '0.5px solid #F0ECE4' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 500, padding: '3px 8px', borderRadius: '4px', background: s.bg, color: s.color }}>
                    {e.status.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: '10px', color: '#8B9388' }}>{e.added_at?.slice(0, 10)}</span>
                </div>
                <div style={{ fontSize: '12px', color: '#2D2D2D', marginBottom: '4px' }}>{e.reason}</div>
                <div style={{ fontSize: '11px', color: '#8B9388' }}>
                  Added by: {e.added_by_email}
                  {e.case_reference && ` · Case: ${e.case_reference}`}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}