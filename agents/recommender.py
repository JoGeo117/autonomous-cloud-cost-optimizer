"""Recommendation & ROI Engine."""

import uuid
from state import (
    AgentState, CostRecommendation, RecommendationCategory, RiskTier
)


def recommendation_engine_node(state: AgentState) -> dict:
    """Calculates ROI, target SKUs, and maps actions to risk tiers."""
    print("\n[Recommendation Engine] Formulating optimization proposals and calculating ROI...")

    recommendations = []
    pending_approvals = []

    for item in state.raw_telemetry:
        # Case A: Orphan volume cleanup
        if not item.is_attached:
            rec = CostRecommendation(
                recommendation_id=str(uuid.uuid4()),
                resource_id=item.resource_id,
                cloud_provider=item.cloud_provider,
                category=RecommendationCategory.IDLE_CLEANUP,
                action_type="DELETE_ORPHAN_VOLUME_WITH_SNAPSHOT",
                risk_tier=RiskTier.TIER_0_AUTONOMOUS if item.environment == "dev" else RiskTier.TIER_2_HUMAN_APPROVAL,
                current_sku=item.current_sku,
                proposed_sku="DELETED",
                current_monthly_cost=item.monthly_cost_usd,
                proposed_monthly_cost=0.0,
                estimated_monthly_savings=item.monthly_cost_usd,
                confidence_score=0.98,
                reasoning="Volume is detached and inactive for > 14 days. Pre-deletion snapshot will be created.",
                requires_human_approval=(item.environment != "dev")
            )
            recommendations.append(rec)
            if rec.requires_human_approval:
                pending_approvals.append(rec)

        # Case B: Compute Rightsizing
        elif item.cpu_p95_pct < 10.0 and item.mem_p95_pct < 25.0:
            # Example Rightsizing: c5.4xlarge ($496.40) -> c6i.xlarge ($122.64)
            proposed_sku = "c6i.xlarge" if item.cloud_provider == "AWS" else "n2-standard-4"
            proposed_cost = item.monthly_cost_usd * 0.25
            savings = item.monthly_cost_usd - proposed_cost

            is_prod = (item.environment == "production")
            rec = CostRecommendation(
                recommendation_id=str(uuid.uuid4()),
                resource_id=item.resource_id,
                cloud_provider=item.cloud_provider,
                category=RecommendationCategory.RIGHTSIZING,
                action_type="RESIZE_COMPUTE_INSTANCE",
                risk_tier=RiskTier.TIER_2_HUMAN_APPROVAL if is_prod else RiskTier.TIER_1_SCHEDULED,
                current_sku=item.current_sku,
                proposed_sku=proposed_sku,
                current_monthly_cost=item.monthly_cost_usd,
                proposed_monthly_cost=proposed_cost,
                estimated_monthly_savings=savings,
                confidence_score=0.94,
                reasoning=f"Downscale {item.current_sku} -> {proposed_sku}. Peak CPU is {item.cpu_p95_pct}%.",
                requires_human_approval=is_prod
            )
            recommendations.append(rec)
            if rec.requires_human_approval:
                pending_approvals.append(rec)

    return {
        "recommendations": recommendations,
        "pending_approvals": pending_approvals,
        "messages": [{
            "agent": "RecommenderEngine",
            "message": (
                f"Generated {len(recommendations)} recommendations. "
                f"{len(pending_approvals)} require Human-in-the-Loop approval."
            )
        }],
        "next_step": "EXECUTION"
    }
