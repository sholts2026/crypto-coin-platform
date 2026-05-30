import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Trend } from '../types'
import { TrendingUp, RefreshCw, Send } from 'lucide-react'
import clsx from 'clsx'

const PLATFORMS = ['', 'twitter', 'reddit', 'tiktok', 'youtube', 'crypto_news', 'google_trends']

function ScorePill({ value }: { value: number }) {
  const color = value >= 80 ? 'bg-green-500/20 text-green-400' : value >= 60 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-slate-700 text-slate-400'
  return <span className={clsx('px-2 py-0.5 rounded text-xs font-semibold', color)}>{value.toFixed(0)}</span>
}

export default function TrendsDashboard() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [platform, setPlatform] = useState('')
  const [loading, setLoading] = useState(true)
  const [collecting, setCollecting] = useState(false)
  const [selected, setSelected] = useState<Trend | null>(null)

  const load = () => {
    setLoading(true)
    api.trends.list(platform || undefined).then((d: any) => {
      setTrends(d.trends || []); setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [platform])

  const collect = async () => {
    setCollecting(true)
    await api.trends.collect(true)
    load()
    setCollecting(false)
  }

  const sendToAgent = async (id: string) => {
    await api.trends.sendToAgent(id)
    alert('Sent to Token Concept Agent!')
  }

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <TrendingUp className="text-cyan-400 w-5 h-5" /> Trend Intelligence
        </h1>
        <div className="flex gap-2">
          <select
            className="bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-1.5 text-sm"
            value={platform} onChange={e => setPlatform(e.target.value)}
          >
            {PLATFORMS.map(p => <option key={p} value={p}>{p || 'All Platforms'}</option>)}
          </select>
          <button onClick={collect} disabled={collecting} className="btn-primary flex items-center gap-1.5">
            <RefreshCw className={clsx('w-3.5 h-3.5', collecting && 'animate-spin')} />
            {collecting ? 'Collecting...' : 'Collect Trends'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Table */}
        <div className="xl:col-span-2 card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 text-xs uppercase tracking-wider border-b border-slate-800">
                <th className="text-left py-2 pr-4">Trend</th>
                <th className="text-left py-2 pr-4">Platform</th>
                <th className="text-right py-2 pr-4">Score</th>
                <th className="text-right py-2 pr-4">Meme</th>
                <th className="text-right py-2 pr-4">Vel.</th>
                <th className="text-right py-2"></th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6} className="py-8 text-center text-slate-500">Loading...</td></tr>
              ) : trends.length === 0 ? (
                <tr><td colSpan={6} className="py-8 text-center text-slate-500">No trends. Click Collect Trends.</td></tr>
              ) : trends.map(t => (
                <tr
                  key={t.id}
                  className={clsx('border-b border-slate-800/50 cursor-pointer hover:bg-slate-800/30', selected?.id === t.id && 'bg-slate-800/50')}
                  onClick={() => setSelected(t)}
                >
                  <td className="py-2.5 pr-4 font-medium text-white">{t.phrase}</td>
                  <td className="py-2.5 pr-4 text-slate-400 text-xs">{t.source_platform}</td>
                  <td className="py-2.5 pr-4 text-right"><ScorePill value={t.composite_score || 0} /></td>
                  <td className="py-2.5 pr-4 text-right text-slate-400">{t.meme_potential.toFixed(0)}</td>
                  <td className="py-2.5 pr-4 text-right text-slate-400">{t.velocity_score.toFixed(0)}</td>
                  <td className="py-2.5 text-right">
                    <button
                      onClick={e => { e.stopPropagation(); sendToAgent(t.id) }}
                      className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                    >
                      <Send className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Detail */}
        <div className="card">
          {selected ? (
            <div className="space-y-3 text-sm">
              <h3 className="font-bold text-white">{selected.phrase}</h3>
              <div className="grid grid-cols-2 gap-2">
                {[
                  ['Velocity', selected.velocity_score],
                  ['Novelty', selected.novelty_score],
                  ['Meme', selected.meme_potential],
                  ['Crypto Rel.', selected.crypto_relevance],
                  ['Saturation', selected.saturation_level],
                  ['Lifespan', `${selected.expected_lifespan_days}d`],
                ].map(([k, v]) => (
                  <div key={k as string} className="bg-slate-800 rounded p-2">
                    <div className="text-slate-500 text-xs">{k}</div>
                    <div className="text-white font-semibold">{typeof v === 'number' ? v.toFixed(0) : v}</div>
                  </div>
                ))}
              </div>
              <div>
                <div className="text-slate-500 text-xs mb-1">Why it matters</div>
                <p className="text-slate-300">{selected.why_it_matters}</p>
              </div>
              {selected.token_narrative_opportunities?.length > 0 && (
                <div>
                  <div className="text-slate-500 text-xs mb-1">Token Opportunities</div>
                  <ul className="space-y-1">
                    {selected.token_narrative_opportunities.map((o, i) => (
                      <li key={i} className="text-slate-300 text-xs">• {o}</li>
                    ))}
                  </ul>
                </div>
              )}
              <button onClick={() => sendToAgent(selected.id)} className="btn-primary w-full flex items-center justify-center gap-1.5">
                <Send className="w-3.5 h-3.5" /> Send to Token Agent
              </button>
            </div>
          ) : (
            <div className="text-slate-500 text-sm text-center py-8">Click a trend to see details</div>
          )}
        </div>
      </div>
    </div>
  )
}
