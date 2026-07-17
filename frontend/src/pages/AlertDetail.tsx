import { useEffect, useState } from 'react'
import { ArrowLeft, User, Calendar, CreditCard, Globe, Briefcase, Newspaper, Shield } from 'lucide-react'
import Navbar from '../components/Navbar'
import RiskBadge from '../components/RiskBadge'
import { getAlert, getCustomer, reviewAlert } from '../api/client'

const PARAM_ICONS: Record<string, any> = {
  name:          { icon: User,      label: 'Name Match' },
  dob:           { icon: Calendar,  label: 'Date of Birth' },
  id_check:      { icon: CreditCard,label: 'ID Match' },
  nationality:   { icon: Globe,     label: 'Nationality' },
  occupation:    { icon: Briefcase, label: 'Occupation' },
  adverse_media: { icon: Newspaper, label: 'Adverse Media' },
  pep:           { icon: Shield,    label: 'PEP Check' },
}

export default function AlertDetail({ alertId, onBack }: { alertId: string; onBack: () => void }) {
  const [alert, setAlert]       = useState<any>(null)
  const [customer, setCustomer] = useState<any>(null)
  const [action, setAction]     = useState('')
  const [notes, setNotes]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [done, setDone]         = useState(false)

  useEffect(() => {
    getAlert(alertId).then(r => {
      setAlert(r.data)
      getCustomer(r.data.customer_id).then(cr => setCustomer(cr.data)).catch(console.error)
    }).catch(console.error)
  }, [alertId])

  const handleReview = async () => {
    if (!action || !notes) return
    setLoading(true)
    try {
      await reviewAlert(alertId, action, notes)
      setDone(true)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  if (!alert) return (
    <div style={{ minHeight: '100vh', background: '#F8F9FB' }}>
      <Navbar />
      <div style={{ padding: '40px', textAlign: 'center', color: '#8D99AE', fontSize: '13px' }}>Loading alert...</div>
    </div>
  )

  const details = alert.match_details || {}

  return (
    <div style={{ minHeight: '100vh', background: '#F8F9FB' }}>
      <Navbar />
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '24px' }}>

        {/* Back button */}
        <button onClick={onBack} style={{
          display: 'flex', alignItems: 'center', gap: '6px',
          fontSize: '12px', color: '#4A5568', background: 'none',
          border: 'none', cursor: 'pointer', marginBottom: '20px', padding: 0,
        }}>
          <ArrowLeft size={14} /> Back to Dashboard
        </button>

        {/* Header */}
        <div style={{
          background: 'white', border: '0.5px solid #E8ECF2',
          borderRadius: '10px', padding: '20px', marginBottom: '16px',
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
        }}>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '4px' }}>
              {customer?.full_name || 'Loading...'}
            </div>
            <div style={{ fontSize: '11px', color: '#8D99AE', fontFamily: "'DM Mono', monospace" }}>
              {alert.customer_id}
            </div>
            <div style={{ marginTop: '10px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <RiskBadge level={alert.risk_level} />
              <span style={{
                fontSize: '10px', fontWeight: 500, padding: '2px 7px',
                borderRadius: '4px', background: '#EEF2FF', color: '#4338CA',
                border: '0.5px solid #C7D2FE',
              }}>
                {alert.alert_type || 'UNKNOWN'}
              </span>
              <span style={{
                fontSize: '10px', fontWeight: 500, padding: '2px 7px',
                borderRadius: '4px', background: '#F8F9FB', color: '#4A5568',
                border: '0.5px solid #E8ECF2',
              }}>
                {alert.status?.replace(/_/g, ' ')}
              </span>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '36px', fontWeight: 600, fontFamily: "'DM Mono', monospace", color: alert.risk_level === 'CRITICAL' ? '#DC2626' : alert.risk_level === 'HIGH' ? '#EA580C' : '#1A4FB3' }}>
              {alert.match_score}
            </div>
            <div style={{ fontSize: '11px', color: '#8D99AE' }}>/ 100 score</div>
            <div style={{ fontSize: '11px', color: '#8D99AE', marginTop: '4px' }}>
              {alert.params_matched} params matched
            </div>
          </div>
        </div>

        {/* Customer info */}
        {customer && (
          <div style={{
            background: 'white', border: '0.5px solid #E8ECF2',
            borderRadius: '10px', padding: '16px', marginBottom: '16px',
          }}>
            <div style={{ fontSize: '12px', fontWeight: 500, marginBottom: '12px', color: '#1A202C' }}>Customer details</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
              {[
                { label: 'Full name',    value: customer.full_name },
                { label: 'DOB',          value: customer.dob || '—' },
                { label: 'PAN',          value: customer.pan || '—' },
                { label: 'Nationality',  value: customer.nationality || '—' },
                { label: 'Occupation',   value: customer.occupation || '—' },
                { label: 'Source',       value: customer.source },
              ].map(f => (
                <div key={f.label}>
                  <div style={{ fontSize: '10px', color: '#8D99AE', marginBottom: '2px' }}>{f.label}</div>
                  <div style={{ fontSize: '12px', fontWeight: 500, color: '#1A202C' }}>{f.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 7 Parameter breakdown */}
        <div style={{
          background: 'white', border: '0.5px solid #E8ECF2',
          borderRadius: '10px', padding: '16px', marginBottom: '16px',
        }}>
          <div style={{ fontSize: '12px', fontWeight: 500, marginBottom: '12px', color: '#1A202C' }}>
            Screening parameters
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(PARAM_ICONS).map(([key, meta]) => {
              const param = details[key] || {}
              const matched = param.matched || false
              const Icon = meta.icon
              return (
                <div key={key} style={{
                  display: 'flex', alignItems: 'center', gap: '12px',
                  padding: '10px 12px', borderRadius: '8px',
                  background: matched ? (key === 'name' || key === 'dob' ? '#FEF2F2' : '#FFF7ED') : '#F8F9FB',
                  border: `0.5px solid ${matched ? '#FECACA' : '#E8ECF2'}`,
                }}>
                  <div style={{
                    width: '28px', height: '28px', borderRadius: '6px', flexShrink: 0,
                    background: matched ? '#DC2626' : '#E8ECF2',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Icon size={13} color={matched ? 'white' : '#8D99AE'} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '12px', fontWeight: 500, color: '#1A202C' }}>{meta.label}</div>
                    {param.detail && (
                      <div style={{ fontSize: '11px', color: '#4A5568', marginTop: '1px' }}>{param.detail}</div>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {param.score > 0 && (
                      <span style={{ fontSize: '11px', fontFamily: "'DM Mono', monospace", color: '#4A5568' }}>
                        {param.score}/100
                      </span>
                    )}
                    <span style={{
                      fontSize: '10px', fontWeight: 500, padding: '2px 7px', borderRadius: '4px',
                      background: matched ? '#FEF2F2' : '#F0FDF4',
                      color: matched ? '#DC2626' : '#16A34A',
                      border: `0.5px solid ${matched ? '#FECACA' : '#BBF7D0'}`,
                    }}>
                      {matched ? 'MATCH' : 'CLEAR'}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Review panel */}
        {!done ? (
          <div style={{
            background: 'white', border: '0.5px solid #E8ECF2',
            borderRadius: '10px', padding: '16px',
          }}>
            <div style={{ fontSize: '12px', fontWeight: 500, marginBottom: '12px', color: '#1A202C' }}>
              Review decision
            </div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
              {['CLEAR', 'CONFIRM', 'ESCALATE', 'REJECT'].map(a => (
                <button key={a} onClick={() => setAction(a)} style={{
                  padding: '7px 14px', fontSize: '12px', fontWeight: 500,
                  borderRadius: '7px', cursor: 'pointer', fontFamily: 'inherit',
                  border: '0.5px solid',
                  background: action === a ? (a === 'CONFIRM' ? '#FEF2F2' : a === 'CLEAR' ? '#F0FDF4' : a === 'ESCALATE' ? '#FFF7ED' : '#F8F9FB') : 'white',
                  color: action === a ? (a === 'CONFIRM' ? '#DC2626' : a === 'CLEAR' ? '#16A34A' : a === 'ESCALATE' ? '#EA580C' : '#4A5568') : '#4A5568',
                  borderColor: action === a ? (a === 'CONFIRM' ? '#FECACA' : a === 'CLEAR' ? '#BBF7D0' : a === 'ESCALATE' ? '#FED7AA' : '#E8ECF2') : '#E8ECF2',
                }}>
                  {a}
                </button>
              ))}
            </div>
            <textarea
              placeholder="Add review notes..."
              value={notes}
              onChange={e => setNotes(e.target.value)}
              style={{
                width: '100%', padding: '10px 12px', fontSize: '12px',
                border: '0.5px solid #CDD3DE', borderRadius: '7px',
                background: '#F8F9FB', color: '#1A202C', outline: 'none',
                fontFamily: 'inherit', resize: 'vertical', minHeight: '80px',
                marginBottom: '12px',
              }}
            />
            <button
              onClick={handleReview}
              disabled={!action || !notes || loading}
              style={{
                padding: '9px 20px', fontSize: '12px', fontWeight: 500,
                background: (!action || !notes) ? '#E8ECF2' : '#1A4FB3',
                color: (!action || !notes) ? '#8D99AE' : 'white',
                border: 'none', borderRadius: '7px', cursor: (!action || !notes) ? 'not-allowed' : 'pointer',
                fontFamily: 'inherit',
              }}
            >
              {loading ? 'Submitting...' : 'Submit review'}
            </button>
          </div>
        ) : (
          <div style={{
            background: '#F0FDF4', border: '0.5px solid #BBF7D0',
            borderRadius: '10px', padding: '16px', textAlign: 'center',
          }}>
            <div style={{ fontSize: '13px', fontWeight: 500, color: '#16A34A', marginBottom: '4px' }}>
              ✓ Review submitted successfully
            </div>
            <div style={{ fontSize: '12px', color: '#4A5568' }}>
              Action: {action} · Case logged in audit trail
            </div>
          </div>
        )}
      </div>
    </div>
  )
}