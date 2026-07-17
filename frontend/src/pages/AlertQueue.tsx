import { useEffect, useState } from 'react'
import AlertList from '../components/AlertList'
import AlertDetailPanel from '../components/AlertDetailPanel'
import { getAlerts, getAlert, getCustomer } from '../api/client'

export default function AlertQueue() {
  const [alerts, setAlerts]     = useState<any[]>([])
  const [filtered, setFiltered] = useState<any[]>([])
  const [filter, setFilter]     = useState('ALL')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail]     = useState<any>(null)
  const [customer, setCustomer] = useState<any>(null)

  useEffect(() => {
  getAlerts().then(async r => {
    const alertsData = r.data
    // Fetch customer names for all alerts
    const enriched = await Promise.all(
      alertsData.map(async (a: any) => {
        try {
          const cr = await getCustomer(a.customer_id)
          return { ...a, customer_name: cr.data.full_name }
        } catch {
          return a
        }
      })
    )
    setAlerts(enriched)
    setFiltered(enriched)
  }).catch(console.error)
}, [])

  const applyFilter = (f: string) => {
    setFilter(f)
    if (f === 'ALL') { setFiltered(alerts); return }
    const map: Record<string, string[]> = {
      SANCTION: ['FULL_SANCTION_MATCH', 'PARTIAL_MATCH'],
      PEP:      ['PEP_HIT'],
      MEDIA:    ['ADVERSE_MEDIA_HIT'],
    }
    setFiltered(alerts.filter(a => (map[f] || []).includes(a.alert_type)))
  }

const handleSelect = async (id: string) => {
  setSelectedId(id)
  setDetail(null)
  setCustomer(null)
  try {
    const ar = await getAlert(id)
    setDetail(ar.data)
    const cr = await getCustomer(ar.data.customer_id)
    setCustomer(cr.data)
  } catch (e) { console.error(e) }
}
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 48px)', background: 'white' }}>

      {/* Topbar */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 20px', borderBottom: '0.5px solid #DDD6C9',
        background: 'white',
      }}>
        <div>
          <div style={{ fontSize: '14px', fontWeight: 500, color: '#2D2D2D' }}>Alert queue</div>
          <div style={{ fontSize: '11px', color: '#8B9388', marginTop: '1px' }}>
            {alerts.length} total · {alerts.filter(a => a.status === 'PENDING_REVIEW').length} pending review
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={() => window.location.reload()} style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            padding: '6px 12px', border: '0.5px solid #DDD6C9',
            borderRadius: '6px', background: 'none', fontSize: '12px',
            cursor: 'pointer', fontFamily: 'inherit', color: '#495844',
          }}>
            <i className="ti ti-refresh" style={{ fontSize: '13px' }} />
            Refresh
          </button>
<button onClick={async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/export/alerts', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) { alert('Export failed — please login again'); return }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'VIGIL-Alerts.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } catch(e) { console.error(e) }
}} style={{
  display: 'flex', alignItems: 'center', gap: '5px',
  padding: '6px 12px', border: '0.5px solid #73856E',
  borderRadius: '6px', background: '#73856E', fontSize: '12px',
  cursor: 'pointer', fontFamily: 'inherit', color: 'white', fontWeight: 500,
}}>
  <i className="ti ti-download" style={{ fontSize: '13px' }} />
  Export CSV
</button>
        </div>
      </div>

      {/* Split view */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', width: '100%' }}>
        <AlertList
          alerts={filtered}
          selected={selectedId}
          onSelect={handleSelect}
          filter={filter}
          onFilter={applyFilter}
        />

        {/* Detail panel */}
        {detail ? (
          <AlertDetailPanel alert={detail} customer={customer} />
        ) : (
          <div style={{
            width: '320px', flexShrink: 0,
            borderLeft: '0.5px solid #DDD6C9',
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            color: '#8B9388', gap: '8px', fontSize: '13px',
            background: '#FAFAF8',
          }}>
            <i className="ti ti-shield" style={{ fontSize: '32px', color: '#DDD6C9' }} />
            <div>Select an alert to review</div>
            <div style={{ fontSize: '11px' }}>Click any row on the left</div>
          </div>
        )}
      </div>
    </div>
  )
}