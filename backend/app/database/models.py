import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    brain_connections = relationship("BrainConnection", back_populates="user", cascade="all, delete-orphan")


class BrainConnection(Base):
    __tablename__ = "brain_connections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    email = Column(String(255), nullable=False)
    encrypted_password = Column(Text, nullable=False)
    environment = Column(String(50), default="PROD")  # PROD, STAGING, SIMULATION
    status = Column(String(50), default="DISCONNECTED")  # CONNECTED, DISCONNECTED, ERROR
    last_tested_at = Column(DateTime, nullable=True)
    last_status_code = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="brain_connections")
    sessions = relationship("BrainSession", back_populates="connection", cascade="all, delete-orphan")


class BrainSession(Base):
    __tablename__ = "brain_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    connection_id = Column(String(36), ForeignKey("brain_connections.id"), nullable=False)
    encrypted_session_cookie = Column(Text, nullable=True)
    encrypted_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)

    connection = relationship("BrainConnection", back_populates="sessions")


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    target_sharpe = Column(Float, default=1.25)
    target_fitness = Column(Float, default=1.00)
    max_turnover = Column(Float, default=0.70)
    min_margin_bps = Column(Float, default=4.00)
    created_at = Column(DateTime, default=get_utc_now)


class ResearchFamily(Base):
    __tablename__ = "research_families"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False)  # MOMENTUM, MEAN_REVERSION, VALUE, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    core_hypothesis = Column(Text, nullable=False)
    preferred_fields = Column(JSON, default=list)
    allowed_fields = Column(JSON, default=list)
    preferred_operators = Column(JSON, default=list)
    discouraged_operators = Column(JSON, default=list)
    temporal_behavior = Column(String(50), default="MEDIUM")
    expected_horizon = Column(String(50), default="10-60d")
    expected_turnover = Column(String(50), default="LOW-MED")
    complexity_range = Column(String(50), default="LOW-MED")
    neutralization_options = Column(JSON, default=list)
    templates = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)


class Field(Base):
    __tablename__ = "fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), default="OTHER")  # PRICE, VOLUME, FUNDAMENTAL, ESTIMATE, QUALITY, VOLATILITY, LIQUIDITY, OTHER
    temporal_behavior = Column(String(50), default="UNKNOWN")  # FAST, MEDIUM, SLOW, EVENT_DRIVEN, UNKNOWN
    typical_frequency = Column(String(50), default="DAILY")
    supported_families = Column(JSON, default=list)
    preferred_operators = Column(JSON, default=list)
    discouraged_operators = Column(JSON, default=list)
    recommended_horizons = Column(JSON, default=list)
    data_quality = Column(Float, default=1.0)
    notes = Column(Text, nullable=True)


class Operator(Base):
    __tablename__ = "operators"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), default="TRANSFORMATION")  # TS, CS, GROUP, MATH, LOGICAL
    arity = Column(Integer, default=1)
    accepted_arg_types = Column(JSON, default=list)
    temporal_requirements = Column(String(50), default="NONE")
    lookback_requirements = Column(String(50), default="OPTIONAL")
    constant_signal_risk = Column(String(50), default="LOW")
    complexity_cost = Column(Float, default=1.0)


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    family_code = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    rationale = Column(Text, nullable=False)
    expected_market_regime = Column(String(100), default="ALL")
    suggested_fields = Column(JSON, default=list)
    suggested_operators = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)


