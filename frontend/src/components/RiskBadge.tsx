export default function RiskBadge({ level }: { level: string }) {
  const styles: Record<string, { bg: string; color: string; border: string }> = {
    CRITICAL: { bg: '#FEF2F2', color: '#DC2626', border: '#FECACA' },
    HIGH:     { bg: '#FFF7ED', color: '#EA580C', border: '#FED7AA' },
    MEDIUM:   { bg: '#FEFCE8', color: '#CA8A04', border: '#FEF08A' },
    LOW:      { bg: '#F0FDF4', color: '#16A34A', border: '#BBF7D0' },
  }
  const s = styles[level] || { bg: '#F8F9FB', color: '#4A5568', border: '#E8ECF2' }

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '5px',
      fontSize: '10px', fontWeight: 500,
      padding: '2px 7px', borderRadius: '4px',
      background: s.bg, color: s.color,
      border: `0.5px solid ${s.border}`,
    }}>
      <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: s.color, flexShrink: 0 }} />
      {level}
    </span>
  )
}