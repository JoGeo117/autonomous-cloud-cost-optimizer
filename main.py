"""Main Execution Harness & Demonstration for Cloud Cost Optimizer."""

import uuid
from state import AgentState
from workflow import build_optimizer_graph


def main():
    print("=" * 80)
    print("  AUTONOMOUS MULTI-CLOUD COST OPTIMIZATION AGENT SYSTEM")
    print("=" * 80)

    # 1. Initialize State and Graph
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    app = build_optimizer_graph()

    initial_state = AgentState(thread_id=thread_id)

    # 2. Run graph until HITL Interrupt (before Execution Agent)
    print("\n>>> [STEP 1] Starting Autonomous Discovery & Recommendation Cycle...")
    for event in app.stream(initial_state.model_dump(), config=config):
        for node_name, output in event.items():
            print(f"--- Node '{node_name}' Completed ---")

    # 3. Inspect Current Checkpointed State
    current_state_dict = app.get_state(config).values
    current_state = AgentState(**current_state_dict)

    print("\n" + "=" * 80)
    print("  HUMAN-IN-THE-LOOP (HITL) APPROVAL GATEWAY")
    print("=" * 80)
    print(f"Total Recommendations Generated: {len(current_state.recommendations)}")
    print(f"Pending Human Approvals: {len(current_state.pending_approvals)}")

    for idx, req in enumerate(current_state.pending_approvals, 1):
        print(f"\n[APPROVAL REQUEST #{idx}]")
        print(f"  Resource ID:       {req.resource_id} ({req.cloud_provider.value})")
        print(f"  Category:          {req.category.value} | Risk: {req.risk_tier.name}")
        print(f"  Proposed Action:   {req.action_type} ({req.current_sku} -> {req.proposed_sku})")
        print(f"  Financial ROI:     Save ${req.estimated_monthly_savings:.2f}/mo (Confidence: {req.confidence_score * 100:.1f}%)")
        print(f"  Reasoning:         {req.reasoning}")

    # 4. Simulate Human Operator Decision (Approving Production Rightsizing)
    print("\n>>> [STEP 2] Human Operator reviews and grants APPROVAL for Production Actions...")
    for rec in current_state.recommendations:
        if rec.requires_human_approval:
            rec.status = "APPROVED"
            print(f"  -> Approved Action for Resource: {rec.resource_id}")

    # Update state in checkpointer
    app.update_state(config, {"recommendations": current_state.recommendations})

    # 5. Resume Graph Execution through Execution & Guardrail Agent
    print("\n>>> [STEP 3] Resuming Execution Agent post-approval...")
    for event in app.stream(None, config=config):
        for node_name, output in event.items():
            print(f"--- Node '{node_name}' Completed ---")

    # 6. Final Audit Log Summary
    final_state_dict = app.get_state(config).values
    final_state = AgentState(**final_state_dict)

    print("\n" + "=" * 80)
    print("  FINAL EXECUTION AUDIT TRAIL")
    print("=" * 80)
    for log in final_state.execution_logs:
        print(f"[{log.executed_at}] Execution ID: {log.execution_id}")
        print(f"  Action:    {log.action_taken}")
        print(f"  Snapshot:  {log.snapshot_created}")
        print(f"  Status:    {log.execution_status} - {log.details}\n")
    print("=" * 80)


if __name__ == "__main__":
    main()
