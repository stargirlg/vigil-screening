import { useEffect, useState } from 'react'
import API from '../api/client'

export default function Customers() {
  const [customers, setCustomers] = useState<any[]>([])
  const [search, setSearch]       = useState('')
  const [loading, setLoading]     = useState(true)
  const [selected, setSelected]   = useState<any>(null)

  useEffect(() => {
    API.get('/customers').then(r => {
      setCustomers(r.data)
      setLoading(false)
    }).catch(console.error)
  }, [])

  const filtered = customers.filter(c =>
    c.full_name?.toLowerCase().includes(search.toLowerCase()) ||
    c.pan?.toLowerCase().includes(search.toLowerCase()) ||
    c.nationality?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#F4F1EA', height: 'calc(100vh - 48px)' }}>

      {/* Header */}
      <div style={{ padding: '16px 20px', borderBottom: '0.5px solid #DDD6C9', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 500, color: '#2D2D2D' }}>Customers</div>
          <div style={{ fontSize: '11px', color: '#8B9388', marginTop: '1px' }}>{customers.length} total customers in system</div>
        </div>
        <input
          placeholder="Search by name, PAN, nationality..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            padding: '7px 12px', fontSize: '12px', width: '280px',
            border: '0.5px solid #DDD6C9', borderRadius: '6px',
            background: '#F6F3EE', color: '#2D2D2D', outline: 'none',
            fontFamily: 'inherit',
          }}
        />
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* Customer list */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {/* Column headers */}
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 100px 120px 120px 80px',
            gap: '8px', padding: '8px 20px',
            fontSize: '10px', color: '#8B9388',
            letterSpacing: '0.05em', textTransform: 'uppercase',
            borderBottom: '0.5px solid #DDD6C9', background: 'white',
          }}>
            <div>Name</div><div>PAN</div><div>Nationality</div><div>Occupation</div><div>Source</div>
          </div>

          {loading ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>Loading customers...</div>
          ) : filtered.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>No customers found</div>
          ) : (
            filtered.map((c, ) => (
              <div key={c.id}
                onClick={() => setSelected(c)}
                style={{
                  display: 'grid', gridTemplateColumns: '1fr 100px 120px 120px 80px',
                  gap: '8px', padding: '10px 20px', alignItems: 'center',
                  borderBottom: '0.5px solid #F0ECE4', cursor: 'pointer',
                  background: selected?.id === c.id ? '#F6F3EE' : 'white',
                  borderLeft: selected?.id === c.id ? '2px solid #73856E' : '2px solid transparent',
                  transition: 'background 0.1s',
                }}
                onMouseOver={e => { if (selected?.id !== c.id) e.currentTarget.style.background = '#FAFAF8' }}
                onMouseOut={e  => { if (selected?.id !== c.id) e.currentTarget.style.background = 'white' }}
              >
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 500, color: '#2D2D2D' }}>{c.full_name}</div>
                  <div style={{ fontSize: '10px', color: '#8B9388', fontFamily: "'DM Mono', monospace", marginTop: '1px' }}>{c.id.slice(0, 16)}…</div>
                </div>
                <div style={{ fontSize: '11px', color: '#495844', fontFamily: "'DM Mono', monospace" }}>{c.pan || '—'}</div>
                <div style={{ fontSize: '11px', color: '#4A5568' }}>{c.nationality || '—'}</div>
                <div style={{ fontSize: '11px', color: '#4A5568' }}>{c.occupation || '—'}</div>
                <div style={{ fontSize: '10px', color: '#8B9388' }}>{c.source || '—'}</div>
              </div>
            ))
          )}
        </div>

        {/* Detail panel */}
        {selected ? (
          <div style={{ width: '280px', flexShrink: 0, borderLeft: '0.5px solid #DDD6C9', background: '#FAFAF8', padding: '16px', overflowY: 'auto' }}>
            <div style={{ fontSize: '14px', fontWeight: 500, color: '#2D2D2D', marginBottom: '4px' }}>{selected.full_name}</div>
            <div style={{ fontSize: '10px', color: '#8B9388', fontFamily: "'DM Mono', monospace', marginBottom: '14px'" }}>{selected.id}</div>

            <div style={{ fontSize: '10px', color: '#8B9388', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '8px', marginTop: '14px' }}>Identity</div>
            {[
              { label: 'PAN',      value: selected.pan },
              { label: 'Aadhaar',  value: selected.aadhaar },
              { label: 'Passport', value: selected.passport },
              { label: 'DIN',      value: selected.din },
              { label: 'UIN',      value: selected.uin },
            ].map(f => f.value && (
              <div key={f.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '0.5px solid #F0ECE4', fontSize: '12px' }}>
                <span style={{ color: '#8B9388' }}>{f.label}</span>
                <span style={{ color: '#2D2D2D', fontFamily: "'DM Mono', monospace", fontWeight: 500 }}>{f.value}</span>
              </div>
            ))}

            <div style={{ fontSize: '10px', color: '#8B9388', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '8px', marginTop: '14px' }}>Profile</div>
            {[
              { label: 'DOB',         value: selected.dob },
              { label: 'Nationality', value: selected.nationality },
              { label: 'Occupation',  value: selected.occupation },
              { label: 'Email',       value: selected.email },
              { label: 'Phone',       value: selected.phone },
              { label: 'Source',      value: selected.source },
            ].map(f => f.value && (
              <div key={f.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '0.5px solid #F0ECE4', fontSize: '12px' }}>
                <span style={{ color: '#8B9388' }}>{f.label}</span>
                <span style={{ color: '#2D2D2D', fontWeight: 500 }}>{f.value}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ width: '280px', flexShrink: 0, borderLeft: '0.5px solid #DDD6C9', background: '#FAFAF8', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#8B9388', gap: '8px' }}>
            <i className="ti ti-user" style={{ fontSize: '32px', color: '#DDD6C9' }} />
            <div style={{ fontSize: '13px' }}>Select a customer</div>
          </div>
        )}
      </div>
    </div>
  )
}