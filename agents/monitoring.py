"""Monitoring and Telemetry Ingestion Agent."""

import uuid
from state import AgentState, CloudProvider, ResourceTelemetry


def monitoring_agent_node(state: AgentState) -> dict:
    """Ingests multi-cloud billing and telemetry metrics into unified FOCUS standard."""
    print("\n[Monitoring Agent] Ingesting real-time telemetry from AWS, GCP, and Azure...")

    # Simulated normalized multi-cloud resources from AWS CUR, GCP BigQuery, & CloudWatch
    sampled_telemetry = [
        ResourceTelemetry(
            resource_id="vol-0a812efc45bc9001",
            cloud_provider=CloudProvider.AWS,
            resource_type="ebs_volume",
            region="us-east-1",
            environment="dev",
            current_sku="gp2_500GB",
            monthly_cost_usd=50.00,
            cpu_p95_pct=0.0,
            mem_p95_pct=0.0,
            network_mb_per_day=0.0,
            is_attached=False,  # Orphan unattached volume
            tags={"Owner": "DevTeamA", "Environment": "dev"}
        ),
        ResourceTelemetry(
            resource_id="i-09f18a23d4cba110",
            cloud_provider=CloudProvider.AWS,
            resource_type="ec2_instance",
            region="us-west-2",
            environment="production",
            current_sku="c5.4xlarge",
            monthly_cost_usd=496.40,
            cpu_p95_pct=6.2,   # Severely over-provisioned compute
            mem_p95_pct=14.5,
            network_mb_per_day=120.0,
            is_attached=True,
            tags={"Service": "OrderProcessor", "Environment": "production"}
        ),
        ResourceTelemetry(
            resource_id="gcp-instance-analytics-prod",
            cloud_provider=CloudProvider.GCP,
            resource_type="compute_engine",
            region="us-central1",
            environment="production",
            current_sku="n2-standard-16",
            monthly_cost_usd=584.00,
            cpu_p95_pct=8.1,
            mem_p95_pct=22.0,
            network_mb_per_day=450.0,
            is_attached=True,
            tags={"Team": "DataScience", "Environment": "production"}
        )
    ]

    return {
        "raw_telemetry": sampled_telemetry,
        "messages": [{
            "agent": "MonitoringAgent",
            "message": f"Successfully ingested {len(sampled_telemetry)} telemetry records."
        }],
        "next_step": "ANALYSIS"
    }
