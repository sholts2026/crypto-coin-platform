import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { BarChart2, Link } from 'lucide-react'

export default function SocialPerformance() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    api.social.performance().then(setData).catch(() => {})
  }, [])

  if (!data) return <div className="p-6 text-slate-400">Loading...</div>

  return (
    <div className="p-6 max-w-screen-xl space-y-5">
      <h1 className="text-xl font-bold flex items-center gap-2">
        <BarChart2 className="text-purple-400 w-5 h-5" /> Social Performance
      </h1>

      <div className="card border-yellow-500/20 bg-yellow-500/5">
        <p className="text-yellow-400 text-sm font-semibold">Connect Real Accounts</p>
        <p className="text-slate-400 text-xs mt-1">
          Social performance tracking requires connecting real accounts via API keys in <code className="text-green-400">.env</code>.
          Only real organic data is tracked. No fake engagement.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {data.platforms?.map((p: any) => (
          <div key={p.platform} className="card">
            <div className="flex items-center justify-between mb-3">
              <span className="font-semibold text-white capitalize">{p.platform}</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-400">{p.status}</span>
            </div>
            {p.status === 'not_connected' ? (
              <div className="text-slate-500 text-xs">
                <p>Not connected.</p>
                <p className="mt-1">Add API keys to <code className="text-green-400">.env</code> to connect.</p>
              </div>
            ) : (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between text-slate-400">
                  <span>Followers</span><span className="text-white">{p.followers?.toLocaleString() ?? 0}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Impressions 7d</span><span className="text-white">{p.impressions_7d?.toLocaleString() ?? 0}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Engagement</span><span className="text-white">{p.engagement_rate ?? 0}%</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Drafts Pending</div>
          <div className="text-2xl font-bold text-yellow-400">{data.drafts_pending}</div>
        </div>
        <div className="card">
          <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Drafts Approved</div>
          <div className="text-2xl font-bold text-green-400">{data.drafts_approved}</div>
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <Link className="w-4 h-4 text-blue-400" /> API Connection Guide
        </h3>
        <div className="space-y-2 text-xs text-slate-400">
          <p><span className="text-white font-semibold">Twitter/X:</span> Add TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET to .env</p>
          <p><span className="text-white font-semibold">Reddit:</span> Add REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD</p>
          <p><span className="text-white font-semibold">YouTube:</span> Add YOUTUBE_API_KEY</p>
          <p><span className="text-white font-semibold">Telegram:</span> Connect bot via Telegram Bot API</p>
          <p><span className="text-white font-semibold">TikTok:</span> Add TIKTOK_SESSION_ID (requires TikTok for Business API access)</p>
        </div>
      </div>
    </div>
  )
}
