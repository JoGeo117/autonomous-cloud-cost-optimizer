"""State and Schema definitions for Autonomous Cloud Cost Optimizer."""

from __future__ import annotations

import operator
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"


class RiskTier(int, Enum):
    TIER_0_AUTONOMOUS = 0      # Non-destructive dev cleanup (Auto-approved)
    TIER_1_SCHEDULED = 1       # Staging rightsizing (Scheduled with opt-out)
    TIER_2_HUMAN_APPROVAL = 2  # Production compute rightsizing (Single approval)
    TIER_3_CRITICAL = 3        # Core DB / large commitment (Dual approval)


class RecommendationCategory(str, Enum):
    RIGHTSIZING = "RIGHTSIZING"
    IDLE_CLEANUP = "IDLE_CLEANUP"
    COMMITMENT_PURCHASE = "COMMITMENT_PURCHASE"
    STORAGE_LIFECYCLE = "STORAGE_LIFECYCLE"


class ResourceTelemetry(BaseModel):
    resource_id: str
    cloud_provider: CloudProvider
    resource_type: str
    region: str
    environment: str  # e.g., 'production', 'staging', 'dev'
    current_sku: str
    monthly_cost_usd: float
    cpu_p95_pct: float
    mem_p95_pct: float
    network_mb_per_day: float
    is_attached: bool = True
    tags: Dict[str, str] = Field(default_factory=dict)


class CostRecommendation(BaseModel):
    recommendation_id: str
    resource_id: str
    cloud_provider: CloudProvider
    category: RecommendationCategory
    action_type: str
    risk_tier: RiskTier
    current_sku: str
    proposed_sku: str
    current_monthly_cost: float
    proposed_monthly_cost: float
    estimated_monthly_savings: float
    confidence_score: float
    reasoning: str
    requires_human_approval: bool
    status: str = "PROPOSED"  # PROPOSED, APPROVED, REJECTED, EXECUTED, ROLLED_BACK


class ExecutionAuditLog(BaseModel):
    execution_id: str
    recommendation_id: str
    executed_at: str
    action_taken: str
    snapshot_created: Optional[str] = None
    dry_run_success: bool
    execution_status: str
    details: str


class AgentState(BaseModel):
    """Global immutable state container passed across all LangGraph nodes."""
    
    thread_id: str
    messages: Annotated[List[Dict[str, Any]], operator.add] = Field(default_factory=list)
    raw_telemetry: List[ResourceTelemetry] = Field(default_factory=list)
    detected_anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[CostRecommendation] = Field(default_factory=list)
    pending_approvals: List[CostRecommendation] = Field(default_factory=list)
    execution_logs: Annotated[List[ExecutionAuditLog], operator.add] = Field(default_factory=list)
    next_step: str = "MONITORING"
    is_complete: bool = False
