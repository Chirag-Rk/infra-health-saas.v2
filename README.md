# 🏙️ Urban Infrastructure Intelligence Portal

> A production-ready city infrastructure intelligence platform — health scoring, risk propagation, geospatial , lifecycle tracking, and maintenance decision support.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Key Features](#key-features)
4. [System Architecture](#system-architecture)
5. [Project Structure](#project-structure)
6. [Database Design](#database-design)
7. [Intelligence Engines](#intelligence-engines)
8. [Installation Guide](#installation-guide)
9. [Running the Application](#running-the-application)
10. [API Reference](#api-reference)
11. [Frontend Pages](#frontend-pages)
12. [Running Tests](#running-tests)
13. [Configuration](#configuration)
14. [Future Improvements](#future-improvements)

---

## Project Overview

The **Urban Infrastructure Intelligence Portal** is a full-stack Python system for managing and analyzing city infrastructure assets — roads, bridges, pipelines, drainage systems, street lights, and public facilities.

Unlike a basic CRUD dashboard, this platform operates as an **intelligence system** that:

- Continuously **scores** the health of every asset using a multi-factor algorithm
- **Propagates risk** through the infrastructure network when critical failures occur
- **Ranks** maintenance jobs by real-world urgency across safety, population impact, and cost
- **Tracks** the full lifecycle history of every asset from construction to decommission
- **Visualizes** the entire city infrastructure network on an interactive geospatial map

---

## Problem Statement

Cities manage thousands of aging infrastructure assets. Most current tools are passive record-keepers — they store data but offer no intelligence. Critical failures are discovered reactively. Maintenance budgets are wasted on low-urgency work while high-risk assets go unnoticed.

**This portal solves four core problems:**

| Problem | Solution |
|--------|---------|
| No dynamic health measurement | Multi-factor health scoring engine with age decay, inspection delay, and damage assessment |
| Siloed asset management | Risk propagation engine models how failures cascade across connected infrastructure |
| No prioritization logic | Priority engine ranks work orders by safety, population impact, and cost urgency |
| Missing historical context | Lifecycle timeline tracks every event from installation to present |

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🧮 **Health Scoring Engine** | Weighted formula combining asset age, inspection delay, damage level, and maintenance frequency |
| 🕸️ **Risk Propagation** | BFS graph traversal cascades risk from critical assets to connected neighbors with 30% decay per hop |
| 🏆 **Maintenance Priority Queue** | Multi-factor ranking by safety risk, population impact, infrastructure importance, and cost urgency |
| ⏱️ **Lifecycle Timeline** | Full chronological history: construction → inspections → citizen reports → risk escalations |
| 🗺️ **Geospatial Map** | Pydeck-powered interactive map with color-coded markers and connection overlays |
| 📊 **Intelligence Dashboard** | KPIs, health distribution, department breakdown, and network health gauge |
| 📢 **Citizen Reports** | Public damage reporting that feeds directly into health scoring |
| 🔗 **Asset Connections** | Model structural and dependency relationships between infrastructure assets |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT FRONTEND                          │
│   Dashboard  │  Map View  │  Asset Explorer  │  Priority Queue  │
└────────────────────────┬────────────────────────────────────────┘
                         │  HTTP REST
┌────────────────────────▼────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│   /assets    │  /analytics  │  /maintenance  │  /map            │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                 INTELLIGENCE SERVICES LAYER                     │
│  Health Engine │ Risk Propagation │ Priority Engine │ Lifecycle  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              SQLAlchemy ORM  →  SQLite / PostgreSQL             │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Data Validation | Pydantic v2 |
| Frontend | Streamlit |
| Charts | Plotly |
| Maps | Pydeck (WebGL) |
| Testing | pytest |

---

## Project Structure

```
urban_infrastructure_portal/
│
├── app/
│   ├── main.py                    # FastAPI app, CORS, router registration
│   ├── config.py                  # Environment settings (Pydantic Settings)
│   ├── database.py                # Engine, session factory, init_db()
│   │
│   ├── models/
│   │   ├── asset_model.py         # InfrastructureAsset ORM model
│   │   ├── maintenance_model.py   # MaintenanceLog, CitizenReport ORM models
│   │   ├── connection_model.py    # AssetConnection ORM model
│   │   └── user_model.py          # User ORM model
│   │
│   ├── schemas/
│   │   ├── asset_schema.py        # Pydantic schemas for assets and connections
│   │   └── maintenance_schema.py  # Pydantic schemas for logs, reports, priority
│   │
│   ├── routers/
│   │   ├── asset_router.py        # CRUD + history endpoints
│   │   ├── analytics_router.py    # Overview + network risk endpoints
│   │   ├── maintenance_router.py  # Priority queue + logs + reports
│   │   └── map_router.py          # GeoJSON + nearby + connections
│   │
│   ├── services/
│   │   ├── health_engine.py       # Multi-factor health scoring algorithm
│   │   ├── risk_propagation.py    # BFS risk cascade graph engine
│   │   ├── priority_engine.py     # Maintenance priority ranking engine
│   │   └── lifecycle_service.py   # Timeline builder and age profiler
│   │
│   └── utils/
│       ├── geo_utils.py           # Haversine, GeoJSON, map bounds
│       ├── scoring_utils.py       # Normalization and scoring helpers
│       └── validation_utils.py    # Input validation helpers
│
├── frontend/
│   ├── streamlit_app.py           # Entry point and navigation
│   └── pages/
│       ├── dashboard.py           # KPIs, charts, network health gauge
│       ├── map_view.py            # Pydeck interactive map
│       ├── asset_explorer.py      # Asset detail view + lifecycle timeline
│       └── maintenance_priority.py # Priority queue ranked cards
│
├── scripts/
│   └── seed_database.py           # Seeds 20 realistic city assets with history
│
├── tests/
│   ├── test_health_engine.py      # 15 unit tests for health scoring
│   ├── test_priority_engine.py    # 12 unit tests for priority ranking
│   └── test_assets.py             # API integration tests (CRUD + analytics)
│
├── docs/
│   ├── system_architecture.md
│   ├── api_documentation.md
│   └── workflow.md
│
├── requirements.txt
└── README.md
```

---

## Database Design

### `infrastructure_assets`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | Auto-increment |
| `asset_name` | String(200) | Human-readable name |
| `asset_type` | String(100) | road, bridge, pipeline, drainage, street_light, public_facility |
| `department` | String(150) | Responsible city department |
| `latitude` | Float | GPS coordinate |
| `longitude` | Float | GPS coordinate |
| `installation_year` | Integer | Year built |
| `status` | String(50) | active, inactive, under_maintenance, decommissioned |
| `last_inspection_date` | Date | Date of most recent inspection |
| `health_score` | Float | 0–100 computed score |
| `risk_level` | String(20) | healthy, warning, critical |

### `maintenance_logs`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | |
| `asset_id` | FK → assets | |
| `inspection_date` | Date | |
| `inspector` | String(150) | Inspector name |
| `condition_notes` | Text | Field observations |
| `damage_level` | Float (0–10) | Severity of damage found |
| `maintenance_action` | String(300) | Action taken |

### `asset_connections`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | |
| `asset_id` | FK → assets | Source asset |
| `connected_asset_id` | FK → assets | Target asset |
| `connection_type` | String(100) | structural, feeds_into, adjacent, dependent |

### `citizen_reports`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | |
| `asset_id` | FK → assets | |
| `report_type` | String(100) | pothole, crack, flooding, outage, structural |
| `description` | Text | |
| `severity` | String(20) | low, medium, high |
| `timestamp` | DateTime | Auto-set |

### `users`

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer PK | |
| `name` | String(150) | |
| `email` | String(200) unique | |
| `role` | String(50) | admin, engineer, inspector, viewer |

---

## Intelligence Engines

### 1. Health Scoring Engine

File: `app/services/health_engine.py`

```
health_score = 0.40 × age_score
             + 0.30 × inspection_delay_score
             + 0.20 × damage_score
             + 0.10 × maintenance_frequency_score
```

| Component | Description |
|-----------|-------------|
| `age_score` | Logarithmic decay curve scaled to asset design life (road: 20 yrs, bridge: 50 yrs) |
| `inspection_delay_score` | Days overdue vs. standard interval per asset type |
| `damage_score` | Avg damage level from logs (0–10 scale) + citizen report count penalty |
| `maintenance_score` | Days since last maintenance vs. standard interval |

**Classification:**

| Score | Risk Level | Color |
|-------|-----------|-------|
| 0 – 30 | Healthy | 🟢 Green |
| 31 – 60 | Warning | 🟡 Yellow |
| 61 – 100 | Critical | 🔴 Red |

---

### 2. Risk Propagation Engine

File: `app/services/risk_propagation.py`

Uses **BFS graph traversal** to model how critical asset failures cascade through the network.

```
Critical Asset (score ≥ 61)
    └─→ Direct Neighbor        risk_delta = source_score × 0.70¹ × 0.30
            └─→ Second Hop     risk_delta × 0.70²
                    └─→ Third Hop (max depth = 3)
```

**Rules:**
- Only assets with `health_score ≥ 61` propagate risk
- Risk decays 30% per connection hop
- Max propagation depth: 3 hops
- Max risk contribution per asset: +40 points
- Multi-source propagation takes the maximum delta

**Example cascade:**
```
Pipeline (critical, 78.0) → Road A (receives +16.8) → Road B (receives +4.7)
Bridge   (critical, 82.0) → Road A (receives +18.9) → Road B capped at 40.0
```

---

### 3. Maintenance Priority Engine

File: `app/services/priority_engine.py`

```
priority_score = 0.40 × safety_risk
               + 0.30 × population_impact
               + 0.20 × infrastructure_importance
               + 0.10 × cost_urgency
```

**Action Matrix:**

| Condition | Recommended Action |
|-----------|-------------------|
| Critical + High Impact | 🚨 EMERGENCY: Immediate shutdown & repair |
| Critical + Lower Impact | ⚠️ URGENT: Schedule repair within 7 days |
| Warning + High Impact | 🔶 HIGH PRIORITY: Plan repair within 30 days |
| Warning / Healthy | 📋 SCHEDULE/MONITOR: Review within 90 days |

---

### 4. Lifecycle Service

File: `app/services/lifecycle_service.py`

Builds a chronological timeline of all lifecycle events per asset:

| Event Type | Icon | Trigger |
|-----------|------|---------|
| construction | 🏗️ | Asset installation_year |
| inspection | 🔍 | Maintenance log (damage_level < 4) |
| maintenance | 🔧 | Maintenance log (damage_level 4–7) |
| risk_escalation | ⚠️ | Maintenance log (damage_level ≥ 7) |
| citizen_report | 📢 | Citizen report submitted |

Also computes asset **age profile**: current age, design life, % life consumed, lifecycle stage (new / mature / aging / end_of_life).

---

## Installation Guide

### Prerequisites

- Python 3.10+
- pip

### Step 1 — Clone the project

```bash
git clone <repository-url>
cd urban_infrastructure_portal
```

### Step 2 — Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies

#### Option A — From requirements.txt
```bash
pip install -r requirements.txt
```

#### Option B — Manual installation (grouped)

```bash
# Backend
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install sqlalchemy==2.0.23
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install python-dotenv==1.0.0
pip install aiosqlite==0.19.0
pip install greenlet==3.0.3

# Frontend
pip install streamlit==1.29.0
pip install plotly==5.18.0
pip install pydeck==0.8.0
pip install pandas==2.1.4
pip install numpy==1.26.2

# Utilities
pip install httpx==0.25.2
pip install requests==2.31.0
pip install faker==20.1.0

# Testing
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
```

#### Option C — One-liner

```bash
pip install fastapi==0.104.1 "uvicorn[standard]==0.24.0" sqlalchemy==2.0.23 pydantic==2.5.0 pydantic-settings==2.1.0 python-dotenv==1.0.0 aiosqlite==0.19.0 greenlet==3.0.3 streamlit==1.29.0 plotly==5.18.0 pydeck==0.8.0 pandas==2.1.4 numpy==1.26.2 httpx==0.25.2 requests==2.31.0 faker==20.1.0 pytest==7.4.3 pytest-asyncio==0.21.1
```

> **Note for Ubuntu/Debian users:** If you see `externally-managed-environment`, add `--break-system-packages` or use a virtual environment.

---

## Running the Application

### Step 1 — Seed the database

```bash
python scripts/seed_database.py
```

This creates 20 realistic city infrastructure assets with maintenance history, citizen reports, and asset connections.

**Expected output:**
```
🏙️  Urban Infrastructure Portal — Database Seeder
====================================================
  ✓ Cleared existing data
  ✓ Seeded 4 users
  ✓ Seeded 20 infrastructure assets
  ✓ Seeded 72 maintenance logs
  ✓ Seeded 38 citizen reports
  ✓ Seeded 14 asset connections
  ✓ Recalculated health scores for 20 assets

✅ Seeding complete!
   Healthy: 8 | Warning: 7 | Critical: 5
```

### Step 2 — Start the API backend

```bash
uvicorn app.main:app --reload
```

- API runs at: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Step 3 — Start the Streamlit frontend

```bash
streamlit run frontend/streamlit_app.py
```

- UI runs at: `http://localhost:8501`

> ⚠️ The API backend must be running before starting the frontend.

---

## API Reference

### Assets

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/assets/` | Create a new infrastructure asset |
| `GET` | `/assets/` | List assets (filter by type, risk_level, department) |
| `GET` | `/assets/{id}` | Get asset with maintenance count + connections |
| `PUT` | `/assets/{id}` | Update asset fields |
| `DELETE` | `/assets/{id}` | Delete asset and all related records |
| `GET` | `/assets/{id}/history` | Full lifecycle timeline + age profile |
| `POST` | `/assets/{id}/recalculate` | Force recalculate health score |
| `POST` | `/assets/connections/` | Create a connection between two assets |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/overview` | City-wide KPIs, type/dept breakdown, recent reports |
| `GET` | `/analytics/network-risk` | Full risk propagation analysis across all assets |
| `GET` | `/analytics/health-trend` | Health scores grouped by installation year |

### Maintenance

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/maintenance/priority` | Ranked maintenance queue with recommended actions |
| `POST` | `/maintenance/logs/` | Submit an inspection / maintenance log |
| `GET` | `/maintenance/logs/{asset_id}` | Get all logs for an asset |
| `POST` | `/maintenance/reports/` | Submit a citizen damage report |
| `GET` | `/maintenance/reports/{asset_id}` | Get all citizen reports for an asset |

### Map

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/map/assets` | All assets as GeoJSON FeatureCollection |
| `GET` | `/map/nearby` | Assets within a radius (lat, lon, radius_km) |
| `GET` | `/map/connections` | All connection edges for network visualization |

---

## Frontend Pages

### 📊 Dashboard
- **KPI cards:** Total assets, Healthy / Warning / Critical counts, Overdue inspections
- **Health distribution:** Donut chart with Network Health Index (NHI) in center
- **By asset type:** Bar chart of average health score per type
- **By department:** Horizontal bar chart of asset counts
- **Network risk panel:** Cascade summary with NHI gauge
- **Recent citizen reports:** Live feed of latest reports

### 🗺️ Map View
- **Pydeck WebGL map** with asset markers color-coded by risk level
- **Filters:** Risk level, asset type
- **Connection overlay:** Toggle lines showing infrastructure dependencies
- **Hover tooltip:** Asset name, type, health score, department
- **Asset table:** Scrollable list below the map

### 🔍 Asset Explorer
- **Asset selector:** Dropdown of all assets
- **Health gauge:** Plotly gauge with delta vs. midpoint
- **Lifecycle profile:** Age bar, % design life consumed, stage label
- **Lifecycle stats:** Event counts by type
- **Connected assets table:** Linked infrastructure with risk levels
- **Lifecycle timeline:** Scrollable colored event log with severity indicators

### 🔧 Maintenance Priority
- **Network cascade banner:** Summary of propagation impact
- **Slider filter:** Show top N assets
- **Risk level filter:** Multi-select
- **Priority bar chart:** Color-coded by risk level with score labels
- **Priority cards:** Styled cards with rank, action badge, score, and recommendation
- **Full data table:** Expandable complete priority list

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_health_engine.py -v
pytest tests/test_priority_engine.py -v
pytest tests/test_assets.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

**Test coverage includes:**

| Test File | What's Tested |
|-----------|--------------|
| `test_health_engine.py` | Age scoring, inspection delay, damage scoring, integration scenarios, boundary conditions |
| `test_priority_engine.py` | Safety risk, population impact, infrastructure importance, cost urgency, full ranking |
| `test_assets.py` | CRUD endpoints, history API, analytics endpoints, map endpoints, maintenance endpoints |

---

## Configuration

Edit `app/config.py` or create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///./urban_infrastructure.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
SECRET_KEY=your-secret-key-here
```

**Switching to PostgreSQL:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/urban_infra
```

---

## Future Improvements

- [ ] **PostgreSQL + Alembic** — Production-grade DB with schema migrations
- [ ] **JWT Authentication** — Role-based access control (admin / engineer / inspector / viewer)
- [ ] **Real-time Alerts** — WebSocket push notifications when assets turn critical
- [ ] **ML Failure Prediction** — Train on historical maintenance data to predict next failure
- [ ] **Budget Optimizer** — Allocate fixed maintenance budget to maximize NHI improvement
- [ ] **City GIS Integration** — Connect to ArcGIS / QGIS / OpenStreetMap live data
- [ ] **Automated Scheduling** — Generate inspection schedules based on risk score and overdue status
- [ ] **PDF Report Generator** — City council-ready infrastructure health reports
- [ ] **Mobile Citizen Portal** — Responsive public-facing damage reporting interface
- [ ] **Multi-city / Multi-tenant** — Namespace isolation for managing multiple cities

---

*Urban Infrastructure Intelligence Portal — Built for Metropolis City Infrastructure Department*
*Version 1.0.0 | Python + FastAPI + Streamlit*
