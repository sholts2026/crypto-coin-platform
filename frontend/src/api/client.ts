const BASE = 'https://web-production-001a9b.up.railway.app/api'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`API ${res.status}: ${err}`)
  }
  return res.json()
}

const post = (path: string, body?: unknown) =>
  req(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined })

// Overview
export const api = {
  overview:      () => req('/overview'),
  agents:        () => req('/agents/status'),
  launchReadiness: () => req('/launch-readiness'),

  // Trends
  trends: {
    list:           (platform?: string, minScore?: number) =>
      req(`/trends${qs({ platform, min_score: minScore })}`),
    get:            (id: string) => req(`/trends/${id}`),
    collect:        (mock = true) => post(`/trends/collect?use_mock=${mock}`),
    sendToAgent:    (id: string) => post(`/trends/${id}/send-to-token-agent`),
  },

  // Token ideas
  tokens: {
    list:           (status?: string) => req(`/token-ideas${qs({ status })}`),
    get:            (id: string) => req(`/token-ideas/${id}`),
    approve:        (id: string, notes?: string) => post(`/token-ideas/${id}/approve`, { notes }),
    reject:         (id: string, notes?: string) => post(`/token-ideas/${id}/reject`, { notes }),
    revise:         (id: string, notes?: string) => post(`/token-ideas/${id}/revise`, { notes }),
    generate:       () => post('/token-ideas/generate'),
  },

  // CEO
  ceo: {
    decisions:      () => req('/ceo/decisions'),
    getDecision:    (id: string) => req(`/ceo/decisions/${id}`),
    approve:        (id: string) => post(`/ceo/decisions/${id}/approve`),
    revise:         (id: string) => post(`/ceo/decisions/${id}/revise`),
    run:            () => post('/ceo/run'),
    score:          () => post('/ceo/score'),
  },

  // Social
  social: {
    drafts:         (platform?: string, status?: string) =>
      req(`/social/drafts${qs({ platform, status })}`),
    getDraft:       (id: string) => req(`/social/drafts/${id}`),
    approveDraft:   (id: string) => post(`/social/drafts/${id}/approve`),
    rejectDraft:    (id: string) => post(`/social/drafts/${id}/reject`),
    markPublished:  (id: string) => post(`/social/drafts/${id}/mark-published`),
    generate:       (ideaId?: string) =>
      post(`/social/generate${ideaId ? `?token_idea_id=${ideaId}` : ''}`),
    performance:    () => req('/social/performance'),
  },

  // Brand
  brand: {
    list:           () => req('/brand'),
    get:            (id: string) => req(`/brand/${id}`),
    approve:        (id: string) => post(`/brand/${id}/approve`),
    reject:         (id: string) => post(`/brand/${id}/reject`),
    generate:       () => post('/brand/generate'),
  },

  // Risk
  risk: {
    list:           () => req('/risk'),
    summary:        () => req('/risk/summary'),
    run:            () => post('/risk/run'),
  },

  // Contracts
  contracts: {
    list:           () => req('/contracts'),
    get:            (id: string) => req(`/contracts/${id}`),
    generate:       (ideaId: string, chain = 'ethereum') =>
      post(`/contracts/generate?token_idea_id=${ideaId}&chain=${chain}`),
  },

  // Reports
  reports: {
    get:            () => req('/reports'),
    markdown:       () => fetch('/api/reports/markdown').then(r => r.text()),
    export:         (format: string) => post(`/reports/export?format=${format}`),
  },
}

function qs(params: Record<string, unknown>): string {
  const parts = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`)
  return parts.length ? '?' + parts.join('&') : ''
}
