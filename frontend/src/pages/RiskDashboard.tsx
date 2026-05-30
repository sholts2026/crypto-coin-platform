import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { RiskReview } from '../types'
import { ShieldAlert, Play } from 'lucide-react'
import clsx from 'clsx'

function RiskMeter({ label, value, max = 10 }: { label: string; value: number; max?: number }) {
  const pct = (value / max) * 100
  const color = pct >= 70 ? 'bg-red-500' : pct >= 40 ? 'bg-yellow-500' : 'bg-green-500'
  return (
    <div>
      <div className="flex justify-between text-xs mb-0.5">
        <span className="text-slate-400">{label}</span>
        <span className={clsx('font-semibold', pct >= 70 ? 'text-red-400' : pct >= 40 ? 'text-yellow-400' : 'text-green-400')}>
          {value.toFixed(1)}/{max}
        </span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5">
        <div className={clsx('h-1.5 rounded-full', color)} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function RiskDashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [reviews, setReviews] = useState<RiskReview[]>([])
  const [selected, setSelected] = useState<RiskReview | null>(null)
  const [running, setRunning] = useState(false)

  const load = () => {
    api.risk.summary().then((d: any) => {
      setSummary(d)
      setReviews(d.reviews || [])
    }).catch(() => {})
  }

  useEffect(() => { load() }, [])

  const runReview = async () => {
    setRunning(true)
    await api.risk.run()
    load(); setRunning(false)
  }

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <ShieldAlert className="text-red-400 w-5 h-5" /> Risk & Compliance
        </h1>
        <button onClick={runReview} disabled={running} className="btn-primary flex items-center gap-1.5">
          <Play className={clsx('w-3.5 h-3.5', running && 'animate-pulse')} />
          {running ? 'Running...' : 'Run Risk Review'}
        </button>
      </div>

      {/* Summary stats */}
      {summary && (
        <div className="grid grid-cols-3 gap-4">
          <div className="stat-card">
            <div className="text-xs text-slate-400 uppercase tracking-wider">Avg Overall Risk</div>
            <div className={clsx('text-2xl font-bold', summary.avg_overall_risk >= 6 ? 'text-red-400' : summary.avg_overall_risk >= 4 ? 'text-yellow-400' : 'text-green-400')}>
              {summary.avg_overall_risk?.toFixed(1)}/10
            </div>
          </div>
          <div className="stat-card">
            <div className="text-xs text-slate-400 uppercase tracking-wider">High Risk Items</div>
            <div className="text-2xl font-bold text-red-400">{summary.high_risk_count}</div>
          </div>
          <div className="stat-card">
            <div className="text-xs text-slate-400 uppercase tracking-wider">Total Warnings</div>
            <div className="text-2xl font-bold text-yellow-400">{summary.total_warnings}</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* List */}
        <div className="space-y-2">
          {reviews.length === 0 ? (
            <div className="card text-slate-500 text-sm">No reviews. Run risk review first.</div>
          ) : reviews.map(r => (
            <div
              key={r.id}
              onClick={() => setSelected(r)}
              className={clsx('card cursor-pointer hover:border-slate-600', selected?.id === r.id && 'border-red-500/50')}
            >
              <div className="text-xs text-slate-400 mb-1">{r.subject_id}</div>
              <div className="flex items-center gap-2">
                <span className={clsx(
                  'text-lg font-bold',
                  r.overall_risk_score >= 6 ? 'text-red-400' : r.overall_risk_score >= 4 ? 'text-yellow-400' : 'text-green-400'
                )}>{r.overall_risk_score.toFixed(1)}</span>
                <span className="text-xs text-slate-500">/10 overall</span>
              </div>
              <div className="text-xs text-slate-500 mt-1">
                {r.flagged_phrases.length + r.flagged_claims.length} flags
              </div>
            </div>
          ))}
        </div>

        {/* Detail */}
        <div className="xl:col-span-2">
          {selected ? (
            <div className="card space-y-4 text-sm">
              <h3 className="font-semibold text-white">Risk Report: {selected.subject_id}</h3>
              <div className="space-y-2.5">
                <RiskMeter label="Overall Risk"    value={selected.overall_risk_score} />
                <RiskMeter label="IP/Trademark"    value={selected.ip_trademark_risk} />
                <RiskMeter label="Marketing"       value={selected.marketing_risk_score} />
                <RiskMeter label="Token"           value={selected.token_risk_score} />
                <RiskMeter label="Platform"        value={selected.platform_risk} />
                <RiskMeter label="Reputational"    value={selected.reputational_risk} />
                <RiskMeter label="Technical"       value={selected.technical_risk} />
              </div>

              {selected.flagged_phrases?.length > 0 && (
                <div>
                  <div className="text-xs text-red-400 font-semibold mb-1">Flagged Phrases</div>
                  <div className="flex flex-wrap gap-1">
                    {selected.flagged_phrases.map((p, i) => (
                      <span key={i} className="text-xs bg-red-500/20 text-red-300 px-2 py-0.5 rounded">"{p}"</span>
                    ))}
                  </div>
                </div>
              )}

              {selected.suggested_revisions?.length > 0 && (
                <div>
                  <div className="text-xs text-yellow-400 font-semibold mb-1">Suggested Revisions</div>
                  <ul className="space-y-1">
                    {selected.suggested_revisions.map((r, i) => (
                      <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                        <span className="text-yellow-400">→</span>{r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selected.required_reviews?.length > 0 && (
                <div className="bg-red-500/10 border border-red-500/20 rounded p-3">
                  <div className="text-xs text-red-400 font-semibold mb-1">Required Human/Legal Reviews</div>
                  {selected.required_reviews.map((r, i) => (
                    <div key={i} className="text-xs text-red-300">• {r}</div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="card text-slate-500 text-sm text-center py-12">Select a review to see details</div>
          )}
        </div>
      </div>
    </div>
  )
}
