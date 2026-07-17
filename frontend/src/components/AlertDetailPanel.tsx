import { useState, useEffect } from 'react'
import { reviewAlert } from '../api/client'
import API from '../api/client'

const PARAMS = [
  { key: 'name',          label: 'Name match',    weight: 25 },
  { key: 'dob',           label: 'Date of birth', weight: 15 },
  { key: 'id_check',      label: 'ID document',   weight: 20 },
  { key: 'nationality',   label: 'Nationality',   weight: 10 },
  { key: 'occupation',    label: 'Occupation',    weight: 5  },
  { key: 'adverse_media', label: 'Adverse media', weight: 10 },
  { key: 'pep',           label: 'PEP status',    weight: 15 },
]

interface Props {
  alert: any
  customer: any
}

export default function AlertDetailPanel({ alert, customer }: Props) {
  const [action, setAction]   = useState('')
  const [notes, setNotes]     = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone]       = useState(false)
  const [auditLogs, setAuditLogs] = useState<any[]>([])

  useEffect(() => {
    // Fetch audit logs for this alert
    API.get('/audit').then(r => {
      const filtered = r.data.filter((l: any) =>
        l.entity_id === alert.id || l.entity_id === alert.customer_id
      ).slice(0, 8)
      setAuditLogs(filtered)
    }).catch(console.error)
  }, [alert.id])

  const handleReview = async () => {
    if (!action || !notes) return
    setLoading(true)
    try {
      await reviewAlert(alert.id, action, notes)
      setDone(true)
    } catch (e) { console.error(e) }
    finally { setLoading(false) }
  }

  const scoreColor = alert.match_score >= 75 ? '#8B4040' :
                     alert.match_score >= 50 ? '#7A5C2E' :
                     alert.match_score >= 30 ? '#73856E' : '#8B9388'

  const STATUS_STYLE: Record<string, { bg: string; color: string }> = {
    PENDING_REVIEW:  { bg: '#EEF2FF', color: '#4338CA' },
    AUTO_CLOSED:     { bg: '#EDF2E8', color: '#495844' },
    CONFIRMED_MATCH: { bg: '#F5E8E8', color: '#8B4040' },
    ESCALATED:       { bg: '#F5EFE0', color: '#7A5C2E' },
    CLEARED:         { bg: '#F6F3EE', color: '#8B9388' },
  }
  const statusStyle = STATUS_STYLE[alert.status] || STATUS_STYLE.CLEARED

  return (
    <div style={{
      width: '320px', flexShrink: 0,
      borderLeft: '0.5px solid #DDD6C9',
      overflowY: 'auto', padding: '16px',
      background: '#FAFAF8',
      display: 'flex', flexDirection: 'column', gap: '14px',
    }}>

      {/* Customer + Score header */}
      <div style={{ paddingBottom: '14px', borderBottom: '0.5px solid #DDD6C9' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            {/* CUSTOMER NAME — not UUID */}
            <div style={{ fontSize: '15px', fontWeight: 600, color: '#2D2D2D' }}>
              {customer?.full_name || 'Loading...'}
            </div>
            <div style={{ fontSize: '10px', color: '#8B9388', fontFamily: "'DM Mono', monospace", marginTop: '2px' }}>
              {alert.customer_id?.slice(0, 12)}…
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '28px', fontWeight: 600, color: scoreColor, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
              {alert.match_score}
            </div>
            <div style={{ fontSize: '10px', color: '#8B9388' }}>/100</div>
          </div>
        </div>

        {/* Risk + Status badges */}
        <div style={{ display: 'flex', gap: '6px', marginTop: '10px', flexWrap: 'wrap' }}>
          <span style={{
            fontSize: '10px', fontWeight: 600, padding: '3px 8px', borderRadius: '4px',
            background: alert.risk_level === 'CRITICAL' ? '#F5E8E8' :
                        alert.risk_level === 'HIGH'     ? '#F5EFE0' :
                        alert.risk_level === 'MEDIUM'   ? '#FEFCE8' : '#EDF2E8',
            color: alert.risk_level === 'CRITICAL' ? '#8B4040' :
                   alert.risk_level === 'HIGH'     ? '#7A5C2E' :
                   alert.risk_level === 'MEDIUM'   ? '#854D0E' : '#495844',
            letterSpacing: '0.04em',
          }}>
            {alert.risk_level}
          </span>
          <span style={{
            fontSize: '10px', fontWeight: 500, padding: '3px 8px', borderRadius: '4px',
            background: statusStyle.bg, color: statusStyle.color,
          }}>
            {alert.status?.replace(/_/g, ' ')}
          </span>
        </div>
      </div>

      {/* Alert details section */}
      <div>
        <div style={{ fontSize: '10px', color: '#8B9388', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '8px' }}>
          Alert details
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          {[
            { label: 'Alert type',   value: alert.alert_type?.replace(/_/g, ' ') || '—' },
            { label: 'Source list',  value: 'OFAC SDN / Local' },
            { label: 'Created',      value: alert.created_at?.slice(0, 10) || '—' },
            { label: 'Params hit',   value: `${alert.params_matched} of 7` },
            { label: 'Rule version', value: '1.0' },
          ].map(f => (
            <div key={f.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '0.5px solid #F0ECE4', fontSize: '11px' }}>
              <span style={{ color: '#8B9388' }}>{f.label}</span>
              <span style={{ color: '#2D2D2D', fontWeight: 500 }}>{f.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Customer profile */}
      <div>
        <div style={{ fontSize: '10px', color: '#8B9388', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '8px' }}>
          Customer profile
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          {[
            { label: 'PAN',         value: customer?.pan },
            { label: 'DOB',         value: customer?.dob },
            { label: 'Nationality', value: customer?.nationality },
            { label: 'Occupation',  value: customer?.occupation },
          ].filter(f => f.value).map(f => (
            <div key={f.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '0.5px solid #F0ECE4', fontSize: '11px' }}>
              <span style={{ color: '#8B9388' }}>{f.label}</span>
              <span style={{ color: '#2D2D2D', fontWeight: 500 }}>{f.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Parameter breakdown */}
      <div>
        <div style={{ fontSize: '10px', color: '#8B9388', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '8px' }}>
          Parameters
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {PARAMS.map(p => {
            const hit = alert.matched_params?.includes(p.key) || false
            return (
              <div key={p.key} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '5px 8px', borderRadius: '5px',
                background: hit ? '#EDF2E8' : '#F6F3EE',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: hit ? '#495844' : '#8B9388' }}>
                  <i className={`ti ${hit ? 'ti-circle-check' : 'ti-circle-x'}`} style={{ fontSize: '13px' }} />
                  {p.label}
                </div>
                <span style={{
                  fontSize: '10px', padding: '1px 5px', borderRadius: '3px',
                  background: hit ? '#D4E3CC' : '#DDD6C9',
                  color: hit ? '#495844' : '#8B9388',
                }}>
                  {hit ? `+${p.weight}` : p.weight}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Audit timeline */}
      <div>
        <div style={{ fontSize: '10px', color: '#8B9388', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '8px' }}>
          Timeline
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {/* Static timeline entries based on alert state */}
          {[
            { time: alert.created_at?.slice(11, 16), label: 'Alert created', done: true },
            { time: alert.created_at?.slice(11, 16), label: 'Screening completed', done: true },
            { time: alert.status !== 'AUTO_CLOSED' ? '—' : null, label: 'Assigned to analyst', done: alert.assigned_to != null },
            { time: null, label: 'Review started', done: alert.status === 'CONFIRMED_MATCH' || alert.status === 'CLEARED' || alert.status === 'ESCALATED' },
            { time: null, label: 'Decision made', done: alert.status === 'CONFIRMED_MATCH' || alert.status === 'CLEARED' },
          ].filter(t => t.time !== null || t.done).map((t, i) => (
            <div key={i} style={{ display: 'flex', gap: '10px', paddingBottom: '10px', position: 'relative' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{
                  width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0, marginTop: '3px',
                  background: t.done ? '#73856E' : '#DDD6C9',
                }} />
                {i < 4 && <div style={{ width: '1px', flex: 1, background: '#DDD6C9', marginTop: '2px' }} />}
              </div>
              <div style={{ flex: 1, paddingBottom: '4px' }}>
                <div style={{ fontSize: '11px', color: t.done ? '#2D2D2D' : '#8B9388', fontWeight: t.done ? 500 : 400 }}>
                  {t.label}
                </div>
                {t.time && (
                  <div style={{ fontSize: '10px', color: '#8B9388', fontFamily: "'DM Mono', monospace" }}>{t.time}</div>
                )}
              </div>
            </div>
          ))}

          {/* Real audit logs */}
          {auditLogs.map((log, i) => (
            <div key={i} style={{ display: 'flex', gap: '10px', paddingBottom: '8px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0, marginTop: '3px', background: '#73856E' }} />
              <div>
                <div style={{ fontSize: '11px', color: '#2D2D2D', fontWeight: 500 }}>
                  {log.action?.replace(/_/g, ' ')}
                </div>
                <div style={{ fontSize: '10px', color: '#8B9388' }}>
                  {log.user_email} · {log.timestamp?.slice(11, 16)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Review actions */}
      {!done ? (
        <div style={{ borderTop: '0.5px solid #DDD6C9', paddingTop: '14px' }}>
          <div style={{ fontSize: '10px', color: '#8B9388', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: '8px' }}>
            Decision
          </div>
          <div style={{ display: 'flex', gap: '5px', marginBottom: '8px' }}>
            <button onClick={() => setAction('CLEAR')} style={{
              flex: 1, padding: '7px 4px', fontSize: '11px', fontWeight: 500,
              borderRadius: '5px', cursor: 'pointer', fontFamily: 'inherit',
              border: '0.5px solid',
              background: action === 'CLEAR' ? '#EDF2E8' : 'white',
              borderColor: action === 'CLEAR' ? '#73856E' : '#DDD6C9',
              color: action === 'CLEAR' ? '#495844' : '#8B9388',
            }}>
              ✓ Clear
            </button>
            <button onClick={() => setAction('ESCALATE')} style={{
              flex: 1, padding: '7px 4px', fontSize: '11px', fontWeight: 500,
              borderRadius: '5px', cursor: 'pointer', fontFamily: 'inherit',
              border: '0.5px solid',
              background: action === 'ESCALATE' ? '#F5EFE0' : 'white',
              borderColor: action === 'ESCALATE' ? '#7A5C2E' : '#DDD6C9',
              color: action === 'ESCALATE' ? '#7A5C2E' : '#8B9388',
            }}>
              ⚠ Escalate
            </button>
            <button onClick={() => setAction('CONFIRM')} style={{
              flex: 1, padding: '7px 4px', fontSize: '11px', fontWeight: 500,
              borderRadius: '5px', cursor: 'pointer', fontFamily: 'inherit',
              border: '0.5px solid',
              background: action === 'CONFIRM' ? '#F5E8E8' : 'white',
              borderColor: action === 'CONFIRM' ? '#8B4040' : '#DDD6C9',
              color: action === 'CONFIRM' ? '#8B4040' : '#8B9388',
            }}>
              🔒 Confirm
            </button>
          </div>
          <textarea
            placeholder="Add review notes..."
            value={notes}
            onChange={e => setNotes(e.target.value)}
            style={{
              width: '100%', padding: '8px', fontSize: '11px',
              border: '0.5px solid #DDD6C9', borderRadius: '6px',
              background: 'white', color: '#2D2D2D', outline: 'none',
              fontFamily: 'inherit', resize: 'vertical', minHeight: '56px',
              marginBottom: '8px',
            }}
          />
          <button
            onClick={handleReview}
            disabled={!action || !notes || loading}
            style={{
              width: '100%', padding: '8px', fontSize: '12px', fontWeight: 500,
              border: 'none', borderRadius: '6px',
              background: !action || !notes ? '#F6F3EE' : '#495844',
              color: !action || !notes ? '#8B9388' : 'white',
              cursor: !action || !notes ? 'not-allowed' : 'pointer',
              fontFamily: 'inherit',
            }}
          >
            {loading ? 'Submitting...' : 'Submit review'}
          </button>
        </div>
      ) : (
        <div style={{ background: '#EDF2E8', border: '0.5px solid #73856E', borderRadius: '7px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '12px', fontWeight: 500, color: '#495844', marginBottom: '3px' }}>✓ Review submitted</div>
          <div style={{ fontSize: '11px', color: '#8B9388' }}>Action: {action} · Logged in audit trail</div>
        </div>
      )}
    </div>
  )
}