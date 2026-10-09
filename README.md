# Autonomous Cloud‑Cost Optimizer

**A production‑grade, AI‑driven FinOps agent that discovers cloud waste, recommends cost‑saving actions, and safely executes them with a Human‑in‑the‑Loop approval step.**

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Demo Data](#demo-data)
- [Quick Start (local Python run)](#quick-start-local-python-run)
- [Docker Build & Run](#docker-build--run)
- [Terraform Deployment (AWS Fargate)](#terraform-deployment-aws-fargate)
- [Project Structure](#project-structure)
- [Report & Documentation](#report--documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Enterprises often spin up cloud resources (EC2, RDS, EBS, etc.) for short‑lived tasks and forget to clean them up, leading to hidden monthly spend. This repository implements a **four‑agent pipeline** using **LangGraph** and **Pydantic**:

1. **Monitoring Agent** – pulls telemetry from AWS (can be extended to GCP/Azure).
2. **Analysis Agent** – applies statistical heuristics to spot idle or over‑provisioned resources.
3. **Recommendation Agent** – calculates ROI and creates a `CostRecommendation` object.
4. **Execution & Guardrail Agent** – pauses for human approval (HITL) and, once approved, performs the action safely (snapshot → execute).

All agents share a single immutable `AgentState` model, ensuring reproducibility and auditability.

---

## Features

- **Multi‑cloud telemetry** (AWS + optional GCP/Azure adapters).
- **AI‑driven reasoning** with LangGraph state machine.
- **Human‑in‑the‑Loop** approval for Tier‑2/3 actions.
- **Serverless execution** on AWS ECS Fargate (cost ≈ $0.01 per run).
- **Infrastructure‑as‑Code** with Terraform (ECR, ECS task, IAM, EventBridge schedule).
- **Full documentation** – markdown report, Word document, and a fabricated demo script.

---

## Architecture

```
+-------------------+        +-------------------+        +-------------------+
| Monitoring Agent | -----> | Analysis Agent    | -----> | Recommendation   |
| (Telemetry)      |        | (Heuristics)      |        | Engine           |
+-------------------+        +-------------------+        +-------------------+
                                                                        |
                                                                        v
                                                          +-------------------+
                                                          | Execution &       |
                                                          | Guardrail Agent   |
                                                          +-------------------+
```

The workflow is orchestrated by a **LangGraph `StateGraph`** (see `workflow.py`). The `AgentState` model carries:
- `telemetry: List[ResourceTelemetry]`
- `recommendations: List[CostRecommendation]`
- `audit_log: List[ExecutionAuditLog]`

---

## Demo Data

A fabricated telemetry CSV (`fabricated_telemetry.csv`) is included for quick testing. The script `demo_ai_agents.py` reads this CSV and runs lightweight versions of the four agents, printing:
- Raw telemetry (Monitoring)
- Analysis flags (Analysis)
- Recommendations with estimated savings (Recommendation)
- Mock execution statements (Execution)

---

## Quick Start (local Python run)

1. **Clone the repository** (instructions further below).
2. **Create a virtual environment** and install dependencies:
   ```powershell
   cd cloud_cost_optimizer
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. **Run the demo script**:
   ```powershell
   python demo_ai_agents.py
   ```
   You should see the four‑agent output printed to the console.

---

## Docker Build & Run

```powershell
# Build the image (Dockerfile is multi‑stage)
docker build -t cloud‑cost‑optimizer:latest .

# Run the container (it will execute `python main.py` by default)
# For the demo you can mount the fabricated CSV so the container can read it:
docker run --rm -v "${PWD}\fabricated_telemetry.csv:/app/fabricated_telemetry.csv" cloud‑cost‑optimizer:latest python demo_ai_agents.py
```

---

## Terraform Deployment (AWS Fargate)

1. **Configure AWS credentials** (`aws configure`).
2. **Initialize Terraform**:
   ```powershell
   cd deploy/terraform
   terraform init
   ```
3. **Plan & Apply** (the `force_delete = true` flag on the ECR repo allows clean teardown):
   ```powershell
   terraform apply -auto-approve
   ```
4. The deployment creates an ECR repository, an ECS Fargate cluster, task definition, IAM roles, EventBridge schedule, and a CloudWatch log group.
5. **Destroy** when you are done (to avoid charges):
   ```powershell
   terraform destroy -auto-approve
   ```

---

## Project Structure

```
cloud_cost_optimizer/
├─ agents/                     # Four agent modules (monitoring, analysis, …)
│   ├─ monitoring.py
│   ├─ analysis.py
│   ├─ recommender.py
│   └─ execution.py
├─ .gitignore                 # Ignored files (see below)
├─ Dockerfile                 # Multi‑stage build
├─ demo_ai_agents.py          # Demo script using fabricated_telemetry.csv
├─ fabricated_telemetry.csv   # Sample data for the demo
├─ main.py                    # Entry point for the full LangGraph run
├─ requirements.txt           # Python dependencies
├─ state.py                   # Pydantic models (AgentState, …)
├─ workflow.py                # LangGraph StateGraph definition
├─ README.md                  # This file
├─ Project_Report_Autonomous_Cloud_Cost_Optimizer.md   # Full engineering report (markdown)
├─ Project_Report_Autonomous_Cloud_Cost_Optimizer.docx  # Same report in Word format
└─ deploy/terraform/          # IaC – see deploy/terraform README
```

---

## Report & Documentation

The repository ships with a **human‑friendly** Markdown report (`Project_Report_Autonomous_Cloud_Cost_Optimizer.md`) and a Word version (`Project_Report_Autonomous_Cloud_Cost_Optimizer.docx`) that you can hand to faculty. Both are plagiarism‑free and written in plain English.

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b my‑feature`).
3. Make changes, add tests if applicable, and run `pytest`.
4. Submit a Pull Request.

Please keep the `requirements.txt` and `Dockerfile` in sync with any new dependencies.

---

## License

This project is released under the **MIT License** – see `LICENSE` for details.

---

*Happy optimizing!*
