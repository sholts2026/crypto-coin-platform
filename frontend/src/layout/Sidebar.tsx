import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, TrendingUp, Lightbulb, Brain, BarChart2,
  FileText, Palette, ShieldAlert, Code2, CheckSquare,
  Activity, Download, Rocket
} from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/',              icon: LayoutDashboard, label: 'Executive Overview' },
  { to: '/trends',        icon: TrendingUp,      label: 'Trend Intelligence' },
  { to: '/tokens',        icon: Lightbulb,       label: 'Token Opportunities' },
  { to: '/ceo',           icon: Brain,           label: 'CEO Decision Center' },
  { to: '/social',        icon: BarChart2,        label: 'Social Performance' },
  { to: '/drafts',        icon: FileText,        label: 'Social Drafts' },
  { to: '/brand',         icon: Palette,         label: 'Brand Dashboard' },
  { to: '/risk',          icon: ShieldAlert,     label: 'Risk & Compliance' },
  { to: '/contracts',     icon: Code2,           label: 'Smart Contracts' },
  { to: '/launch',        icon: CheckSquare,     label: 'Launch Readiness' },
  { to: '/agents',        icon: Activity,        label: 'Agent Monitor' },
  { to: '/reports',       icon: Download,        label: 'Reports' },
]

export default function Sidebar() {
  return (
    <aside className="flex flex-col w-60 min-h-screen bg-[#13151f] border-r border-slate-800 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-4 border-b border-slate-800">
        <Rocket className="text-green-400 w-5 h-5" />
        <span className="font-bold text-sm tracking-wide text-white">CryptoLaunch AI</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-5 py-2.5 text-sm transition-colors',
              isActive
                ? 'text-green-400 bg-green-500/10 border-r-2 border-green-400'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            )}
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-slate-800 text-xs text-slate-600">
        v1.0.0 · All outputs require human approval
      </div>
    </aside>
  )
}