class AlphaCandidate(Base):
    __tablename__ = "alpha_candidates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    expression = Column(Text, nullable=False)
    expression_hash = Column(String(64), index=True, nullable=False)
    structure_hash = Column(String(64), index=True, nullable=False)
    family_code = Column(String(50), nullable=False)
    hypothesis_id = Column(String(36), nullable=True)
    
    # AST Metadata
    fields_used = Column(JSON, default=list)
    operators_used = Column(JSON, default=list)
    complexity_score = Column(Float, default=1.0)
    operator_count = Column(Integer, default=1)
    nesting_depth = Column(Integer, default=1)

    # Preflight Status
    preflight_status = Column(String(50), default="PENDING")  # PASS, REJECT, REGENERATE, PENDING
    preflight_reason = Column(String(100), nullable=True)
    compatibility_score = Column(Float, default=1.0)
    constant_signal_risk = Column(Float, default=0.0)

    # Classification & Tiering
    tier = Column(String(50), default="TIER_1_PREFLIGHT_PENDING")
    is_pareto = Column(Boolean, default=False)
    pareto_rank = Column(Integer, nullable=True)
    priority_bucket = Column(String(50), default="PROVEN")  # PROVEN, EXPLORED, NOVEL

    # Lineage
    parent_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=True)
    mutation_type = Column(String(100), nullable=True)
    generation_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    simulations = relationship("Simulation", back_populates="candidate", cascade="all, delete-orphan")
    preflight_result = relationship("PreflightResult", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    research_score = relationship("ResearchScore", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    lineages = relationship("AlphaLineage", foreign_keys="AlphaLineage.candidate_id", back_populates="candidate", cascade="all, delete-orphan")


class AlphaLineage(Base):
    __tablename__ = "alpha_lineages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=True)
    mutation_type = Column(String(100), nullable=False)  # LOOKBACK_MUTATION, OPERATOR_SWAP, FIELD_SWAP, etc.
    changed_field = Column(String(100), nullable=True)
    changed_operator = Column(String(100), nullable=True)
    changed_lookback = Column(Integer, nullable=True)
    changed_group = Column(String(50), nullable=True)
    changed_transformation = Column(String(100), nullable=True)
    generation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    candidate = relationship("AlphaCandidate", foreign_keys=[candidate_id], back_populates="lineages")


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    brain_sim_id = Column(String(100), nullable=True, index=True)
    
    # State Machine: CREATED, PREFLIGHT, QUEUED, SUBMITTING, SUBMITTED, RUNNING,
    # COMPLETE, PORTFOLIO_EMPTY, METRICS_AVAILABLE, METRICS_MISSING, PARSE_ERROR,
    # SUBMISSION_ERROR, TIMEOUT, RATE_LIMITED, TECHNICAL_FAILURE, EVALUATED, REJECTED, PARETO, CANDIDATE_READY
    status = Column(String(50), default="CREATED")
    
    # Failure Separation: TECHNICAL_FAILURE vs ALPHA_FAILURE vs SUCCESS
    classification = Column(String(50), default="PENDING")
    
    # Sub-states
    portfolio_status = Column(String(50), default="UNKNOWN")  # VALID, EMPTY, UNKNOWN
    metrics_status = Column(String(50), default="UNKNOWN")    # AVAILABLE, MISSING, PARSE_ERROR, UNKNOWN

    # Settings payload used
    universe = Column(String(50), default="TOP3000")
    region = Column(String(50), default="USA")
    delay = Column(Integer, default=1)
    decay = Column(Integer, default=0)
    neutralization = Column(String(50), default="SUBINDUSTRY")
    truncation = Column(Float, default=0.08)
    pasteurization = Column(String(50), default="ON")
    language = Column(String(50), default="FASTEXPR")
    
    # Diagnostics & Telemetry
    remote_status = Column(String(50), nullable=True)
    diagnostic_code = Column(String(50), default="NONE")
    root_cause_type = Column(String(100), nullable=True)
    root_cause_confidence = Column(String(20), default="UNKNOWN")  # HIGH, MEDIUM, LOW, UNKNOWN
    position_count = Column(Integer, nullable=True)
    diagnostic_details = Column(JSON, default=dict)
    
    retry_count = Column(Integer, default=0)
    diagnostic_reason = Column(Text, nullable=True)
    possible_cause = Column(Text, nullable=True)
    raw_response = Column(JSON, nullable=True)
    
    submitted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    candidate = relationship("AlphaCandidate", back_populates="simulations")
    metrics = relationship("SimulationMetric", back_populates="simulation", uselist=False, cascade="all, delete-orphan")


class SimulationMetric(Base):
    __tablename__ = "simulation_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    simulation_id = Column(String(36), ForeignKey("simulations.id"), nullable=False)
    
    # True Metrics (NULL if unavailable, NEVER convert to 0)
    sharpe = Column(Float, nullable=True)
    fitness = Column(Float, nullable=True)
    turnover = Column(Float, nullable=True)
    margin_bps = Column(Float, nullable=True)
    returns_annualized = Column(Float, nullable=True)
    drawdown_max = Column(Float, nullable=True)
    long_count = Column(Integer, nullable=True)
    short_count = Column(Integer, nullable=True)
    correlation = Column(Float, nullable=True)
    
    # Diagnostics
    has_valid_metrics = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)

    simulation = relationship("Simulation", back_populates="metrics")


class PreflightResult(Base):
    __tablename__ = "preflight_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    decision = Column(String(50), default="PASS")  # PASS, REJECT, REGENERATE
    reason = Column(String(100), nullable=True)
    
    compatibility_score = Column(Float, default=1.0)
    constant_signal_risk = Column(Float, default=0.0)
    data_sufficiency = Column(Float, default=1.0)
    cross_sectional_variation = Column(Float, default=1.0)
    duplicate_risk = Column(Float, default=0.0)
    complexity_score = Column(Float, default=1.0)
    
    diagnostic_details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=get_utc_now)

    candidate = relationship("AlphaCandidate", back_populates="preflight_result")


class ResearchScore(Base):
    __tablename__ = "research_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    
    total_score = Column(Float, nullable=True)
    sharpe_component = Column(Float, nullable=True)
    fitness_component = Column(Float, nullable=True)
    turnover_component = Column(Float, nullable=True)
    stability_component = Column(Float, nullable=True)
    robustness_component = Column(Float, nullable=True)
    diversity_component = Column(Float, nullable=True)
    simplicity_component = Column(Float, nullable=True)
    complexity_penalty = Column(Float, default=0.0)
    
    is_target_passing = Column(Boolean, default=False)
    is_candidate_ready = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)

    candidate = relationship("AlphaCandidate", back_populates="research_score")


