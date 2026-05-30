import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Overview } from '../types'
import { TrendingUp, Lightbulb, FileText, ShieldAlert, Rocket, ArrowRight, Zap } from 'lucide-react'
import clsx from 'clsx'

function StatCard({ icon: Icon, label, value, color = 'text-green-400' }: {
  icon: React.ElementType; label: string; value: string | number; color?: string
}) {
  return (
    <div className="stat-card">
      <div className="flex items-center gap-2 text-slate-400 text-xs uppercase tracking-wider mb-1">
        <Icon className={clsx('w-3.5 h-3.5', color)} />
        {label}
      </div>
      <div className={clsx('text-2xl font-bold', color)}>{value}</div>
    </div>
  )
}

export default function ExecutiveOverview() {
  const [data, setData] = useState<Overview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    api.overview()
      .then((d: any) => { setData(d); setLoading(false) })
      .catch((e: any) => { setError(String(e)); setLoading(false) })
  }, [])

  if (loading) return <div className="p-8 text-slate-400 animate-pulse">Loading overview...</div>
  if (!data) return (
    <div className="p-8">
      <div className="card max-w-2xl">
        <p className="text-red-400 font-bold mb-3">Connection error</p>
        <p className="text-slate-300 text-sm font-mono break-all mb-3">{error || 'Unknown error'}</p>
        <p className="text-slate-500 text-xs">Target: {(window as any).__API_BASE__ || 'check console'}</p>
      </div>
    </div>
  )

  const readinessColor = data.launch_readiness_score >= 70 ? 'text-green-400'
    : data.launch_readiness_score >= 40 ? 'text-yellow-400' : 'text-red-400'

  return (
    <div className="p-6 space-y-6 max-w-screen-xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Rocket className="text-green-400 w-6 h-6" />
          Launch Command Center
        </h1>
        <p className="text-slate-400 text-sm mt-1">Multi-agent crypto token research & launch platform</p>
      </div>

      {/* CEO recommendation */}
      {data.ceo_recommendation && (
        <div className="card border-green-500/30 bg-green-500/5">
          <div className="flex items-center gap-2 text-green-400 font-semibold text-sm mb-1">
            <Zap className="w-4 h-4" /> CEO Recommendation
          </div>
          <p className="text-white text-lg font-bold">{data.ceo_recommendation}</p>
          <p className="text-slate-400 text-sm mt-1">{data.next_recommended_action}</p>
        </div>
      )}

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={TrendingUp}  label="Trends Detected"  value={data.total_trends_detected}  color="text-cyan-400" />
        <StatCard icon={Lightbulb}   label="Token Ideas"      value={data.total_token_ideas}       color="text-yellow-400" />
        <StatCard icon={FileText}    label="Social Drafts"    value={data.total_social_drafts}     color="text-blue-400" />
        <StatCard icon={ShieldAlert} label="Risk Warnings"    value={data.total_risk_warnings}     color="text-red-400" />
      </div>

      {/* Launch readiness */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-slate-300">Launch Readiness</span>
          <span className={clsx('text-xl font-bold', readinessColor)}>{data.launch_readiness_score}%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-2">
          <div
            className={clsx('h-2 rounded-full transition-all', data.launch_readiness_score >= 70 ? 'bg-green-500' : data.launch_readiness_score >= 40 ? 'bg-yellow-500' : 'bg-red-500')}
            style={{ width: `${data.launch_readiness_score}%` }}
          />
        </div>
      </div>

      {/* Top trends */}
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-cyan-400" /> Top Trending Narratives
        </h2>
        <div className="space-y-2">
          {data.top_trending_narratives.map((phrase, i) => (
            <div key={i} className="flex items-center gap-3 text-sm">
              <span className="text-slate-500 w-4 shrink-0">#{i + 1}</span>
              <span className="text-slate-200">{phrase}</span>
            </div>
          ))}
          {data.top_trending_narratives.length === 0 && (
            <p className="text-slate-500 text-sm">No trends yet. Run <code className="text-green-400">collect-trends</code></p>
          )}
        </div>
      </div>

      {/* Next action */}
      <div className="card flex items-center gap-3 border-blue-500/20 bg-blue-500/5">
        <ArrowRight className="text-blue-400 w-5 h-5 shrink-0" />
        <div>
          <div className="text-xs text-slate-400 uppercase tracking-wider">Next Recommended Action</div>
          <div className="text-white font-medium">{data.next_recommended_action}</div>
        </div>
      </div>
    </div>
  )
}
