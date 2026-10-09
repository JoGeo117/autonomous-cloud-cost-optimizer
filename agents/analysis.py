"""Analysis & Anomaly Detection Agent."""

from state import AgentState


def analysis_agent_node(state: AgentState) -> dict:
    """Evaluates telemetry for idle assets, over-provisioning, and anomalies."""
    print("\n[Analysis & Anomaly Agent] Executing statistical & heuristic anomaly models...")

    anomalies = []
    for item in state.raw_telemetry:
        # Check 1: Idle Unattached Disks
        if not item.is_attached and item.resource_type in ["ebs_volume", "persistent_disk"]:
            anomalies.append({
                "resource_id": item.resource_id,
                "type": "ORPHAN_STORAGE",
                "severity": "MEDIUM",
                "description": f"Unattached storage volume costing ${item.monthly_cost_usd:.2f}/mo."
            })
        
        # Check 2: Severe Over-provisioning (p95 CPU < 10% and p95 RAM < 25%)
        elif item.cpu_p95_pct < 10.0 and item.mem_p95_pct < 25.0:
            anomalies.append({
                "resource_id": item.resource_id,
                "type": "OVERPROVISIONED_COMPUTE",
                "severity": "HIGH",
                "description": (
                    f"Resource {item.resource_id} ({item.current_sku}) is severely underutilized: "
                    f"p95 CPU={item.cpu_p95_pct}%, p95 RAM={item.mem_p95_pct}%."
                )
            })

    return {
        "detected_anomalies": anomalies,
        "messages": [{
            "agent": "AnalysisAgent",
            "message": f"Identified {len(anomalies)} anomalies and optimization opportunities."
        }],
        "next_step": "RECOMMENDER"
    }
