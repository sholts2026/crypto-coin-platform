import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Download, FileText, RefreshCw } from 'lucide-react'

export default function ReportsCenter() {
  const [report, setReport] = useState<any>(null)
  const [mdContent, setMdContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)

  const load = () => {
    setLoading(true)
    api.reports.get().then(d => { setReport(d); setLoading(false) }).catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const exportMarkdown = async () => {
    setExporting(true)
    const md = await api.reports.markdown()
    setMdContent(md)
    setExporting(false)
  }

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'launch_report.json'; a.click()
    URL.revokeObjectURL(url)
  }

  const downloadMd = async () => {
    const md = await api.reports.markdown()
    const blob = new Blob([md], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'launch_report.md'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold flex items-center gap-2">
          <Download className="text-slate-400 w-5 h-5" /> Reports Center
        </h1>
        <div className="flex gap-2">
          <button onClick={load} className="btn-ghost flex items-center gap-1.5">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
          <button onClick={downloadJson} className="btn-ghost flex items-center gap-1.5">
            <Download className="w-3.5 h-3.5" /> JSON
          </button>
          <button onClick={downloadMd} className="btn-primary flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5" /> Markdown
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-slate-400 text-sm">Loading report...</div>
      ) : !report ? (
        <div className="card text-slate-500 text-sm">No report data. Run pipeline first.</div>
      ) : (
        <div className="space-y-4">
          {/* Summary */}
          <div className="card">
            <h2 className="text-sm font-semibold text-slate-300 mb-3">Report Summary</h2>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
              {Object.entries(report.summary || {}).map(([k, v]) => (
                <div key={k} className="bg-slate-800 rounded p-3 text-center">
                  <div className="text-lg font-bold text-white">{String(v)}</div>
                  <div className="text-xs text-slate-500">{k.replace(/_/g, ' ')}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Top token ideas */}
          {report.top_token_ideas?.length > 0 && (
            <div className="card">
              <h2 className="text-sm font-semibold text-slate-300 mb-3">Top Token Opportunities</h2>
              <div className="space-y-3">
                {report.top_token_ideas.map((idea: any, i: number) => (
                  <div key={idea.id} className="flex items-start gap-3 border-b border-slate-800 pb-3 last:border-0">
                    <span className="text-slate-500 font-bold text-sm w-4 shrink-0">#{i+1}</span>
                    <div className="flex-1">
                      <div className="font-semibold text-white">{idea.token_name} <span className="text-green-400">${idea.ticker}</span></div>
                      <div className="text-xs text-slate-400 mt-0.5">{idea.one_line_narrative}</div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-green-400 font-bold text-sm">{(idea.opportunity_score || 0).toFixed(1)}</div>
                      <div className="text-xs text-slate-500">score</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* CEO decision */}
          {report.ceo_decision && (
            <div className="card">
              <h2 className="text-sm font-semibold text-slate-300 mb-2">CEO Decision</h2>
              <div className="flex items-center justify-between">
                <div className="font-bold text-white">{report.ceo_decision.recommended_token_name}</div>
                <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">
                  {report.ceo_decision.human_approval_status}
                </span>
              </div>
            </div>
          )}

          {/* Risk summary */}
          {report.risk_summary && (
            <div className="card">
              <h2 className="text-sm font-semibold text-slate-300 mb-2">Risk Summary</h2>
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div className="bg-slate-800 rounded p-2 text-center">
                  <div className="text-lg font-bold text-yellow-400">{report.risk_summary.avg_overall?.toFixed(1)}/10</div>
                  <div className="text-xs text-slate-500">Avg Risk</div>
                </div>
                <div className="bg-slate-800 rounded p-2 text-center">
                  <div className="text-lg font-bold text-red-400">{report.risk_summary.high_risk_items?.length || 0}</div>
                  <div className="text-xs text-slate-500">High Risk</div>
                </div>
                <div className="bg-slate-800 rounded p-2 text-center">
                  <div className="text-lg font-bold text-orange-400">{report.risk_summary.avg_ip?.toFixed(1)}/10</div>
                  <div className="text-xs text-slate-500">IP Risk</div>
                </div>
              </div>
            </div>
          )}

          {/* Markdown preview */}
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-slate-300">Markdown Report Preview</h2>
              <button onClick={exportMarkdown} disabled={exporting} className="btn-ghost text-xs flex items-center gap-1">
                <FileText className="w-3 h-3" /> {exporting ? 'Loading...' : 'Preview'}
              </button>
            </div>
            {mdContent ? (
              <pre className="text-xs text-slate-300 whitespace-pre-wrap font-sans bg-slate-900 rounded p-4 max-h-64 overflow-y-auto">
                {mdContent}
              </pre>
            ) : (
              <div className="text-slate-500 text-xs">Click Preview to load markdown</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
