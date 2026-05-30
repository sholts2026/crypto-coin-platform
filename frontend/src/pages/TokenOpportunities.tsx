import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { TokenIdea } from '../types'
import { Lightbulb, Check, X, Edit3, RefreshCw } from 'lucide-react'
import clsx from 'clsx'

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    pending: 'badge-pending', approved: 'badge-approved',
    rejected: 'badge-rejected', needs_revision: 'badge-revision'
  }
  return <span className={map[status] || 'badge-pending'}>{status.replace('_', ' ')}</span>
}

function ScoreBar({ label, value, color = 'bg-green-500' }: { label: string; value: number; color?: string }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-0.5">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300 font-semibold">{value.toFixed(0)}</span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5">
        <div className={clsx('h-1.5 rounded-full', color)} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

export default function TokenOpportunities() {
  const [ideas, setIdeas] = useState<TokenIdea[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<TokenIdea | null>(null)
  const [acting, setActing] = useState(false)

  const load = () => {
    setLoading(true)
    api.tokens.list().then((d: any) => { setIdeas(d.ideas || []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const act = async (action: 'approve' | 'reject' | 'revise', id: string) => {
    setActing(true)
    if (action === 'approve') await api.tokens.approve(id)
    else if (action === 'reject') await api.tokens.reject(id)
    else await api.tokens.revise(id)
    load(); setActing(false)
  }

  const generate = async () => {
    setActing(true)
    await api.tokens.generate()
    load(); setActing(false)
  }

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Lightbulb className="text-yellow-400 w-5 h-5" /> Token Opportunities
        </h1>
        <button onClick={generate} disabled={acting} className="btn-primary flex items-center gap-1.5">
          <RefreshCw className={clsx('w-3.5 h-3.5', acting && 'animate-spin')} /> Generate Ideas
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* List */}
        <div className="xl:col-span-1 space-y-2">
          {loading ? (
            <div className="text-slate-500 text-sm">Loading...</div>
          ) : ideas.length === 0 ? (
            <div className="card text-slate-500 text-sm">No ideas. Collect trends first.</div>
          ) : ideas.map(idea => (
            <div
              key={idea.id}
              onClick={() => setSelected(idea)}
              className={clsx(
                'card cursor-pointer hover:border-slate-600 transition-colors',
                selected?.id === idea.id && 'border-green-500/50'
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-bold text-white">{idea.token_name}</div>
                  <div className="text-green-400 text-xs">${idea.ticker}</div>
                </div>
                <StatusBadge status={idea.approval_status} />
              </div>
              <div className="text-slate-400 text-xs mt-1.5 line-clamp-2">{idea.one_line_narrative}</div>
              <div className="flex gap-3 mt-2">
                <span className="text-xs text-slate-500">Score: <span className="text-green-400 font-bold">{(idea.opportunity_score || 0).toFixed(1)}</span></span>
                <span className="text-xs text-slate-500">Risk: <span className="text-red-400 font-bold">{(idea.risk_score || 0).toFixed(1)}/10</span></span>
              </div>
            </div>
          ))}
        </div>

        {/* Detail */}
        <div className="xl:col-span-2">
          {selected ? (
            <div className="card space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">{selected.token_name}</h2>
                  <div className="text-green-400 font-semibold">${selected.ticker}</div>
                </div>
                <StatusBadge status={selected.approval_status} />
              </div>

              <p className="text-slate-300">{selected.one_line_narrative}</p>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-slate-500 text-xs mb-1">Target Community</div>
                  <div className="text-slate-300">{selected.target_community}</div>
                </div>
                <div>
                  <div className="text-slate-500 text-xs mb-1">Why Now</div>
                  <div className="text-slate-300 text-xs">{selected.why_now}</div>
                </div>
              </div>

              <div className="space-y-2">
                <ScoreBar label="Meme Potential"  value={selected.meme_potential}       color="bg-pink-500" />
                <ScoreBar label="Community"       value={selected.community_potential}   color="bg-blue-500" />
                <ScoreBar label="Novelty"         value={selected.novelty}               color="bg-purple-500" />
                <ScoreBar label="Timing"          value={selected.timing}                color="bg-yellow-500" />
                <ScoreBar label="Technical"       value={selected.technical_feasibility} color="bg-cyan-500" />
              </div>

              {selected.meme_angle && (
                <div>
                  <div className="text-slate-500 text-xs mb-1">Meme Angle</div>
                  <div className="bg-slate-800 rounded p-3 text-sm text-slate-300 italic">{selected.meme_angle}</div>
                </div>
              )}

              {selected.possible_risks?.length > 0 && (
                <div>
                  <div className="text-slate-500 text-xs mb-1">Risks</div>
                  <ul className="space-y-1">
                    {selected.possible_risks.map((r, i) => (
                      <li key={i} className="text-xs text-red-400 flex items-start gap-1.5">
                        <span className="mt-0.5">⚠</span>{r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-2 border-t border-slate-800">
                <button onClick={() => act('approve', selected.id)} disabled={acting} className="btn-primary flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Approve
                </button>
                <button onClick={() => act('revise', selected.id)} disabled={acting} className="btn-ghost flex items-center gap-1">
                  <Edit3 className="w-3.5 h-3.5" /> Revise
                </button>
                <button onClick={() => act('reject', selected.id)} disabled={acting} className="btn-danger flex items-center gap-1">
                  <X className="w-3.5 h-3.5" /> Reject
                </button>
              </div>
            </div>
          ) : (
            <div className="card text-slate-500 text-sm text-center py-12">Select a token idea to view details</div>
          )}
        </div>
      </div>
    </div>
  )
}
