import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { CEODecision } from '../types'
import { Brain, Check, Edit3, Play } from 'lucide-react'
import clsx from 'clsx'

export default function CEODecisionCenter() {
  const [decisions, setDecisions] = useState<CEODecision[]>([])
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  const load = () => {
    setLoading(true)
    api.ceo.decisions().then((d: any) => { setDecisions(d.decisions || []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const runCEO = async () => {
    setRunning(true)
    await api.ceo.score()
    await api.ceo.run()
    load(); setRunning(false)
  }

  const approve = async (id: string) => {
    await api.ceo.approve(id); load()
  }

  const latest = decisions[decisions.length - 1]

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Brain className="text-emerald-400 w-5 h-5" /> CEO Decision Center
        </h1>
        <button onClick={runCEO} disabled={running} className="btn-primary flex items-center gap-1.5">
          <Play className={clsx('w-3.5 h-3.5', running && 'animate-pulse')} />
          {running ? 'Running...' : 'Run CEO Agent'}
        </button>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm">Loading...</div>
      ) : !latest ? (
        <div className="card text-slate-500 text-sm">No decisions yet. Run CEO Agent.</div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {/* Main recommendation */}
          <div className="xl:col-span-2 space-y-4">
            <div className="card border-green-500/30 bg-green-500/5">
              <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Recommended Token</div>
              <div className="text-2xl font-bold text-white">{latest.recommended_token_name}</div>
              <div className="flex items-center gap-2 mt-2">
                <span className={clsx(
                  'px-2 py-0.5 rounded-full text-xs font-semibold',
                  latest.human_approval_status === 'approved' ? 'bg-green-500/20 text-green-400'
                    : latest.human_approval_status === 'rejected' ? 'bg-red-500/20 text-red-400'
                    : 'bg-yellow-500/20 text-yellow-400'
                )}>
                  {latest.human_approval_status}
                </span>
              </div>
            </div>

            {/* Score breakdown */}
            {Object.keys(latest.score_breakdown).length > 0 && (
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">Score Breakdown</h3>
                <div className="space-y-2">
                  {Object.entries(latest.score_breakdown).map(([k, v]) => (
                    <div key={k} className="flex items-center gap-3">
                      <div className="text-xs text-slate-400 w-40 shrink-0">{k.replace(/_/g, ' ')}</div>
                      <div className="flex-1 bg-slate-800 rounded-full h-2">
                        <div
                          className={clsx('h-2 rounded-full', k === 'risk_score' ? 'bg-red-500' : 'bg-green-500')}
                          style={{ width: `${Math.min(100, k === 'risk_score' ? (v as number)*10 : (v as number))}%` }}
                        />
                      </div>
                      <div className="text-xs text-slate-300 w-12 text-right font-semibold">{(v as number).toFixed(1)}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Summary report */}
            {latest.summary_report && (
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">Decision Report</h3>
                <pre className="text-xs text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
                  {latest.summary_report}
                </pre>
              </div>
            )}
          </div>

          {/* Sidebar info */}
          <div className="space-y-4">
            {/* Selection reasons */}
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-2">Why Selected</h3>
              <ul className="space-y-1.5">
                {latest.selection_reasons.map((r, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                    <span className="text-green-400 mt-0.5">✓</span>{r}
                  </li>
                ))}
              </ul>
            </div>

            {/* Rejected */}
            {latest.rejected_alternatives?.length > 0 && (
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Rejected Alternatives</h3>
                {latest.rejected_alternatives.map((alt, i) => (
                  <div key={i} className="mb-2 pb-2 border-b border-slate-800 last:border-0 last:mb-0">
                    <div className="text-xs font-semibold text-slate-400">{alt.name}</div>
                    <div className="text-xs text-slate-500">{alt.reason}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Next actions */}
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-2">Required Actions</h3>
              <ul className="space-y-1">
                {latest.required_next_actions.map((a, i) => (
                  <li key={i} className="text-xs text-slate-400 flex items-start gap-1.5">
                    <span className="text-yellow-400 mt-0.5">→</span>{a}
                  </li>
                ))}
              </ul>
            </div>

            {/* Approve button */}
            {latest.human_approval_status === 'pending' && (
              <div className="space-y-2">
                <button onClick={() => approve(latest.id)} className="btn-primary w-full flex items-center justify-center gap-1.5">
                  <Check className="w-4 h-4" /> Approve Decision
                </button>
                <button onClick={() => api.ceo.revise(latest.id).then(load)} className="btn-ghost w-full flex items-center justify-center gap-1.5">
                  <Edit3 className="w-4 h-4" /> Request Revision
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
