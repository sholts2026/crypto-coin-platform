from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db.database import Base


class TrendModel(Base):
    __tablename__ = "trends"
    id:               Mapped[str]   = mapped_column(String, primary_key=True)
    phrase:           Mapped[str]   = mapped_column(String)
    source_platform:  Mapped[str]   = mapped_column(String)
    detected_at:      Mapped[str]   = mapped_column(String)
    velocity_score:   Mapped[float] = mapped_column(Float, default=0)
    novelty_score:    Mapped[float] = mapped_column(Float, default=0)
    meme_potential:   Mapped[float] = mapped_column(Float, default=0)
    crypto_relevance: Mapped[float] = mapped_column(Float, default=0)
    community_size:   Mapped[float] = mapped_column(Float, default=0)
    saturation_level: Mapped[float] = mapped_column(Float, default=0)
    expected_lifespan_days: Mapped[int] = mapped_column(Integer, default=14)
    composite_score:  Mapped[float] = mapped_column(Float, default=0)
    why_it_matters:   Mapped[str]   = mapped_column(Text, default="")
    related_communities: Mapped[list] = mapped_column(JSON, default=list)
    related_figures:  Mapped[list]  = mapped_column(JSON, default=list)
    token_narrative_opportunities: Mapped[list] = mapped_column(JSON, default=list)
    raw_data:         Mapped[dict]  = mapped_column(JSON, default=dict)


class TokenIdeaModel(Base):
    __tablename__ = "token_ideas"
    id:               Mapped[str]   = mapped_column(String, primary_key=True)
    token_name:       Mapped[str]   = mapped_column(String)
    ticker:           Mapped[str]   = mapped_column(String)
    one_line_narrative: Mapped[str] = mapped_column(Text, default="")
    target_community: Mapped[str]   = mapped_column(Text, default="")
    meme_angle:       Mapped[str]   = mapped_column(Text, default="")
    utility_angle:    Mapped[str]   = mapped_column(Text, default="")
    why_now:          Mapped[str]   = mapped_column(Text, default="")
    possible_risks:   Mapped[list]  = mapped_column(JSON, default=list)
    virality_score:   Mapped[float] = mapped_column(Float, default=0)
    launch_readiness_score: Mapped[float] = mapped_column(Float, default=0)
    meme_potential:   Mapped[float] = mapped_column(Float, default=0)
    community_potential: Mapped[float] = mapped_column(Float, default=0)
    novelty:          Mapped[float] = mapped_column(Float, default=0)
    timing:           Mapped[float] = mapped_column(Float, default=0)
    technical_feasibility: Mapped[float] = mapped_column(Float, default=80)
    brand_strength:   Mapped[float] = mapped_column(Float, default=0)
    source_trend_id:  Mapped[str]   = mapped_column(String, nullable=True)
    created_at:       Mapped[str]   = mapped_column(String)
    approval_status:  Mapped[str]   = mapped_column(String, default="pending")
    ceo_notes:        Mapped[str]   = mapped_column(Text, default="")


class RiskReviewModel(Base):
    __tablename__ = "risk_reviews"
    id:                   Mapped[str]   = mapped_column(String, primary_key=True)
    subject_id:           Mapped[str]   = mapped_column(String, index=True)
    subject_type:         Mapped[str]   = mapped_column(String, default="token_concept")
    token_risk_score:     Mapped[float] = mapped_column(Float, default=5)
    marketing_risk_score: Mapped[float] = mapped_column(Float, default=5)
    ip_trademark_risk:    Mapped[float] = mapped_column(Float, default=5)
    platform_risk:        Mapped[float] = mapped_column(Float, default=3)
    reputational_risk:    Mapped[float] = mapped_column(Float, default=3)
    technical_risk:       Mapped[float] = mapped_column(Float, default=2)
    overall_risk_score:   Mapped[float] = mapped_column(Float, default=5)
    flagged_phrases:      Mapped[list]  = mapped_column(JSON, default=list)
    flagged_claims:       Mapped[list]  = mapped_column(JSON, default=list)
    weak_narratives:      Mapped[list]  = mapped_column(JSON, default=list)
    required_reviews:     Mapped[list]  = mapped_column(JSON, default=list)
    suggested_revisions:  Mapped[list]  = mapped_column(JSON, default=list)
    reviewed_at:          Mapped[str]   = mapped_column(String)
    reviewer_agent:       Mapped[str]   = mapped_column(String, default="risk_review_agent")


