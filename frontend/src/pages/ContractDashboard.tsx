import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { ContractSpec } from '../types'
import { Code2, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

export default function ContractDashboard() {
  const [contracts, setContracts] = useState<ContractSpec[]>([])
  const [selected, setSelected] = useState<ContractSpec | null>(null)
  const [tab, setTab] = useState<'overview' | 'code' | 'deploy' | 'tests' | 'audit'>('overview')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.contracts.list().then((d: any) => {
      setContracts(d.contracts || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <h1 className="text-xl font-bold flex items-center gap-2">
        <Code2 className="text-cyan-400 w-5 h-5" /> Smart Contract Dashboard
      </h1>

      <div className="card border-red-500/20 bg-red-500/5 flex items-start gap-3">
        <AlertTriangle className="text-red-400 w-5 h-5 mt-0.5 shrink-0" />
        <div>
          <p className="text-red-400 font-semibold text-sm">Mainnet deployment is blocked</p>
          <p className="text-slate-400 text-xs">All contracts are drafts. Requires: security audit + human founder approval before any mainnet deployment.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* List */}
        <div className="space-y-2">
          {loading ? <div className="text-slate-500 text-sm">Loading...</div>
            : contracts.length === 0 ? (
              <div className="card text-slate-500 text-sm space-y-2">
                <p>No contracts yet.</p>
                <p className="text-xs">Run: <code className="text-green-400">python cli/main.py prepare-contract [idea-id]</code></p>
              </div>
            ) : contracts.map(c => (
            <div
              key={c.id}
              onClick={() => setSelected(c)}
              className={clsx('card cursor-pointer hover:border-slate-600', selected?.id === c.id && 'border-cyan-500/50')}
            >
              <div className="font-bold text-white">{c.token_name}</div>
              <div className="text-green-400 text-xs">${c.ticker} · {c.standard} · {c.chain}</div>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400">mainnet blocked</span>
                <span className="text-xs text-slate-500">{c.deployment_status}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Detail */}
        <div className="xl:col-span-2">
          {selected ? (
            <div className="card space-y-4">
              <div className="flex gap-2 border-b border-slate-800 pb-3">
                {(['overview','code','deploy','tests','audit'] as const).map(t => (
                  <button
                    key={t}
                    onClick={() => setTab(t)}
                    className={clsx('text-xs px-3 py-1.5 rounded font-medium capitalize', tab === t ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:text-white')}
                  >
                    {t}
                  </button>
                ))}
              </div>

              {tab === 'overview' && (
                <div className="space-y-4 text-sm">
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      ['Token Name', selected.token_name],
                      ['Ticker', `$${selected.ticker}`],
                      ['Standard', selected.standard],
                      ['Chain', selected.chain],
                      ['Total Supply', selected.tokenomics.total_supply.toLocaleString()],
                      ['Status', selected.deployment_status],
                    ].map(([k, v]) => (
                      <div key={k} className="bg-slate-800 rounded p-2">
                        <div className="text-xs text-slate-500">{k}</div>
                        <div className="text-white font-semibold">{v}</div>
                      </div>
                    ))}
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-2">Tokenomics</div>
                    <div className="space-y-1.5">
                      {Object.entries(selected.tokenomics).filter(([k]) => k.endsWith('_pct')).map(([k, v]) => (
                        <div key={k} className="flex items-center gap-2">
                          <div className="text-xs text-slate-400 w-32">{k.replace('_pct','').replace('_',' ')}</div>
                          <div className="flex-1 bg-slate-800 rounded-full h-2">
                            <div className="h-2 rounded-full bg-green-500" style={{ width: `${v as number}%` }} />
                          </div>
                          <div className="text-xs text-slate-300 w-8 text-right">{v as number}%</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  {selected.warnings?.length > 0 && (
                    <div className="bg-yellow-500/10 border border-yellow-500/20 rounded p-3 space-y-1">
                      {selected.warnings.map((w, i) => (
                        <div key={i} className="text-xs text-yellow-300 flex items-start gap-1.5">
                          <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />{w}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {tab === 'code' && (
                <pre className="text-xs text-green-300 bg-slate-900 rounded p-4 overflow-x-auto max-h-96 font-mono leading-relaxed">
                  {selected.contract_code || 'No contract code generated yet.'}
                </pre>
              )}

              {tab === 'deploy' && (
                <pre className="text-xs text-blue-300 bg-slate-900 rounded p-4 overflow-x-auto max-h-96 font-mono leading-relaxed">
                  {selected.deploy_script || 'No deploy script generated yet.'}
                </pre>
              )}

              {tab === 'tests' && (
                <pre className="text-xs text-purple-300 bg-slate-900 rounded p-4 overflow-x-auto max-h-96 font-mono leading-relaxed">
                  {selected.test_script || 'No test script generated yet.'}
                </pre>
              )}

              {tab === 'audit' && (
                <div className="space-y-2">
                  {selected.audit_checklist?.map((item, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm">
                      <span className={clsx('text-xs mt-0.5', item.startsWith('[x]') ? 'text-green-400' : 'text-slate-500')}>
                        {item.startsWith('[x]') ? '✓' : '○'}
                      </span>
                      <span className="text-slate-300 text-xs">{item.replace(/^\[[ x]\] /, '')}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="card text-slate-500 text-sm text-center py-12">Select a contract to view details</div>
          )}
        </div>
      </div>
    </div>
  )
}
