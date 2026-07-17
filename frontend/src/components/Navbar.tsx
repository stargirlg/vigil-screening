import { Shield, Bell } from 'lucide-react'

export default function Navbar() {
  const email = localStorage.getItem('email') || 'user'
  const role  = localStorage.getItem('role') || 'ADMIN'

  const logout = () => { localStorage.clear(); window.location.reload() }

  return (
    <nav style={{
      height: '48px', background: 'white',
      borderBottom: '0.5px solid #DDD6C9',
      display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', padding: '0 20px',
      position: 'sticky', top: 0, zIndex: 50,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ width: '24px', height: '24px', background: '#495844', borderRadius: '5px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Shield size={13} color="white" />
        </div>
        <span style={{ fontSize: '14px', fontWeight: 600, letterSpacing: '0.06em', color: '#2D2D2D' }}>VIGIL</span>
        <span style={{ fontSize: '11px', color: '#8B9388', marginLeft: '4px' }}>Compliance</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Bell size={15} color="#8B9388" style={{ cursor: 'pointer' }} />
        <span style={{ fontSize: '12px', color: '#495844' }}>{email}</span>
        <span style={{
          fontSize: '10px', fontWeight: 500, padding: '2px 7px',
          borderRadius: '4px', background: '#EDF2E8',
          color: '#495844', border: '0.5px solid #DDD6C9',
        }}>
          {role}
        </span>
        <button onClick={logout} style={{
          fontSize: '12px', color: '#8B9388', background: 'none',
          border: 'none', cursor: 'pointer', padding: '4px 8px',
          borderRadius: '5px', fontFamily: 'inherit',
        }}
          onMouseOver={e => (e.currentTarget.style.color = '#8B4040')}
          onMouseOut={e  => (e.currentTarget.style.color = '#8B9388')}
        >
          Logout
        </button>
      </div>
    </nav>
  )
}