import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { SocialDraft } from '../types'
import { FileText, Check, X, RefreshCw } from 'lucide-react'
import clsx from 'clsx'

const PLATFORMS = ['', 'twitter', 'reddit', 'telegram', 'discord', 'tiktok']
const STATUSES  = ['', 'pending', 'approved', 'rejected']

const PLATFORM_ICON: Record<string, string> = {
  twitter: '𝕏', reddit: '🟠', telegram: '✈️', discord: '💬', tiktok: '🎵'
}

export default function SocialDrafts() {
  const [drafts, setDrafts] = useState<SocialDraft[]>([])
  const [platform, setPlatform] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [acting, setActing] = useState<string | null>(null)
  const [selected, setSelected] = useState<SocialDraft | null>(null)

  const load = () => {
    setLoading(true)
    api.social.drafts(platform || undefined, status || undefined)
      .then((d: any) => { setDrafts(d.drafts || []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [platform, status])

  const act = async (action: string, id: string) => {
    setActing(id)
    if (action === 'approve') await api.social.approveDraft(id)
    else if (action === 'reject') await api.social.rejectDraft(id)
    else await api.social.markPublished(id)
    load(); setActing(null)
  }

  const generate = async () => {
    setActing('generate')
    await api.social.generate()
    load(); setActing(null)
  }

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <FileText className="text-blue-400 w-5 h-5" /> Social Draft Approval
        </h1>
        <div className="flex gap-2 flex-wrap">
          <select className="bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-1.5 text-sm" value={platform} onChange={e => setPlatform(e.target.value)}>
            {PLATFORMS.map(p => <option key={p} value={p}>{p || 'All Platforms'}</option>)}
          </select>
          <select className="bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-1.5 text-sm" value={status} onChange={e => setStatus(e.target.value)}>
            {STATUSES.map(s => <option key={s} value={s}>{s || 'All Status'}</option>)}
          </select>
          <button onClick={generate} disabled={acting === 'generate'} className="btn-primary flex items-center gap-1.5">
            <RefreshCw className={clsx('w-3.5 h-3.5', acting === 'generate' && 'animate-spin')} /> Generate
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Draft list */}
        <div className="xl:col-span-1 space-y-2 max-h-[70vh] overflow-y-auto pr-1">
          {loading ? (
            <div className="text-slate-500 text-sm">Loading...</div>
          ) : drafts.length === 0 ? (
            <div className="card text-slate-500 text-sm">No drafts. Generate content first.</div>
          ) : drafts.map(d => (
            <div
              key={d.id}
              onClick={() => setSelected(d)}
              className={clsx(
                'card cursor-pointer hover:border-slate-600 transition-colors',
                selected?.id === d.id && 'border-blue-500/50'
              )}
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="text-sm font-medium text-white">
                  {PLATFORM_ICON[d.platform] || ''} {d.platform}
                </span>
                <span className={clsx(
                  'text-xs px-1.5 py-0.5 rounded',
                  d.approval_status === 'approved' ? 'bg-green-500/20 text-green-400'
                    : d.approval_status === 'rejected' ? 'bg-red-500/20 text-red-400'
                    : 'bg-yellow-500/20 text-yellow-400'
                )}>{d.approval_status}</span>
              </div>
              <div className="text-xs text-slate-400 line-clamp-2">{d.text}</div>
              <div className="text-xs text-slate-600 mt-1">{d.post_type}</div>
            </div>
          ))}
        </div>

        {/* Detail */}
        <div className="xl:col-span-2">
          {selected ? (
            <div className="card space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{PLATFORM_ICON[selected.platform] || ''}</span>
                  <div>
                    <div className="font-semibold text-white capitalize">{selected.platform}</div>
                    <div className="text-xs text-slate-400">{selected.post_type}</div>
                  </div>
                </div>
                <span className={clsx(
                  'px-2 py-0.5 rounded-full text-xs font-semibold',
                  selected.approval_status === 'approved' ? 'badge-approved'
                    : selected.approval_status === 'rejected' ? 'badge-rejected'
                    : 'badge-pending'
                )}>{selected.approval_status}</span>
              </div>

              {/* Post text */}
              <div className="bg-slate-800 rounded-lg p-4">
                <pre className="text-sm text-white whitespace-pre-wrap font-sans">{selected.text}</pre>
              </div>

              {selected.media_prompt && (
                <div>
                  <div className="text-xs text-slate-500 mb-1">Media Prompt</div>
                  <div className="text-xs text-slate-400 bg-slate-800 rounded p-2 italic">{selected.media_prompt}</div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-xs text-slate-500 mb-0.5">Target Audience</div>
                  <div className="text-slate-300 text-xs">{selected.target_audience}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-0.5">Goal</div>
                  <div className="text-slate-300 text-xs">{selected.expected_goal}</div>
                </div>
              </div>

              {selected.risk_flags?.length > 0 && (
                <div className="bg-red-500/10 border border-red-500/20 rounded p-3">
                  <div className="text-xs text-red-400 font-semibold mb-1">Risk Flags</div>
                  {selected.risk_flags.map((f, i) => (
                    <div key={i} className="text-xs text-red-300">⚠ {f}</div>
                  ))}
                </div>
              )}

              <div className="flex gap-2 pt-2 border-t border-slate-800">
                <button onClick={() => act('approve', selected.id)} disabled={!!acting} className="btn-primary flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Approve
                </button>
                <button onClick={() => act('reject', selected.id)} disabled={!!acting} className="btn-danger flex items-center gap-1">
                  <X className="w-3.5 h-3.5" /> Reject
                </button>
                <button onClick={() => act('publish', selected.id)} disabled={!!acting} className="btn-ghost flex items-center gap-1 text-xs">
                  Mark Published
                </button>
              </div>
            </div>
          ) : (
            <div className="card text-slate-500 text-sm text-center py-12">Select a draft to review</div>
          )}
        </div>
      </div>
    </div>
  )
}