class SocialDraftModel(Base):
    __tablename__ = "social_drafts"
    id:                   Mapped[str]   = mapped_column(String, primary_key=True)
    token_idea_id:        Mapped[str]   = mapped_column(String, index=True)
    platform:             Mapped[str]   = mapped_column(String)
    post_type:            Mapped[str]   = mapped_column(String)
    text:                 Mapped[str]   = mapped_column(Text)
    media_prompt:         Mapped[str]   = mapped_column(Text, default="")
    target_audience:      Mapped[str]   = mapped_column(String, default="")
    expected_goal:        Mapped[str]   = mapped_column(String, default="")
    suggested_publish_time: Mapped[str] = mapped_column(String, nullable=True)
    risk_flags:           Mapped[list]  = mapped_column(JSON, default=list)
    approval_status:      Mapped[str]   = mapped_column(String, default="pending")
    created_at:           Mapped[str]   = mapped_column(String)
    published_at:         Mapped[str]   = mapped_column(String, nullable=True)


class BrandPackageModel(Base):
    __tablename__ = "brand_packages"
    id:                   Mapped[str]   = mapped_column(String, primary_key=True)
    token_idea_id:        Mapped[str]   = mapped_column(String, index=True)
    token_name_options:   Mapped[list]  = mapped_column(JSON, default=list)
    ticker_options:       Mapped[list]  = mapped_column(JSON, default=list)
    slogans:              Mapped[list]  = mapped_column(JSON, default=list)
    tone_of_voice:        Mapped[str]   = mapped_column(Text, default="")
    visual_direction:     Mapped[str]   = mapped_column(Text, default="")
    logo_prompts:         Mapped[list]  = mapped_column(JSON, default=list)
    website_copy:         Mapped[dict]  = mapped_column(JSON, default=dict)
    landing_page_structure: Mapped[list] = mapped_column(JSON, default=list)
    whitepaper_lite:      Mapped[str]   = mapped_column(Text, default="")
    manifesto:            Mapped[str]   = mapped_column(Text, default="")
    meme_language:        Mapped[list]  = mapped_column(JSON, default=list)
    brand_consistency_guide: Mapped[str] = mapped_column(Text, default="")
    created_at:           Mapped[str]   = mapped_column(String)
    approval_status:      Mapped[str]   = mapped_column(String, default="pending")


class DecisionModel(Base):
    __tablename__ = "decisions"
    id:                       Mapped[str]   = mapped_column(String, primary_key=True)
    recommended_token_id:     Mapped[str]   = mapped_column(String)
    recommended_token_name:   Mapped[str]   = mapped_column(String)
    selection_reasons:        Mapped[list]  = mapped_column(JSON, default=list)
    rejected_alternatives:    Mapped[list]  = mapped_column(JSON, default=list)
    score_breakdown:          Mapped[dict]  = mapped_column(JSON, default=dict)
    risks_considered:         Mapped[list]  = mapped_column(JSON, default=list)
    required_next_actions:    Mapped[list]  = mapped_column(JSON, default=list)
    launch_checklist_status:  Mapped[dict]  = mapped_column(JSON, default=dict)
    human_approval_status:    Mapped[str]   = mapped_column(String, default="pending")
    decided_at:               Mapped[str]   = mapped_column(String)
    summary_report:           Mapped[str]   = mapped_column(Text, default="")


class ContractModel(Base):
    __tablename__ = "contracts"
    id:                Mapped[str]  = mapped_column(String, primary_key=True)
    token_idea_id:     Mapped[str]  = mapped_column(String, index=True)
    chain:             Mapped[str]  = mapped_column(String, default="ethereum")
    standard:          Mapped[str]  = mapped_column(String, default="ERC-20")
    token_name:        Mapped[str]  = mapped_column(String)
    ticker:            Mapped[str]  = mapped_column(String)
    tokenomics:        Mapped[dict] = mapped_column(JSON, default=dict)
    contract_code:     Mapped[str]  = mapped_column(Text, default="")
    deploy_script:     Mapped[str]  = mapped_column(Text, default="")
    test_script:       Mapped[str]  = mapped_column(Text, default="")
    audit_checklist:   Mapped[list] = mapped_column(JSON, default=list)
    deployment_status: Mapped[str]  = mapped_column(String, default="not_deployed")
    mainnet_blocked:   Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:        Mapped[str]  = mapped_column(String)
    warnings:          Mapped[list] = mapped_column(JSON, default=list)


class ScoreModel(Base):
    __tablename__ = "scores"
    token_idea_id:          Mapped[str]   = mapped_column(String, primary_key=True)
    trend_strength:         Mapped[float] = mapped_column(Float, default=0)
    meme_potential:         Mapped[float] = mapped_column(Float, default=0)
    community_potential:    Mapped[float] = mapped_column(Float, default=0)
    novelty:                Mapped[float] = mapped_column(Float, default=0)
    timing:                 Mapped[float] = mapped_column(Float, default=0)
    technical_feasibility:  Mapped[float] = mapped_column(Float, default=0)
    brand_strength:         Mapped[float] = mapped_column(Float, default=0)
    risk_score:             Mapped[float] = mapped_column(Float, default=50)
    final_opportunity_score: Mapped[float] = mapped_column(Float, default=0)
    calculated_at:          Mapped[str]   = mapped_column(String)
