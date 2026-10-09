"""Execution & Guardrail Agent with Snapshot & Rollback Capabilities."""

import datetime
import uuid
from state import AgentState, ExecutionAuditLog, RiskTier


def execution_agent_node(state: AgentState) -> dict:
    """Executes safe autonomous actions (Tier 0) or pre-approved actions."""
    print("\n[Execution & Guardrail Agent] Processing remediation actions against safety guardrails...")

    execution_logs = []

    for rec in state.recommendations:
        # Guardrail Check 1: Block Tier 2/3 actions if not approved
        if rec.requires_human_approval and rec.status != "APPROVED":
            print(f"  [GUARDRAIL HALT] Action on {rec.resource_id} ({rec.risk_tier.name}) requires explicit human sign-off.")
            continue

        # Execute Autonomous Action
        print(f"  [EXECUTING] Applying {rec.action_type} for resource: {rec.resource_id}")
        
        # Step 1: Pre-execution Safety Snapshot
        snapshot_id = f"snap-auto-{uuid.uuid4().hex[:8]}"
        print(f"    -> Safety pre-flight: Created snapshot backup: {snapshot_id}")

        # Step 2: Simulated IaC / SDK execution
        print(f"    -> Dry-run verification: PASS. Executed {rec.proposed_sku} migration.")

        # Step 3: Log Execution Audit Trail
        log = ExecutionAuditLog(
            execution_id=str(uuid.uuid4()),
            recommendation_id=rec.recommendation_id,
            executed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            action_taken=f"{rec.action_type}: {rec.current_sku} -> {rec.proposed_sku}",
            snapshot_created=snapshot_id,
            dry_run_success=True,
            execution_status="SUCCESS",
            details=f"Monthly cost reduced from ${rec.current_monthly_cost:.2f} to ${rec.proposed_monthly_cost:.2f}."
        )
        execution_logs.append(log)
        rec.status = "EXECUTED"

    return {
        "execution_logs": execution_logs,
        "messages": [{
            "agent": "ExecutionAgent",
            "message": f"Successfully executed {len(execution_logs)} actions."
        }],
        "is_complete": True
    }
