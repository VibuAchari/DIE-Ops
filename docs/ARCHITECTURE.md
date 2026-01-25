# DIE-Ops Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         DIE-Ops Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐          ┌──────────────────────────┐    │
│  │   React Frontend │◄────────►│   FastAPI Backend        │    │
│  │   (Port 5173)    │   REST   │   (Port 8000)            │    │
│  └──────────────────┘          └──────────────────────────┘    │
│           │                              │                      │
│           ▼                              ▼                      │
│  ┌──────────────────┐          ┌──────────────────────────┐    │
│  │  UI Components   │          │  ML Models               │    │
│  │  - AdminPanel    │          │  - Churn (LightGBM)      │    │
│  │  - CustomerSearch│          │  - Uplift (T-Learner)    │    │
│  │  - CampaignBuild │          │  - CLTV (BG/NBD+GG)      │    │
│  │  - Reports       │          └──────────────────────────┘    │
│  └──────────────────┘                    │                      │
│                                          ▼                      │
│                                ┌──────────────────────────┐    │
│                                │  Data Layer              │    │
│                                │  - /data (CSV)           │    │
│                                │  - /models (PKL)         │    │
│                                │  - /output (HTML)        │    │
│                                └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Backend (`app.py`)

Single-file Python application containing all business logic:

| Module | Lines | Purpose |
|--------|-------|---------|
| Utilities | 75-116 | Directory management, validation |
| Ingest | 118-181 | Synthetic data generation |
| Features | 183-221 | RFM feature engineering |
| Explainability | 223-246 | SHAP narrative generation |
| Models | 248-324 | Churn, Uplift, CLTV training |
| Optimizer | 326-368 | ROI-based customer selection |
| Report Gen | 370-422 | HTML report generation |
| API Routes | 424-580 | FastAPI endpoints |

### Frontend (`frontend/`)

```
frontend/
├── src/
│   ├── App.tsx              # Main app with routing
│   ├── api.ts               # API client (axios)
│   ├── index.css            # Global premium styles
│   └── components/
│       ├── Navbar.tsx       # Navigation header
│       ├── AdminPanel.tsx   # Dashboard + admin actions
│       ├── KPICard.tsx      # Metric display cards
│       ├── CustomerSearch.tsx # Customer lookup
│       ├── CampaignBuilder.tsx # Campaign optimizer
│       └── Reports.tsx      # Report viewer
```

## Data Flow

### Scoring Flow
```
User Request → API → Load Data → Featurize → Model Predict → Response
```

### Campaign Optimization Flow
```
Budget + CPA → Score All Customers → Compute Expected Gain → ROI Sort → Select Top N → Return List
```

## Model Architecture

### Churn Model
- **Algorithm**: LightGBM Classifier
- **Features**: RFM metrics, log transforms, tenure buckets
- **Output**: Probability [0, 1]

### Uplift Model (T-Learner)
- **Treatment Model**: LightGBM on treated customers
- **Control Model**: LightGBM on control customers
- **Output**: P(conversion|treated) - P(conversion|control)

### CLTV Model
- **BG/NBD**: Predicts expected transactions
- **Gamma-Gamma**: Predicts expected monetary value
- **Output**: 12-month CLV, normalized [0, 1]

## API Design

All endpoints follow REST conventions with JSON payloads.

### Request Example
```json
POST /score/customer
{
  "customer_id": 42
}
```

### Response Example
```json
{
  "customer_id": 42,
  "churn_prob": 0.34,
  "uplift": 0.08,
  "cltv": 0.72
}
```

## Deployment Options

| Component | Platform | Notes |
|-----------|----------|-------|
| Frontend | Vercel | Set `VITE_API_URL` env var |
| Backend | Railway | Use `python app.py api` |
| Full Stack | Docker Compose | Local or cloud VMs |
