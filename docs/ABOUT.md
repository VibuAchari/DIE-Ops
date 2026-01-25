# DIE-Ops: Customer Intelligence Platform

## Overview

DIE-Ops (Decision Intelligence Engine for Operations) is an AI-powered customer intelligence platform that combines machine learning models with a modern web interface to optimize marketing campaigns and predict customer behavior.

## Key Features

### 🎯 Customer Scoring
- **Churn Prediction**: LightGBM-based model to identify at-risk customers
- **CLTV Estimation**: Probabilistic lifetime value using BG/NBD + Gamma-Gamma models
- **Uplift Modeling**: Two-model approach to measure campaign effectiveness

### 📊 Campaign Optimization
- ROI-based customer selection algorithm
- Budget-constrained targeting
- Expected gain calculations

### 🖥️ Modern Interface
- React + TypeScript frontend
- FastAPI backend with automatic API docs
- Real-time scoring and recommendations

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Generate sample data
python app.py ingest

# Train models
python app.py train

# Start API server
python app.py api
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/score/customer` | POST | Score individual customer |
| `/score/batch` | POST | Score all customers |
| `/recommend` | POST | Get campaign recommendations |
| `/simulate` | GET | Quick simulation |
| `/admin/ingest` | POST | Trigger data generation |
| `/admin/train` | POST | Trigger model training |
| `/reports` | GET | List generated reports |

## Tech Stack

- **Backend**: Python, FastAPI, LightGBM, lifetimes, scikit-learn
- **Frontend**: React, TypeScript, Vite, Framer Motion
- **Styling**: Custom CSS with glassmorphism design

## License

MIT License
