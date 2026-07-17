import { useEffect, useState } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import AlertQueue from './pages/AlertQueue'
import Cases from './pages/Cases'
import Customers from './pages/Customers'
import Watchlist from './pages/Watchlist'
import Analytics from './pages/Analytics'
import Audit from './pages/Audit'
import Rules from './pages/Rules'
import Users from './pages/Users'
import Settings from './pages/Settings'
import AnalystDashboard from './pages/AnalystDashboard'
import CODashboard from './pages/CODashboard'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import { getDashboardStats } from './api/client'
import CheckerDashboard from './pages/CheckerDashboard'

function App() {
  const [token, setToken]     = useState<string | null>(null)
  const [checked, setChecked] = useState(false)
  const [page, setPage]       = useState('dashboard')
  const [pending, setPending] = useState(0)
  const role = localStorage.getItem('role') || 'ANALYST'

  useEffect(() => {
    const t = localStorage.getItem('token')
    if (t) {
      fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${t}` }
      }).then(r => {
        if (r.ok) {
          setToken(t)
          const r2 = localStorage.getItem('role') || 'ANALYST'
          if (r2 === 'ANALYST') setPage('analyst')
          else if (r2 === 'CO') setPage('co_dashboard')
          else if (r2 === 'CHECKER') setPage('checker')
          else setPage('dashboard')
        } else {
          localStorage.clear()
          setToken(null)
        }
        setChecked(true)
      }).catch(() => {
        localStorage.clear()
        setToken(null)
        setChecked(true)
      })
    } else {
      setChecked(true)
    }
  }, [])

  useEffect(() => {
    if (token) {
      getDashboardStats()
        .then(r => setPending(r.data.alert_breakdown.pending_review))
        .catch(console.error)
    }
  }, [token])

  if (!checked) return null
  if (!token) return <Login onLogin={(t) => { setToken(t); window.location.reload() }} />

  const renderPage = () => {
    switch (page) {
      case 'alerts':       return <AlertQueue />
      case 'cases':        return <Cases />
      case 'customers':    return <Customers />
      case 'watchlist':    return <Watchlist />
      case 'analytics':    return <Analytics />
      case 'audit':        return <Audit />
      case 'rules':        return <Rules />
      case 'users':        return <Users />
      case 'settings':     return <Settings />
      case 'co_dashboard': return <CODashboard />
      case 'analyst':      return <AnalystDashboard />
      case 'approvals':    return <CODashboard />
      case 'sar':          return <CODashboard />
      case 'checker':      return <CheckerDashboard />
      default:             return <Dashboard />
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#F4F1EA' }}>
      <Navbar />
      <div style={{ display: 'flex', width: '100%', overflow: 'hidden' }}>
        <Sidebar active={page} onChange={setPage} pendingAlerts={pending} role={role} />
        <div style={{ flex: 1, overflow: 'hidden', minWidth: 0 }}>
          {renderPage()}
        </div>
      </div>
    </div>
  )
}

export default App