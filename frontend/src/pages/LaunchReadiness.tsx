import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { LaunchReadiness as LR } from '../types'
import { CheckSquare, Check, X, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

const LABELS: Record<string, string> = {
  trend_validated:               'Trend Validated',
  token_concept_approved:        'Token Concept Approved',
  brand_package_approved:        'Brand Package Approved',
  risk_review_completed:         'Risk Review Completed',
  social_infrastructure_prepared:'Social Infrastructure Prepared',
  first_content_calendar_ready:  'First Content Calendar Ready',
  community_channels_ready:      'Community Channels Ready',
  smart_contract_generated:      'Smart Contract Generated',
  smart_contract_tests_passed:   'Smart Contract Tests Passed',
  tokenomics_reviewed:           'Tokenomics Reviewed',
  launch_report_generated:       'Launch Report Generated',
  human_approval_received:       'Human Approval Received',
}

export default function LaunchReadiness() {
  const [data, setData] = useState<LR | null>(null)

  useEffect(() => {
    api.launchReadiness().then((d: any) => setData(d)).catch(() => {})
  }, [])

  if (!data) return <div className="p-6 text-slate-400">Loading...</div>

  const color = data.readiness_pct >= 80 ? 'text-green-400' : data.readiness_pct >= 50 ? 'text-yellow-400' : 'text-red-400'
  const barColor = data.readiness_pct >= 80 ? 'bg-green-500' : data.readiness_pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <h1 className="text-xl font-bold flex items-center gap-2">
        <CheckSquare className="text-green-400 w-5 h-5" /> Launch Readiness
      </h1>

      {/* Progress */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-sm text-slate-400">Overall Readiness</div>
            <div className={clsx('text-4xl font-bold', color)}>{data.readiness_pct}%</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-500">{data.done_count} of {data.total_count} items complete</div>
            <div className={clsx('text-sm font-semibold', data.readiness_pct >= 80 ? 'text-green-400' : 'text-yellow-400')}>
              {data.readiness_pct >= 100 ? 'Ready to Launch' : data.readiness_pct >= 80 ? 'Almost Ready' : 'In Progress'}
            </div>
          </div>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-3">
          <div className={clsx('h-3 rounded-full transition-all', barColor)} style={{ width: `${data.readiness_pct}%` }} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Checklist */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-300 mb-3">Launch Checklist</h2>
          <div className="space-y-2">
            {Object.entries(data.checklist).map(([key, done]) => (
              <div key={key} className="flex items-center gap-3">
                <div className={clsx('w-5 h-5 rounded flex items-center justify-center shrink-0',
                  done ? 'bg-green-500/20' : 'bg-slate-800'
                )}>
                  {done
                    ? <Check className="w-3 h-3 text-green-400" />
                    : <X className="w-3 h-3 text-slate-600" />
                  }
                </div>
                <span className={clsx('text-sm', done ? 'text-slate-300' : 'text-slate-500')}>
                  {LABELS[key] ?? key.replace(/_/g, ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Blockers & warnings */}
        <div className="space-y-4">
          {data.blockers.length > 0 && (
            <div className="card">
              <h2 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-1.5">
                <X className="w-4 h-4" /> Blockers ({data.blockers.length})
              </h2>
              <ul className="space-y-1">
                {data.blockers.map((b, i) => (
                  <li key={i} className="text-xs text-red-300 flex items-start gap-1.5">
                    <span className="mt-0.5">•</span>{b}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {data.warnings.length > 0 && (
            <div className="card border-yellow-500/20 bg-yellow-500/5">
              <h2 className="text-sm font-semibold text-yellow-400 mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" /> Warnings
              </h2>
              <ul className="space-y-1">
                {data.warnings.map((w, i) => (
                  <li key={i} className="text-xs text-yellow-300">⚠ {w}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="card border-blue-500/20 bg-blue-500/5">
            <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Next Action</div>
            <div className="text-white font-medium text-sm">{data.next_action}</div>
          </div>

          <div className="card border-red-500/20">
            <p className="text-xs text-red-400 font-semibold">Human Approval Required</p>
            <p className="text-xs text-slate-400 mt-1">
              No public launch activity should happen without explicit human founder approval.
              All agent outputs are drafts and recommendations only.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
