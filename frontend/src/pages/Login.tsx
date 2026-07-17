import { useState } from 'react'
import { Shield } from 'lucide-react'
import { login } from '../api/client'

interface LoginProps {
  onLogin?: (token: string) => void
}

export default function Login({ onLogin }: LoginProps) {
  const [email, setEmail]     = useState('admin@vigil.com')
  const [password, setPassword] = useState('Admin@123!')
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    setLoading(true); setError('')
    try {
      const res = await login(email, password)
      localStorage.setItem('token', res.data.access_token)
      localStorage.setItem('email', res.data.user.email)
      localStorage.setItem('role',  res.data.user.role)
      if (onLogin) onLogin(res.data.access_token)
      else window.location.reload()
    } catch { setError('Invalid email or password') }
    finally { setLoading(false) }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: '#F4F1EA',
    }}>
      <div style={{
        background: 'white', border: '0.5px solid #DDD6C9',
        borderRadius: '14px', padding: '40px', width: '100%', maxWidth: '400px',
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '32px' }}>
          <div style={{
            width: '36px', height: '36px', background: '#495844',
            borderRadius: '9px', display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Shield size={18} color="white" />
          </div>
          <div>
            <div style={{ fontSize: '18px', fontWeight: 600, letterSpacing: '0.04em', color: '#2D2D2D' }}>VIGIL</div>
            <div style={{ fontSize: '11px', color: '#8B9388' }}>Compliance Screening Platform</div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ fontSize: '12px', color: '#495844', fontWeight: 500, display: 'block', marginBottom: '6px' }}>
              Email
            </label>
            <input
              type="email" value={email}
              onChange={e => setEmail(e.target.value)}
              style={{
                width: '100%', padding: '9px 12px', fontSize: '13px',
                border: '0.5px solid #DDD6C9', borderRadius: '7px',
                background: '#F6F3EE', color: '#2D2D2D', outline: 'none',
                fontFamily: 'inherit',
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: '#495844', fontWeight: 500, display: 'block', marginBottom: '6px' }}>
              Password
            </label>
            <input
              type="password" value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              style={{
                width: '100%', padding: '9px 12px', fontSize: '13px',
                border: '0.5px solid #DDD6C9', borderRadius: '7px',
                background: '#F6F3EE', color: '#2D2D2D', outline: 'none',
                fontFamily: 'inherit',
              }}
            />
          </div>

          {error && (
            <div style={{
              fontSize: '12px', color: '#8B4040', background: '#F5E8E8',
              border: '0.5px solid #DDD6C9', borderRadius: '6px', padding: '8px 12px'
            }}>
              {error}
            </div>
          )}

          <button
            onClick={handleLogin} disabled={loading}
            style={{
              width: '100%', padding: '10px', fontSize: '13px', fontWeight: 500,
              background: loading ? '#8B9388' : '#495844', color: 'white',
              border: 'none', borderRadius: '7px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontFamily: 'inherit', marginTop: '4px',
              transition: 'background 0.15s',
            }}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </div>

        <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '0.5px solid #DDD6C9' }}>
          <div style={{ fontSize: '10px', color: '#8B9388', textAlign: 'center' }}>
            BFSI Compliant · AML/KYC · RBI Guidelines
          </div>
        </div>
      </div>
    </div>
  )
}