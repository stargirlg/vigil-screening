interface Alert {
  customer_name: string
  id: string
  customer_id: string
  match_score: number
  risk_level: string
  alert_type: string
  status: string
  params_matched: number
  created_at: string
}

interface AlertListProps {
  alerts: Alert[]
  selected: string | null
  onSelect: (id: string) => void
  filter: string
  onFilter: (f: string) => void
}

const FILTERS = ['ALL', 'SANCTION', 'PEP', 'MEDIA']

const scoreColor = (s: number) =>
  s >= 75 ? '#8B4040' : s >= 50 ? '#7A5C2E' : s >= 30 ? '#73856E' : '#8B9388'

export default function AlertList({ alerts, selected, onSelect, filter, onFilter }: AlertListProps) {
  return (
    <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>

      {/* Filters */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 20px 10px',
        borderBottom: '0.5px solid #DDD6C9',
      }}>
        <div style={{ fontSize: '12px', color: '#8B9388' }}>
          {alerts.length} alerts
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          {FILTERS.map(f => (
            <button key={f} onClick={() => onFilter(f)} style={{
              padding: '3px 10px', borderRadius: '20px', fontSize: '11px',
              cursor: 'pointer', border: '0.5px solid', fontFamily: 'inherit',
              background: filter === f ? '#73856E' : 'none',
              borderColor: filter === f ? '#73856E' : '#DDD6C9',
              color: filter === f ? 'white' : '#8B9388',
              transition: 'all 0.12s',
            }}>
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Column headers */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '24px 1fr 60px 80px 90px 60px',
        gap: '8px', padding: '8px 20px',
        fontSize: '10px', color: '#8B9388',
        letterSpacing: '0.05em', textTransform: 'uppercase',
        borderBottom: '0.5px solid #DDD6C9',
      }}>
        <div>#</div>
        <div>Customer</div>
        <div>Risk</div>
        <div>Score</div>
        <div>Type</div>
        <div>Date</div>
      </div>

      {/* Rows */}
      <div style={{ overflowY: 'auto', flex: 1 }}>
        {alerts.map((a, i) => (
          <div key={a.id}
            onClick={() => onSelect(a.id)}
            style={{
              display: 'grid',
              gridTemplateColumns: '24px 1fr 60px 80px 90px 60px',
              gap: '8px', padding: '10px 20px', alignItems: 'center',
              borderBottom: '0.5px solid #F0ECE4',
              cursor: 'pointer', transition: 'background 0.1s',
              background: selected === a.id ? '#F6F3EE' : 'white',
              borderLeft: selected === a.id ? '2px solid #73856E' : '2px solid transparent',
            }}
            onMouseOver={e => { if (selected !== a.id) e.currentTarget.style.background = '#FAFAF8' }}
            onMouseOut={e  => { if (selected !== a.id) e.currentTarget.style.background = 'white' }}
          >
            <div style={{ fontSize: '10px', color: '#8B9388' }}>{i + 1}</div>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D' }}>
                { a.customer_name ||a.customer_id.slice(0, 8)}…
              </div>
              <div style={{ fontSize: '10px', color: '#8B9388', fontFamily: "'DM Mono', monospace", marginTop: '1px' }}>
                {a.id.slice(0, 10)}…
              </div>
            </div>
            <div>
              <span style={{
                fontSize: '10px', fontWeight: 500, padding: '2px 6px',
                borderRadius: '3px',
                background: a.risk_level === 'CRITICAL' ? '#F5E8E8' :
                            a.risk_level === 'HIGH'     ? '#F5EFE0' :
                            a.risk_level === 'MEDIUM'   ? '#EDF2E8' : '#F0ECE4',
                color: a.risk_level === 'CRITICAL' ? '#8B4040' :
                       a.risk_level === 'HIGH'     ? '#7A5C2E' :
                       a.risk_level === 'MEDIUM'   ? '#495844' : '#8B9388',
              }}>
                {a.risk_level}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <div style={{ flex: 1, height: '3px', background: '#F0ECE4', borderRadius: '2px' }}>
                <div style={{
                  height: '100%', borderRadius: '2px',
                  background: scoreColor(a.match_score),
                  width: `${a.match_score}%`,
                }} />
              </div>
              <span style={{ fontSize: '11px', color: '#495844', fontFamily: "'DM Mono', monospace", minWidth: '20px' }}>
                {a.match_score}
              </span>
            </div>
            <div style={{ fontSize: '10px', color: '#8B9388' }}>
              {a.alert_type?.replace(/_/g, ' ') || '—'}
            </div>
            <div style={{ fontSize: '10px', color: '#8B9388' }}>
              {new Date(a.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}
            </div>
          </div>
        ))}

        {alerts.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>
            No alerts found
          </div>
        )}
      </div>
    </div>
  )
}