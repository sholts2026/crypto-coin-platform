import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { AgentStatus } from '../types'
import { Activity, RefreshCw } from 'lucide-react'
import clsx from 'clsx'

const AGENT_LABELS: Record<string, string> = {
  ceo_agent:              'CEO Agent',
  trend_hunter_agent:     'Trend Hunter',
  token_concept_agent:    'Token Concept',
  token_builder_agent:    'Token Builder',
  social_strategy_agent:  'Social Strategy',
  community_agent:        'Community',
  brand_agent:            'Brand',
  risk_review_agent:      'Risk Review',
}

const AGENT_COLORS: Record<string, string> = {
  ceo_agent:              'text-emerald-400',
  trend_hunter_agent:     'text-cyan-400',
  token_concept_agent:    'text-yellow-400',
  token_builder_agent:    'text-blue-400',
  social_strategy_agent:  'text-purple-400',
  community_agent:        'text-pink-400',
  brand_agent:            'text-orange-400',
  risk_review_agent:      'text-red-400',
}

export default function AgentMonitor() {
  const [agents, setAgents] = useState<AgentStatus[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.agents().then((d: any) => { setAgents(d.agents || []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Activity className="text-green-400 w-5 h-5" /> Agent Monitor
        </h1>
        <button onClick={load} className="btn-ghost flex items-center gap-1.5">
          <RefreshCw className={clsx('w-3.5 h-3.5', loading && 'animate-spin')} /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {loading ? (
          <div className="text-slate-500 text-sm col-span-4">Loading agents...</div>
        ) : agents.map(agent => (
          <div key={agent.agent_name} className="card space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <div className={clsx('font-semibold text-sm', AGENT_COLORS[agent.agent_name] || 'text-white')}>
                  {AGENT_LABELS[agent.agent_name] || agent.agent_name}
                </div>
                <div className="text-xs text-slate-500">{agent.agent_name}</div>
              </div>
              <span className={clsx(
                'text-xs px-2 py-0.5 rounded-full',
                agent.status === 'ready' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
              )}>
                {agent.status}
              </span>
            </div>

            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Outputs</span>
                <span className="text-white font-semibold">{agent.last_output_count}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Last Run</span>
                <span className="text-slate-300">
                  {agent.last_run_time
                    ? new Date(agent.last_run_time).toLocaleDateString()
                    : 'Never'}
                </span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Current Task</span>
                <span className="text-slate-300">{agent.current_task}</span>
              </div>
            </div>

            {agent.errors?.length > 0 && (
              <div className="bg-red-500/10 rounded p-2">
                {agent.errors.map((e, i) => <div key={i} className="text-xs text-red-300">{e}</div>)}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="font-semibold text-slate-300 text-sm mb-3">Run Pipeline Steps</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          {[
            ['collect-trends', 'Collect Trends'],
            ['generate-token-ideas', 'Generate Ideas'],
            ['run-risk-review', 'Risk Review'],
            ['score-token-ideas', 'Score Ideas'],
            ['generate-brand-package', 'Brand Package'],
            ['generate-social-calendar', 'Social Calendar'],
            ['ceo-decision', 'CEO Decision'],
            ['export-report', 'Export Report'],
          ].map(([cmd, label]) => (
            <div key={cmd} className="bg-slate-800 rounded p-2">
              <div className="text-slate-300 font-medium">{label}</div>
              <code className="text-green-400 text-xs">python cli/main.py {cmd}</code>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
