export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'needs_revision'

export interface Trend {
  id: string
  phrase: string
  source_platform: string
  detected_at: string
  velocity_score: number
  novelty_score: number
  meme_potential: number
  crypto_relevance: number
  community_size: number
  saturation_level: number
  expected_lifespan_days: number
  composite_score: number
  why_it_matters: string
  related_communities: string[]
  related_figures: string[]
  token_narrative_opportunities: string[]
}

export interface TokenIdea {
  id: string
  token_name: string
  ticker: string
  one_line_narrative: string
  target_community: string
  meme_angle: string
  utility_angle: string
  why_now: string
  possible_risks: string[]
  virality_score: number
  launch_readiness_score: number
  meme_potential: number
  community_potential: number
  novelty: number
  timing: number
  technical_feasibility: number
  brand_strength: number
  source_trend_id: string | null
  created_at: string
  approval_status: ApprovalStatus
  ceo_notes: string
  opportunity_score?: number
  risk_score?: number
}

export interface RiskReview {
  id: string
  subject_id: string
  subject_type: string
  token_risk_score: number
  marketing_risk_score: number
  ip_trademark_risk: number
  platform_risk: number
  reputational_risk: number
  technical_risk: number
  overall_risk_score: number
  flagged_phrases: string[]
  flagged_claims: string[]
  weak_narratives: string[]
  required_reviews: string[]
  suggested_revisions: string[]
  reviewed_at: string
}

export interface SocialDraft {
  id: string
  token_idea_id: string
  platform: string
  post_type: string
  text: string
  media_prompt: string
  target_audience: string
  expected_goal: string
  suggested_publish_time: string | null
  risk_flags: string[]
  approval_status: ApprovalStatus
  created_at: string
  published_at: string | null
}

export interface BrandPackage {
  id: string
  token_idea_id: string
  token_name_options: string[]
  ticker_options: string[]
  slogans: string[]
  tone_of_voice: string
  visual_direction: string
  logo_prompts: string[]
  website_copy: Record<string, string>
  landing_page_structure: string[]
  whitepaper_lite: string
  manifesto: string
  meme_language: string[]
  brand_consistency_guide: string
  created_at: string
  approval_status: ApprovalStatus
}

export interface CEODecision {
  id: string
  recommended_token_id: string
  recommended_token_name: string
  selection_reasons: string[]
  rejected_alternatives: Array<{ id: string; name: string; score: number; reason: string }>
  score_breakdown: Record<string, number>
  risks_considered: string[]
  required_next_actions: string[]
  launch_checklist_status: Record<string, boolean>
  human_approval_status: ApprovalStatus
  decided_at: string
  summary_report: string
}

export interface ContractSpec {
  id: string
  token_idea_id: string
  chain: string
  standard: string
  token_name: string
  ticker: string
  tokenomics: {
    total_supply: number
    liquidity_pct: number
    community_pct: number
    treasury_pct: number
    team_pct: number
    marketing_pct: number
  }
  contract_code: string
  deploy_script: string
  test_script: string
  audit_checklist: string[]
  deployment_status: string
  mainnet_blocked: boolean
  created_at: string
  warnings: string[]
}

export interface AgentStatus {
  agent_name: string
  current_task: string
  last_run_time: string | null
  last_output_count: number
  status: string
  errors: string[]
  warnings: string[]
}

export interface LaunchReadiness {
  readiness_pct: number
  checklist: Record<string, boolean>
  blockers: string[]
  warnings: string[]
  next_action: string
  done_count: number
  total_count: number
}

export interface Overview {
  top_trending_narratives: string[]
  best_token_opportunity: string | null
  best_opportunity_ticker: string | null
  launch_readiness_score: number
  total_token_ideas: number
  total_social_drafts: number
  total_risk_warnings: number
  total_trends_detected: number
  total_decisions: number
  system_status: string
  next_recommended_action: string
  ceo_recommendation: string | null
}
