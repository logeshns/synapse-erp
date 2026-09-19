import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard, ClipboardList, ShoppingCart, Users, FileText,
  PackageSearch, Sparkles, Receipt, CreditCard, UsersRound, LineChart,
  MessageSquareText, LogOut,
} from 'lucide-react'
import { useAuth } from '../auth/AuthContext'

const NAV_BY_ROLE = {
  SALES: [
    { to: '/sales', label: 'Dashboard', end: true, icon: LayoutDashboard },
    { to: '/sales/order-requests', label: 'Order Requests', icon: ClipboardList },
    { to: '/sales/orders', label: 'Orders', icon: ShoppingCart },
    { to: '/sales/customers', label: 'Customers', icon: Users },
    { to: '/sales/invoices', label: 'Invoices', icon: FileText },
  ],
  WAREHOUSE: [
    { to: '/warehouse', label: 'Dashboard', end: true, icon: LayoutDashboard },
    { to: '/warehouse/pending-orders', label: 'Pending Orders', icon: ClipboardList },
    { to: '/warehouse/inventory', label: 'Inventory', icon: PackageSearch },
    { to: '/warehouse/assistant', label: 'AI Assistant', icon: Sparkles },
  ],
  ACCOUNTANT: [
    { to: '/accountant', label: 'Dashboard', end: true, icon: LayoutDashboard },
    { to: '/accountant/payments', label: 'Payments', icon: CreditCard },
    { to: '/accountant/receipts', label: 'Receipts', icon: Receipt },
  ],
  MANAGER: [
    { to: '/manager', label: 'Dashboard', end: true, icon: LayoutDashboard },
    { to: '/manager/team', label: 'Team', icon: UsersRound },
  ],
  OWNER: [
    { to: '/owner', label: 'Dashboard', end: true, icon: LineChart },
    { to: '/owner/business-analyst', label: 'Business Analyst', icon: MessageSquareText },
  ],
}

export default function DashboardLayout() {
  const { user, logout } = useAuth()
  const navItems = NAV_BY_ROLE[user?.role] || []
  const initials = (user?.name || '?').split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase()

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <aside className="w-64 bg-ink-950 text-slate-300 flex flex-col">
        <div className="px-5 py-6 flex items-center gap-2.5 border-b border-white/5">
          <div className="w-8 h-8 rounded-lg bg-brand-gradient flex items-center justify-center shrink-0">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm leading-tight">Synapse ERP</div>
            <div className="text-[11px] text-slate-500">AI-Powered Automation</div>
          </div>
        </div>
        <nav className="flex-1 px-3 py-5 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors relative ${
                    isActive ? 'bg-white/10 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive && <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-full bg-brand-400" />}
                    <Icon className="w-4 h-4 shrink-0" strokeWidth={2} />
                    {item.label}
                  </>
                )}
              </NavLink>
            )
          })}
        </nav>
        <div className="px-4 py-4 border-t border-white/5 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-gradient flex items-center justify-center text-white text-xs font-semibold shrink-0">{initials}</div>
          <div className="flex-1 min-w-0">
            <div className="text-white text-sm truncate">{user?.name}</div>
            <div className="text-slate-500 text-xs">{user?.role}</div>
          </div>
          <button onClick={logout} title="Log out" className="text-slate-500 hover:text-white p-1.5 rounded-md hover:bg-white/5">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto p-8 animate-fadeIn">
          <Outlet />
        </div>
      </main>
    </div>
  )
}