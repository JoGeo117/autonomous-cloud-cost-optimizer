import pandas as pd
from pathlib import Path

# ------------------------------------------------------------
# Load fabricated telemetry data (CSV) – this file was created as an artifact.
# ------------------------------------------------------------
csv_path = Path(__file__).parent / "fabricated_telemetry.csv"
if not csv_path.exists():
    raise FileNotFoundError(f"Telemetry CSV not found at {csv_path}")

df = pd.read_csv(csv_path)
print("=== Monitoring Agent (raw telemetry) ===")
print(df)

# ------------------------------------------------------------
# Simple Analysis Agent – flag idle storage or over‑provisioned compute.
# ------------------------------------------------------------
def analyse(row):
    if row['resource_type'] == 'EBS' and row['iops'] == 0 and row['size_gb'] > 0:
        return 'idle_storage'
    if row['resource_type'] == 'EC2' and row['cpu_percent'] < 10 and row['memory_percent'] < 25:
        return 'overprovisioned_compute'
    return 'healthy'

df['analysis'] = df.apply(analyse, axis=1)
print("\n=== Analysis Agent ===")
print(df[['resource_id', 'resource_type', 'analysis']])

# ------------------------------------------------------------
# Recommendation Agent – produce a recommendation dict for each flagged row.
# ------------------------------------------------------------
def recommend(row):
    if row['analysis'] == 'idle_storage':
        return {
            'resource_id': row['resource_id'],
            'action': 'delete_volume',
            'details': f"Delete idle EBS volume {row['resource_id']} (size {row['size_gb']} GB)",
            'estimated_savings_usd_per_month': 5.0,
        }
    if row['analysis'] == 'overprovisioned_compute':
        return {
            'resource_id': row['resource_id'],
            'action': 'rightsize_instance',
            'details': f"Resize EC2 instance {row['resource_id']} to a smaller class",
            'estimated_savings_usd_per_month': 30.0,
        }
    return None

recommendations = []
for _, row in df.iterrows():
    rec = recommend(row)
    if rec:
        recommendations.append(rec)

print("\n=== Recommendation Agent ===")
if recommendations:
    rec_df = pd.DataFrame(recommendations)
    print(rec_df)
else:
    print("No recommendations generated.")

# ------------------------------------------------------------
# Execution Agent – for this demo we only print what would be done.
# ------------------------------------------------------------
print("\n=== Execution Agent ===")
if recommendations:
    for rec in recommendations:
        print(f"[EXECUTION] Would perform: {rec['action']} on {rec['resource_id']} – {rec['details']}")
else:
    print("No actions to execute – not applicable for this demo.")

# End of demo script
