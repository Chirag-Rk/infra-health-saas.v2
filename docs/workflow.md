# Workflow Documentation

## Core Workflows

### 1. Asset Onboarding
1. POST `/assets/` with asset metadata
2. System auto-calculates health_score via Health Engine
3. Risk Propagation Engine updates network risk
4. Asset appears on Map View and in Priority Queue

### 2. Maintenance Inspection
1. Inspector visits asset in the field
2. POST `/maintenance/logs/` with damage_level and notes
3. Asset's `last_inspection_date` is automatically updated
4. Health score is recalculated immediately
5. If risk_level changes, cascade propagation updates network

### 3. Citizen Report
1. Citizen reports damage via POST `/maintenance/reports/`
2. Damage report count increases asset's damage_score component
3. Health score recalculates; may trigger risk level change
4. Asset appears higher in Priority Queue

### 4. Priority Decision Making
1. City manager opens Maintenance Priority page
2. System fetches `/maintenance/priority` — ranked by multi-factor score
3. Manager reviews recommended action per asset
4. Resources allocated starting from Rank 1 (highest urgency)

### 5. Network Risk Review
1. Engineer opens `/analytics/network-risk`
2. Review which critical assets are cascading risk to neighbors
3. Identify assets at elevated risk due to connected failures
4. Prioritize systemic repairs to reduce cascade impact
