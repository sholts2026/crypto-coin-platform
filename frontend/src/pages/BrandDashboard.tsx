import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { BrandPackage } from '../types'
import { Palette, Check, X, RefreshCw } from 'lucide-react'
import clsx from 'clsx'

export default function BrandDashboard() {
  const [brands, setBrands] = useState<BrandPackage[]>([])
  const [selected, setSelected] = useState<BrandPackage | null>(null)
  const [loading, setLoading] = useState(true)
  const [acting, setActing] = useState(false)

  const load = () => {
    setLoading(true)
    api.brand.list().then((d: any) => { setBrands(d.brands || []); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const generate = async () => { setActing(true); await api.brand.generate(); load(); setActing(false) }
  const approve  = async (id: string) => { await api.brand.approve(id); load() }
  const reject   = async (id: string) => { await api.brand.reject(id); load() }

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Palette className="text-pink-400 w-5 h-5" /> Brand Dashboard
        </h1>
        <button onClick={generate} disabled={acting} className="btn-primary flex items-center gap-1.5">
          <RefreshCw className={clsx('w-3.5 h-3.5', acting && 'animate-spin')} /> Generate Brands
        </button>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* List */}
        <div className="space-y-2">
          {loading ? <div className="text-slate-500 text-sm">Loading...</div>
            : brands.length === 0 ? <div className="card text-slate-500 text-sm">No brand packages yet.</div>
            : brands.map(b => (
            <div
              key={b.id}
              onClick={() => setSelected(b)}
              className={clsx('card cursor-pointer hover:border-slate-600', selected?.id === b.id && 'border-pink-500/50')}
            >
              <div className="flex justify-between items-start">
                <div className="font-bold text-white">{b.token_name_options?.[0] ?? 'Brand Package'}</div>
                <span className={clsx('text-xs px-2 py-0.5 rounded-full', b.approval_status === 'approved' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400')}>
                  {b.approval_status}
                </span>
              </div>
              <div className="text-slate-400 text-xs mt-1">{b.slogans?.[0]}</div>
            </div>
          ))}
        </div>

        {/* Detail */}
        <div className="xl:col-span-2">
          {selected ? (
            <div className="card space-y-4 text-sm">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-white">{selected.token_name_options?.[0]}</h2>
                  <div className="text-slate-400 text-xs">Brand Package {selected.id}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => approve(selected.id)} className="btn-primary flex items-center gap-1"><Check className="w-3.5 h-3.5" />Approve</button>
                  <button onClick={() => reject(selected.id)} className="btn-danger flex items-center gap-1"><X className="w-3.5 h-3.5" />Reject</button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-slate-500 text-xs mb-1">Name Options</div>
                  {selected.token_name_options?.map((n, i) => <div key={i} className="text-slate-300 text-xs">• {n}</div>)}
                </div>
                <div>
                  <div className="text-slate-500 text-xs mb-1">Ticker Options</div>
                  {selected.ticker_options?.map((t, i) => <div key={i} className="text-green-400 text-xs font-mono">• ${t}</div>)}
                </div>
              </div>

              <div>
                <div className="text-slate-500 text-xs mb-1">Slogans</div>
                <div className="space-y-1">
                  {selected.slogans?.map((s, i) => <div key={i} className="text-slate-300 italic text-xs">"{s}"</div>)}
                </div>
              </div>

              <div>
                <div className="text-slate-500 text-xs mb-1">Tone of Voice</div>
                <p className="text-slate-300 text-xs">{selected.tone_of_voice}</p>
              </div>

              <div>
                <div className="text-slate-500 text-xs mb-1">Visual Direction</div>
                <p className="text-slate-300 text-xs">{selected.visual_direction}</p>
              </div>

              {selected.manifesto && (
                <div>
                  <div className="text-slate-500 text-xs mb-1">Manifesto</div>
                  <div className="bg-slate-800 rounded p-3">
                    <pre className="text-xs text-slate-300 whitespace-pre-wrap font-sans">{selected.manifesto}</pre>
                  </div>
                </div>
              )}

              {selected.meme_language?.length > 0 && (
                <div>
                  <div className="text-slate-500 text-xs mb-1">Meme Language</div>
                  <div className="flex flex-wrap gap-2">
                    {selected.meme_language.map((m, i) => (
                      <span key={i} className="text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded">{m}</span>
                    ))}
                  </div>
                </div>
              )}

              {selected.logo_prompts?.length > 0 && (
                <div>
                  <div className="text-slate-500 text-xs mb-1">Logo Prompts (for AI image generation)</div>
                  <div className="space-y-1">
                    {selected.logo_prompts.map((p, i) => (
                      <div key={i} className="text-xs text-blue-300 bg-blue-500/10 rounded p-2 italic">{p}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="card text-slate-500 text-sm text-center py-12">Select a brand package to view details</div>
          )}
        </div>
      </div>
    </div>
  )
}
