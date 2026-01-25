# DIE-Ops 
### (Decision Intelligence Engine for Enterprise Operations)

## Overview
**DIE-Ops** is an end-to-end Decision Intelligence prototype designed to help enterprises convert customer analytics into actionable, budget-constrained decisions. 

Rather than stopping at predictions (churn scores, CLTV, forecasts), DIE-Ops focuses on the harder and more valuable problem: 
> **Who should we act on, why, under a fixed budget, and what business impact should we expect?**

This project reflects how real-world enterprises operationalize AI to drive measurable ROI, bridging the gap between data science and business outcomes.

---

## 🚀 One-Click Deploy

Deploy DIE-Ops instantly to the cloud with these one-click buttons:

### Full Stack on Railway (Recommended)
Deploy both backend and frontend together on Railway:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/new?template=https://github.com/blacklovertech/DIE-Ops)

### Backend Only on Railway
Deploy just the FastAPI backend service:

[![Deploy Backend on Railway](https://railway.com/button.svg)](https://railway.com/template/new?template=https://github.com/blacklovertech/DIE-Ops&rootDir=backend)

### Frontend on Vercel
Deploy the React frontend to Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/blacklovertech/DIE-Ops&root-directory=frontend)

### Frontend on Railway
Alternatively, deploy the frontend to Railway:

[![Deploy Frontend on Railway](https://railway.com/button.svg)](https://railway.com/template/new?template=https://github.com/blacklovertech/DIE-Ops&rootDir=frontend)

> **Note:** After deploying, update the frontend's `VITE_API_URL` environment variable to point to your deployed backend URL.

---

## 🐳 Docker Deployment

Run DIE-Ops anywhere with Docker Compose:

### Quick Start
```bash
# Clone the repository
git clone https://github.com/blacklovertech/DIE-Ops.git
cd DIE-Ops

# Build and run the entire stack (production)
docker-compose -f docker/docker-compose.yml up --build

# Or run in development mode with hot reload
docker-compose -f docker/docker-compose.dev.yml up
```

### Access the Application
| Service | Production | Development |
|---------|------------|-------------|
| **Frontend** | http://localhost:3000 | http://localhost:5173 |
| **Backend API** | http://localhost:8000 | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs | http://localhost:8000/docs |

### Docker Commands
```bash
# Run in detached mode (background)
docker-compose -f docker/docker-compose.yml up -d --build

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop all services
docker-compose -f docker/docker-compose.yml down

# Rebuild a specific service
docker-compose -f docker/docker-compose.yml up --build backend

docker-compose -f docker/docker-compose.yml up --build frontend

```

### Docker Folder Structure
```
docker/
├── backend/Dockerfile      # FastAPI backend
├── frontend/Dockerfile     # React frontend (multi-stage)
├── docker-compose.yml      # Production config
├── docker-compose.dev.yml  # Development with hot reload
└── README.md               # Docker documentation
```

---

## The Problem This Project Solves
Most organizations already have churn models, customer segmentation, and dashboards. Yet they still struggle to answer basic operational questions:
* Which customers should we target right now?
* How much should we spend?
* What return can we realistically expect?
* Why were these customers chosen?

The gap is not modeling—**it is decision-making.** DIE-Ops exists to bridge analytics and action.

### Core Decision Enabled
**Given a fixed marketing budget and cost per action, which customers should we target to maximize incremental business impact—and why?**

---

## Conceptual Foundations
DIE-Ops combines three complementary decision lenses to move beyond simple propensity scoring:

1.  **Churn (Risk):** Estimates the probability that a customer will disengage. 
    * *Answers: "Who is at risk?"*
2.  **CLTV (Value):** Estimates the future economic value of a customer using repeat-purchase behavior (BG/NBD + Gamma-Gamma). 
    * *Answers: "Who is worth saving?"*
3.  **Uplift (Impact):** Estimates the incremental change caused by taking an action (e.g., an offer). 
    * *Answers: "Who will actually change behavior if we act?"*

**DIE-Ops combines all three into ROI-aware decisions.**

---

## System Architecture

[Customer Data: CSV / SQL]
        |
        v
[Ingestion & Validation]
        |
        v
[Feature Engineering]
        |
        v
[ML Layer]
  - Churn Model (LightGBM)
  - CLTV Model (Lifetimes)
  - Uplift Model (Two-Model Approach)
        |
        v
[Decision Engine]
  - ROI-based Optimizer (Greedy Selection)
  - Budget & Cost Constraints
        |
        v
[Explainability Layer]
  - SHAP-based narratives
  - Scenario simulation
        |
        v
[Delivery]
  - FastAPI endpoints (Scoring & Decisions)
  - Flask + HTMX UI (Interaction)
  - Executive-ready HTML reports & CSV exports

---

## What DIE-Ops Actually Produces
For a given campaign configuration, the system outputs:
* **Prioritized Target List:** A specific list of customers sorted by ROI.
* **Financial Projections:** Expected incremental revenue and total campaign ROI.
* **Reason Codes:** SHAP-derived explanations for why a customer was selected.
* **Strategy Reports:** Automated, executive-ready HTML reports for stakeholders.
* **Operational Exports:** CSV files ready for CRM ingestion.

---

## Key Features
* **Enterprise Data Layer:** Deterministic ingestion with schema validation and checksums for reproducibility.
* **Multi-Model Intelligence:** Integrated Risk, Value, and Impact modeling.
* **Decision & Optimization:** ROI-aware selection that explicitly excludes negative-ROI actions ("Sleeping Dogs").
* **Explainability:** SHAP-based explanations converted into business-friendly narratives.
* **Full-Stack Mindset:** FastAPI for serving, Flask/HTMX for UI, and CI-ready Docker structures.

---

## Why This Project Matters
DIE-Ops demonstrates:
1.  **Decision-first thinking**, not just model-first thinking.
2.  Understanding of how AI is **operationalized** in enterprise environments.
3.  The ability to design systems that connect **Data → Decisions → Outcomes**.
4.  Alignment with high-level analytics consulting and AI transformation work.

---

## How to Run

### 1. Setup & Ingestion
```bash
# Generate synthetic dataset
python src/ingest/ingest.py
```

### 2. Model Training
```bash

# Train the three-pillar intelligence layer
python -m src.models.train_churn
python -m src.models.train_uplift
python -m src.models.train_cltv
```

### 3. Start Services
```bash

# Start the FastAPI Backend
uvicorn src.api.main:app --reload

# In a new terminal, start the Flask UI
python src/frontend/server.py
Access the dashboard at http://localhost:5001.
```

---

## Future Extensions
* Online A/B validation of predicted uplift.
* Campaign monitoring and automated drift detection.
* Integration with production CRM platforms (e.g., Salesforce, HubSpot).
* Multi-action policy optimization (Choosing the best offer, not just any offer).

---

## Author Intent
This project was built to demonstrate how applied AI systems should be designed when the goal is **better decisions**, not just better models.
