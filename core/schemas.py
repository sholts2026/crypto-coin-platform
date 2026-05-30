from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


# ── Enums ──────────────────────────────────────────────────────────────────────

class ApprovalStatus(str, Enum):
    PENDING   = "pending"
    APPROVED  = "approved"
    REJECTED  = "rejected"
    REVISION  = "needs_revision"

class Platform(str, Enum):
    TWITTER  = "twitter"
    REDDIT   = "reddit"
    TIKTOK   = "tiktok"
    YOUTUBE  = "youtube"
    TELEGRAM = "telegram"
    DISCORD  = "discord"
    GOOGLE   = "google_trends"
    CRYPTO   = "crypto_news"
    FARCASTER = "farcaster"

class Chain(str, Enum):
    ETHEREUM = "ethereum"
    BASE     = "base"
    SOLANA   = "solana"

class PostType(str, Enum):
    ANNOUNCEMENT = "announcement"
    MEME         = "meme"
    THREAD       = "thread"
    POLL         = "poll"
    FAQ          = "faq"
    EDUCATIONAL  = "educational"
    AMA          = "ama"


# ── Trend ─────────────────────────────────────────────────────────────────────

class Trend(BaseModel):
    id: str
    phrase: str
    source_platform: Platform
    detected_at: datetime
    velocity_score: float = Field(ge=0, le=100)
    novelty_score: float = Field(ge=0, le=100)
    meme_potential: float = Field(ge=0, le=100)
    crypto_relevance: float = Field(ge=0, le=100)
    community_size: float = Field(ge=0, le=100)
    saturation_level: float = Field(ge=0, le=100)
    expected_lifespan_days: int
    related_communities: List[str] = []
    related_figures: List[str] = []
    why_it_matters: str
    token_narrative_opportunities: List[str] = []
    raw_data: Dict[str, Any] = {}


# ── Token Concept ─────────────────────────────────────────────────────────────

class TokenConceptCard(BaseModel):
    id: str
    token_name: str
    ticker: str
    one_line_narrative: str
    target_community: str
    meme_angle: str
    utility_angle: str
    why_now: str
    possible_risks: List[str] = []
    virality_score: float = Field(ge=0, le=100)
    launch_readiness_score: float = Field(ge=0, le=100)
    source_trend_id: Optional[str] = None
    created_at: datetime
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    ceo_notes: str = ""


# ── Opportunity Scores ─────────────────────────────────────────────────────────

class OpportunityScore(BaseModel):
    token_idea_id: str
    trend_strength: float = Field(ge=0, le=100)
    meme_potential: float = Field(ge=0, le=100)
    community_potential: float = Field(ge=0, le=100)
    novelty: float = Field(ge=0, le=100)
    timing: float = Field(ge=0, le=100)
    technical_feasibility: float = Field(ge=0, le=100)
    brand_strength: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    final_opportunity_score: float = 0.0
    calculated_at: datetime


# ── Tokenomics ────────────────────────────────────────────────────────────────

class Tokenomics(BaseModel):
    total_supply: int = 1_000_000_000
    decimals: int = 18
    treasury_pct: float = 10.0
    liquidity_pct: float = 40.0
    community_pct: float = 30.0
    team_pct: float = 10.0
    marketing_pct: float = 10.0
    vesting_schedule: Dict[str, str] = {
        "team": "12 months cliff, 24 months linear vesting",
        "treasury": "locked 6 months, then governance-controlled",
        "marketing": "no lock, spend as needed",
    }


# ── Contract ──────────────────────────────────────────────────────────────────

class ContractSpec(BaseModel):
    id: str
    token_idea_id: str
    chain: Chain = Chain.ETHEREUM
    standard: str = "ERC-20"
    token_name: str
    ticker: str
    tokenomics: Tokenomics
    contract_code: str = ""
    deploy_script: str = ""
    test_script: str = ""
    audit_checklist: List[str] = []
    deployment_status: str = "not_deployed"
    mainnet_blocked: bool = True
    created_at: datetime
    warnings: List[str] = []


# ── Brand Package ─────────────────────────────────────────────────────────────

class BrandPackage(BaseModel):
    id: str
    token_idea_id: str
    token_name_options: List[str] = []
    ticker_options: List[str] = []
    slogans: List[str] = []
    tone_of_voice: str
    visual_direction: str
    logo_prompts: List[str] = []
    website_copy: Dict[str, str] = {}
    landing_page_structure: List[str] = []
    whitepaper_lite: str = ""
    manifesto: str = ""
    meme_language: List[str] = []
    brand_consistency_guide: str = ""
    created_at: datetime
    approval_status: ApprovalStatus = ApprovalStatus.PENDING


# ── Social Draft ──────────────────────────────────────────────────────────────

class SocialDraft(BaseModel):
    id: str
    token_idea_id: str
    platform: Platform
    post_type: PostType
    text: str
    media_prompt: str = ""
    target_audience: str
    expected_goal: str
    suggested_publish_time: Optional[datetime] = None
    risk_flags: List[str] = []
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime
    published_at: Optional[datetime] = None


# ── Risk Review ───────────────────────────────────────────────────────────────

class RiskReview(BaseModel):
    id: str
    subject_id: str
    subject_type: str
    token_risk_score: float = Field(ge=0, le=10)
    marketing_risk_score: float = Field(ge=0, le=10)
    ip_trademark_risk: float = Field(ge=0, le=10)
    platform_risk: float = Field(ge=0, le=10)
    reputational_risk: float = Field(ge=0, le=10)
    technical_risk: float = Field(ge=0, le=10)
    overall_risk_score: float = Field(ge=0, le=10)
    flagged_phrases: List[str] = []
    flagged_claims: List[str] = []
    weak_narratives: List[str] = []
    required_reviews: List[str] = []
    suggested_revisions: List[str] = []
    reviewed_at: datetime
    reviewer_agent: str = "risk_review_agent"


# ── CEO Decision ──────────────────────────────────────────────────────────────

class CEODecision(BaseModel):
    id: str
    recommended_token_id: str
    recommended_token_name: str
    selection_reasons: List[str] = []
    rejected_alternatives: List[Dict[str, Any]] = []
    score_breakdown: Dict[str, float] = {}
    risks_considered: List[str] = []
    required_next_actions: List[str] = []
    launch_checklist_status: Dict[str, bool] = {}
    human_approval_status: ApprovalStatus = ApprovalStatus.PENDING
    decided_at: datetime
    summary_report: str = ""


# ── Agent Output wrapper ──────────────────────────────────────────────────────

class AgentOutput(BaseModel):
    timestamp: datetime
    agent_name: str
    input_summary: str
    output: Any
    score: Optional[float] = None
    next_recommended_action: str = ""


# ── Launch Readiness ──────────────────────────────────────────────────────────

class LaunchChecklist(BaseModel):
    trend_validated: bool = False
    token_concept_approved: bool = False
    brand_package_approved: bool = False
    risk_review_completed: bool = False
    social_infrastructure_prepared: bool = False
    first_content_calendar_ready: bool = False
    community_channels_ready: bool = False
    smart_contract_generated: bool = False
    smart_contract_tests_passed: bool = False
    tokenomics_reviewed: bool = False
    launch_report_generated: bool = False
    human_approval_received: bool = False

    @property
    def readiness_pct(self) -> float:
        fields = list(self.model_fields.keys())
        done = sum(1 for f in fields if getattr(self, f))
        return round(done / len(fields) * 100, 1)

    @property
    def blockers(self) -> list[str]:
        return [f for f in self.model_fields if not getattr(self, f)]
