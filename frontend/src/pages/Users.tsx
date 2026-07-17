import { useEffect, useState } from 'react'
import API from '../api/client'

const ROLE_COLOR: Record<string, { bg: string; color: string }> = {
  ADMIN:   { bg: '#EDF2E8', color: '#495844' },
  ANALYST: { bg: '#EEF2FF', color: '#4338CA' },
  CO:      { bg: '#F5EFE0', color: '#7A5C2E' },
}

export default function Users() {
  const [users, setUsers]   = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    API.get('/users').then(r => {
      setUsers(r.data)
      setLoading(false)
    }).catch(e => {
      console.error(e)
      setLoading(false)
    })
  }, [])

  return (
    <div style={{ flex: 1, padding: '24px', background: '#F4F1EA', overflowY: 'auto' }}>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '16px', fontWeight: 500, color: '#2D2D2D' }}>Users</div>
        <div style={{ fontSize: '12px', color: '#8B9388', marginTop: '2px' }}>
          System users and role assignments
        </div>
      </div>

      <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', overflow: 'hidden' }}>
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 200px 100px 80px 160px',
          gap: '8px', padding: '8px 16px',
          fontSize: '10px', color: '#8B9388',
          letterSpacing: '0.05em', textTransform: 'uppercase',
          borderBottom: '0.5px solid #DDD6C9',
        }}>
          <div>Name</div><div>Email</div><div>Role</div><div>Active</div><div>Created</div>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>Loading users...</div>
        ) : users.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#8B9388', fontSize: '13px' }}>No users found</div>
        ) : (
          users.map(u => {
            const r = ROLE_COLOR[u.role] || { bg: '#F6F3EE', color: '#8B9388' }
            return (
              <div key={u.id} style={{
                display: 'grid', gridTemplateColumns: '1fr 200px 100px 80px 160px',
                gap: '8px', padding: '10px 16px', alignItems: 'center',
                borderBottom: '0.5px solid #F0ECE4', fontSize: '12px',
              }}>
                <div style={{ fontWeight: 500, color: '#2D2D2D' }}>{u.full_name || '—'}</div>
                <div style={{ color: '#4A5568', fontSize: '11px' }}>{u.email}</div>
                <div>
                  <span style={{ fontSize: '10px', fontWeight: 500, padding: '2px 6px', borderRadius: '3px', background: r.bg, color: r.color }}>
                    {u.role}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: u.is_active ? '#495844' : '#8B4040' }}>
                  {u.is_active ? '✓ Active' : '✗ Inactive'}
                </div>
                <div style={{ fontSize: '10px', color: '#8B9388', fontFamily: "'DM Mono', monospace" }}>
                  {u.created_at?.slice(0, 10)}
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Credentials reference */}
      <div style={{ background: 'white', border: '0.5px solid #DDD6C9', borderRadius: '10px', padding: '16px', marginTop: '16px' }}>
        <div style={{ fontSize: '12px', fontWeight: 500, color: '#2D2D2D', marginBottom: '10px' }}>Login credentials</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {[
            { email: 'admin@vigil.com',    password: 'Admin@123!',   role: 'ADMIN' },
            { email: 'analyst@vigil.com',  password: 'Analyst@123!', role: 'ANALYST' },
            { email: 'co@vigil.com',       password: 'CO@123456!',   role: 'CO' },
            { email: 'checker@vigil.com',  password: 'Checker@123!', role: 'ANALYST' },
          ].map(u => {
            const r = ROLE_COLOR[u.role] || { bg: '#F6F3EE', color: '#8B9388' }
            return (
              <div key={u.email} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '7px 10px', background: '#F6F3EE', borderRadius: '6px', fontSize: '11px' }}>
                <span style={{ fontSize: '10px', fontWeight: 500, padding: '2px 6px', borderRadius: '3px', background: r.bg, color: r.color }}>{u.role}</span>
                <span style={{ color: '#495844', fontFamily: "'DM Mono', monospace" }}>{u.email}</span>
                <span style={{ color: '#8B9388', fontFamily: "'DM Mono', monospace" }}>{u.password}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}