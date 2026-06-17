# System Architecture — Urban Infrastructure Intelligence Portal

## Overview

The Urban Infrastructure Intelligence Portal is a full-stack city infrastructure management platform designed to go beyond traditional CRUD. It functions as an **intelligence system** that models the health, risk, and interdependencies of city infrastructure assets.

---

## Architecture Layers

```
┌────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                          │
│  Dashboard │ Map View │ Asset Explorer │ Maintenance Priority  │
└──────────────────────┬─────────────────────────────────────────┘
                       │ HTTP (REST)
┌──────────────────────▼─────────────────────────────────────────┐
│                   FASTAPI BACKEND                              │
│  /assets  │ /analytics  │ /maintenance  │ /map                 │
└──────────────────────┬─────────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────────┐
│               INTELLIGENCE SERVICES                            │
│  Health Engine │ Risk Propagation │ Priority Engine │ Lifecycle │
└──────────────────────┬─────────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────────┐
│             SQLAlchemy ORM + SQLite / PostgreSQL               │
└────────────────────────────────────────────────────────────────┘
```

---

## Core Intelligence Services

### 1. Health Scoring Engine (`services/health_engine.py`)

Uses a weighted multi-factor formula:

```
health_score = 0.40 × age_score
             + 0.30 × inspection_delay_score
             + 0.20 × damage_score
             + 0.10 × maintenance_frequency_score
```

- **age_score**: Logarithmic decay curve based on asset type design life
- **inspection_delay_score**: Days since last inspection vs. standard interval
- **damage_score**: Average damage level from maintenance logs + citizen report count
- **maintenance_score**: Recency of last maintenance action

Classifications:
- 0–30 → **Healthy** (Green)
- 31–60 → **Warning** (Yellow)
- 61–100 → **Critical** (Red)

### 2. Risk Propagation Engine (`services/risk_propagation.py`)

BFS graph traversal that cascades risk from critical assets to connected neighbors:

```
Critical Asset (score ≥ 61)
    └─→ Direct Neighbor (risk_delta = base × 0.70^1 × 0.30)
            └─→ Second Hop (risk_delta × 0.70^2)
                    └─→ Third Hop (max depth)
```

Risk decays 30% per hop. Supports multi-source propagation with max-delta resolution.

### 3. Maintenance Priority Engine (`services/priority_engine.py`)

```
priority_score = 0.40 × safety_risk
               + 0.30 × population_impact
               + 0.20 × infrastructure_importance
               + 0.10 × cost_urgency
```

Returns a ranked queue with recommended actions:
- EMERGENCY → Immediate intervention
- URGENT → 7 days
- HIGH PRIORITY → 30 days
- SCHEDULE → 90 days
- MONITOR → Standard cycle

### 4. Lifecycle Service (`services/lifecycle_service.py`)

Constructs a chronological event timeline per asset including:
- Construction event
- Inspection and maintenance events
- Citizen reports
- Risk escalation events

---

## Data Flow

```
Citizen Report / Maintenance Log Added
        ↓
Health Engine recalculates score
        ↓
Risk Propagation updates network
        ↓
Priority Engine re-ranks assets
        ↓
Streamlit UI reflects updated state
```

---

## Technology Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| API | FastAPI | Async, auto-docs, Pydantic integration |
| ORM | SQLAlchemy 2.0 | Mature, flexible, supports migrations |
| DB | SQLite (dev) / PostgreSQL (prod) | Easy local dev, production-ready swap |
| Frontend | Streamlit | Rapid data app development |
| Charts | Plotly | Interactive, professional visualizations |
| Maps | Pydeck | WebGL-powered geospatial rendering |
| Testing | pytest | Industry standard, simple fixtures |