class ParetoResult(Base):
    __tablename__ = "pareto_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    is_pareto_optimal = Column(Boolean, default=False)
    pareto_rank = Column(Integer, default=1)
    dominance_count = Column(Integer, default=0)
    dominated_by_count = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=get_utc_now)


class WalkForwardResult(Base):
    __tablename__ = "walk_forward_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    in_sample_sharpe = Column(Float, nullable=True)
    out_of_sample_sharpe = Column(Float, nullable=True)
    degradation_ratio = Column(Float, nullable=True)
    stability_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)


class RobustnessResult(Base):
    __tablename__ = "robustness_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    parameter_sensitivity = Column(Float, nullable=True)
    universe_sensitivity = Column(Float, nullable=True)
    decay_sensitivity = Column(Float, nullable=True)
    neutralization_sensitivity = Column(Float, nullable=True)
    lookback_sensitivity = Column(Float, nullable=True)
    overall_robustness_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)


class FieldPerformance(Base):
    __tablename__ = "field_performances"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    field_name = Column(String(100), unique=True, nullable=False)
    total_candidates = Column(Integer, default=0)
    valid_simulations = Column(Integer, default=0)
    empty_portfolio_count = Column(Integer, default=0)
    avg_sharpe = Column(Float, nullable=True)
    avg_fitness = Column(Float, nullable=True)
    avg_turnover = Column(Float, nullable=True)
    avg_margin_bps = Column(Float, nullable=True)
    success_rate = Column(Float, default=0.0)
    empty_portfolio_rate = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class OperatorPerformance(Base):
    __tablename__ = "operator_performances"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    operator_name = Column(String(100), unique=True, nullable=False)
    total_candidates = Column(Integer, default=0)
    valid_simulations = Column(Integer, default=0)
    empty_portfolio_count = Column(Integer, default=0)
    avg_sharpe = Column(Float, nullable=True)
    avg_fitness = Column(Float, nullable=True)
    avg_turnover = Column(Float, nullable=True)
    avg_margin_bps = Column(Float, nullable=True)
    success_rate = Column(Float, default=0.0)
    empty_portfolio_rate = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class FamilyPerformance(Base):
    __tablename__ = "family_performances"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    family_code = Column(String(50), unique=True, nullable=False)
    total_candidates = Column(Integer, default=0)
    valid_simulations = Column(Integer, default=0)
    empty_portfolio_count = Column(Integer, default=0)
    avg_sharpe = Column(Float, nullable=True)
    avg_fitness = Column(Float, nullable=True)
    avg_turnover = Column(Float, nullable=True)
    avg_margin_bps = Column(Float, nullable=True)
    success_rate = Column(Float, default=0.0)
    empty_portfolio_rate = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class CandidateSimilarity(Base):
    __tablename__ = "candidate_similarities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_a_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    candidate_b_id = Column(String(36), ForeignKey("alpha_candidates.id"), nullable=False)
    structural_similarity = Column(Float, default=0.0)
    signal_correlation = Column(Float, nullable=True)
    field_overlap = Column(Float, default=0.0)
    operator_overlap = Column(Float, default=0.0)
    created_at = Column(DateTime, default=get_utc_now)


class AIProvider(Base):
    __tablename__ = "ai_providers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)  # OPENAI, ANTHROPIC, GEMINI, CUSTOM
    display_name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=False)
    is_validated = Column(Boolean, default=False)
    last_validated_at = Column(DateTime, nullable=True)
    last_status = Column(String(50), default="DISCONNECTED")
    model_name = Column(String(100), nullable=True)


class AIApiKeyMetadata(Base):
    __tablename__ = "ai_api_key_metadata"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider_name = Column(String(50), unique=True, nullable=False)
    encrypted_key = Column(Text, nullable=False)
    key_hint = Column(String(20), nullable=False)  # e.g., sk-...a1b2
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)


class ResearchLog(Base):
    __tablename__ = "research_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    severity = Column(String(20), default="INFO")
    component = Column(String(50), default="SYSTEM")
    event = Column(String(100), nullable=False)
    candidate_id = Column(String(36), nullable=True)
    simulation_id = Column(String(36), nullable=True)
    message = Column(Text, nullable=False)
    diagnostic_metadata = Column(JSON, default=dict)


class WorkerJob(Base):
    __tablename__ = "worker_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_type = Column(String(50), nullable=False)  # GENERATION, PREFLIGHT, SIMULATION, EVALUATION
    priority = Column(Integer, default=50)
    status = Column(String(50), default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    payload = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=get_utc_now)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(100), nullable=False)
    source = Column(String(100), default="VERDE_CORE")
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=get_utc_now)
