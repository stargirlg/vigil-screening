export default function Settings() {
  const email = localStorage.getItem('email')
  const role  = localStorage.getItem('role')

  return (
    <div style={{ flex: 1, padding: '24px', background: '#F4F1EA', overflowY: 'auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '16px', fontWeight: 500, color: '#2D2D2D' }}>Settings</div>
        <div style={{ fontSize: '12px', color: '#8B9388', marginTop: '2px' }}>System configuration</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '12px' }}>Current session</div>
          {[
            { label: 'Email',     value: email },
            { label: 'Role',      value: role },
            { label: 'Platform',  value: 'VIGIL v1.0' },
            { label: 'DB',        value: 'PostgreSQL 16' },
            { label: 'Backend',   value: 'FastAPI 0.111' },
            { label: 'Frontend',  value: 'React + TypeScript' },
          ].map(f => (
            <div key={f.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '0.5px solid #F0ECE4', fontSize: '12px' }}>
              <span style={{ color: '#8B9388' }}>{f.label}</span>
              <span style={{ color: '#2D2D2D', fontWeight: 500 }}>{f.value}</span>
            </div>
          ))}
        </div>

        <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '12px' }}>System info</div>
          {[
            { label: 'Rule version',   value: '1.0' },
            { label: 'Screening params', value: '7 parameters' },
            { label: 'Risk levels',    value: 'LOW / MEDIUM / HIGH / CRITICAL' },
            { label: 'SLA — Medium',   value: '48 hours' },
            { label: 'SLA — High',     value: '24 hours' },
            { label: 'SLA — Critical', value: '4 hours' },
            { label: 'Fuzzy threshold', value: '85%' },
          ].map(f => (
            <div key={f.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '0.5px solid #F0ECE4', fontSize: '12px' }}>
              <span style={{ color: '#8B9388' }}>{f.label}</span>
              <span style={{ color: '#2D2D2D', fontWeight: 500, fontSize: '11px' }}>{f.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}