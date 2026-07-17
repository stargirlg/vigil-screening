interface NavItem {
  icon: string
  label: string
  key: string
  badge?: boolean
  section?: string
  roles?: string[]
}

const NAV: NavItem[] = [
  // =========================
  // Dashboards
  // =========================
  {
    icon: 'ti-layout-dashboard',
    label: 'Dashboard',
    key: 'dashboard',
    roles: ['ADMIN'],
  },
  {
    icon: 'ti-layout-dashboard',
    label: 'Dashboard',
    key: 'analyst',
    roles: ['ANALYST'],
  },
  {
    icon: 'ti-layout-dashboard',
    label: 'Dashboard',
    key: 'checker',
    roles: ['CHECKER'],
  },
  {
    icon: 'ti-layout-dashboard',
    label: 'Dashboard',
    key: 'co_dashboard',
    roles: ['CO'],
  },

  // =========================
  // Core Operations
  // =========================
  {
    icon: 'ti-shield-check',
    label: 'Alert Queue',
    key: 'alerts',
    badge: true,
    roles: ['ADMIN', 'ANALYST', 'CHECKER', 'CO'],
  },
  {
    icon: 'ti-folder',
    label: 'Cases',
    key: 'cases',
    roles: ['ADMIN', 'ANALYST', 'CHECKER', 'CO'],
  },
  {
    icon: 'ti-users',
    label: 'Customers',
    key: 'customers',
    roles: ['ADMIN', 'ANALYST', 'CHECKER', 'CO'],
  },
  {
    icon: 'ti-flag',
    label: 'Watchlist',
    key: 'watchlist',
    roles: ['ADMIN', 'ANALYST', 'CHECKER', 'CO'],
  },

  // =========================
  // Compliance Officer
  // =========================
  {
    icon: 'ti-checks',
    label: 'Approvals',
    key: 'approvals',
    roles: ['CO'],
    section: 'CO Actions',
  },
  {
    icon: 'ti-file-invoice',
    label: 'SAR Queue',
    key: 'sar',
    roles: ['CO'],
  },

  // =========================
  // Reports
  // =========================
  {
    icon: 'ti-chart-bar',
    label: 'Analytics',
    key: 'analytics',
    roles: ['ADMIN', 'ANALYST', 'CHECKER', 'CO'],
    section: 'Reports',
  },
  {
    icon: 'ti-file-text',
    label: 'Audit',
    key: 'audit',
    roles: ['ADMIN', 'CO'],
  },

  // =========================
  // Administration
  // =========================
  {
    icon: 'ti-settings-2',
    label: 'Rules',
    key: 'rules',
    roles: ['ADMIN'],
    section: 'Admin',
  },
  {
    icon: 'ti-users-group',
    label: 'Users',
    key: 'users',
    roles: ['ADMIN'],
  },
  {
    icon: 'ti-settings',
    label: 'Settings',
    key: 'settings',
    roles: ['ADMIN'],
  },
]
interface SidebarProps {
  active: string
  onChange: (key: string) => void
  pendingAlerts?: number
  role?: string
}

export default function Sidebar({ active, onChange, pendingAlerts = 0, role = 'ANALYST' }: SidebarProps) {
  const visibleItems = NAV.filter(item => !item.roles || item.roles.includes(role))
  let lastSection = ''

  return (
    <div style={{
      width: '200px', minHeight: 'calc(100vh - 48px)',
      background: '#F6F3EE', borderRight: '0.5px solid #DDD6C9',
      padding: '12px 0', flexShrink: 0,
      display: 'flex', flexDirection: 'column',
    }}>
      {/* Role badge */}
      <div style={{
        padding: '8px 16px 12px',
        borderBottom: '0.5px solid #DDD6C9',
        marginBottom: '8px',
      }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '6px',
          padding: '3px 8px', borderRadius: '4px', fontSize: '10px', fontWeight: 500,
          background: role === 'ADMIN'   ? '#EDF2E8' :
                      role === 'CO'      ? '#F5EFE0' :
                      role === 'ANALYST' ? '#EEF2FF' : '#F6F3EE',
          color: role === 'ADMIN'   ? '#495844' :
                 role === 'CO'      ? '#7A5C2E' :
                 role === 'ANALYST' ? '#4338CA' : '#8B9388',
          border: '0.5px solid #DDD6C9',
        }}>
          <i className={
            role === 'ADMIN'   ? 'ti ti-settings' :
            role === 'CO'      ? 'ti ti-shield-check' :
            role === 'ANALYST' ? 'ti ti-search' : 'ti ti-checks'
          } style={{ fontSize: '11px' }} />
          {role}
        </div>
      </div>

      {visibleItems.map(item => {
        const showSection = item.section && item.section !== lastSection
        if (item.section) lastSection = item.section

        return (
          <div key={item.key}>
            {showSection && (
              <div style={{
                fontSize: '10px', color: '#8B9388',
                padding: '12px 16px 4px',
                letterSpacing: '0.08em', textTransform: 'uppercase',
              }}>
                {item.section}
              </div>
            )}
            <button
              onClick={() => onChange(item.key)}
              style={{
                display: 'flex', alignItems: 'center', gap: '9px',
                padding: '8px 16px', width: '100%', textAlign: 'left',
                background: active === item.key ? '#F4F1EA' : 'none',
                borderLeft: active === item.key ? '2px solid #73856E' : '2px solid transparent',
                borderTop: 'none', borderRight: 'none', borderBottom: 'none',
                fontSize: '13px', cursor: 'pointer',
                color: active === item.key ? '#495844' : '#8B9388',
                fontFamily: "'DM Sans', sans-serif",
                fontWeight: active === item.key ? 500 : 400,
                transition: 'all 0.12s',
              }}
              onMouseOver={e => { if (active !== item.key) e.currentTarget.style.color = '#495844' }}
              onMouseOut={e  => { if (active !== item.key) e.currentTarget.style.color = '#8B9388' }}
            >
              <i className={`ti ${item.icon}`} style={{ fontSize: '15px', width: '16px' }} />
              {item.label}
              {item.badge && pendingAlerts > 0 && (
                <span style={{
                  marginLeft: 'auto', background: '#73856E', color: 'white',
                  fontSize: '10px', padding: '1px 6px', borderRadius: '10px', fontWeight: 500,
                }}>
                  {pendingAlerts}
                </span>
              )}
            </button>
          </div>
        )
      })}
    </div>
  )
}