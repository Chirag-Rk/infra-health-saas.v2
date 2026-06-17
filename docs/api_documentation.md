# API Documentation — Urban Infrastructure Intelligence Portal

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## Assets

### POST /assets/
Create a new infrastructure asset.

**Request Body:**
```json
{
  "asset_name": "Main Street Bridge",
  "asset_type": "bridge",
  "department": "Public Works",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "installation_year": 1985,
  "status": "active",
  "last_inspection_date": "2023-06-15"
}
```
**Response:** `201 Created` with asset object including computed `health_score` and `risk_level`.

---

### GET /assets/
List all infrastructure assets with optional filters.

**Query Params:**
- `asset_type` (string): road, bridge, pipeline, drainage, street_light, public_facility
- `risk_level` (string): healthy, warning, critical
- `department` (string)
- `skip` / `limit` (int)

---

### GET /assets/{id}
Get full asset details including maintenance count, citizen report count, and connected asset IDs.

---

### PUT /assets/{id}
Update asset fields.

---

### DELETE /assets/{id}
Delete an asset and all its related records.

---

### GET /assets/{id}/history
Get full lifecycle timeline for an asset.

**Response:**
```json
{
  "asset_id": 1,
  "asset_name": "Main Street Bridge",
  "timeline": [
    {
      "event_type": "construction",
      "date": "1985-01-01",
      "title": "Asset Installed: Main Street Bridge",
      "description": "Bridge constructed and commissioned.",
      "icon": "🏗️",
      "severity": "info"
    }
  ],
  "stats": {
    "total_events": 12,
    "inspections": 5,
    "maintenance_actions": 3,
    "citizen_reports": 4,
    "risk_escalations": 0
  },
  "age_profile": {
    "current_age_years": 39,
    "design_life_years": 50,
    "remaining_life_years": 11,
    "percent_life_used": 78.0,
    "lifecycle_stage": "aging"
  }
}
```

---

## Analytics

### GET /analytics/overview
Returns city-wide infrastructure summary.

**Response:**
```json
{
  "summary": {
    "total_assets": 20,
    "healthy": 8,
    "warning": 7,
    "critical": 5,
    "overdue_inspections": 3,
    "network_health_index": 62.4,
    "avg_health_score": 37.6
  },
  "by_type": [...],
  "by_department": [...],
  "recent_citizen_reports": [...]
}
```

---

### GET /analytics/network-risk
Returns full network risk propagation analysis.

**Response:**
```json
{
  "summary": {
    "total_assets": 20,
    "directly_critical": 5,
    "propagation_affected": 8,
    "risk_escalated": 3,
    "network_health_index": 62.4
  },
  "asset_risks": [
    {
      "asset_id": 1,
      "original_score": 78.2,
      "propagated_delta": 12.5,
      "adjusted_score": 90.7,
      "risk_level": "critical",
      "adjusted_risk_level": "critical",
      "propagated_from": [...]
    }
  ]
}
```

---

## Maintenance

### GET /maintenance/priority
Returns ranked maintenance priority queue.

**Response:**
```json
[
  {
    "rank": 1,
    "asset_id": 13,
    "asset_name": "Old Mill Bridge",
    "asset_type": "bridge",
    "risk_level": "critical",
    "health_score": 82.5,
    "priority_score": 87.3,
    "recommended_action": "EMERGENCY: Immediate shutdown & repair",
    "department": "Public Works"
  }
]
```

---

### POST /maintenance/logs/
Add a maintenance/inspection log for an asset.

**Request Body:**
```json
{
  "asset_id": 1,
  "inspection_date": "2024-03-01",
  "inspector": "James Carter",
  "condition_notes": "Surface cracks detected",
  "damage_level": 4.5,
  "maintenance_action": "Filled cracks with epoxy"
}
```

---

### POST /maintenance/reports/
Submit a citizen damage report.

---

## Map

### GET /map/assets
Returns all assets as a GeoJSON FeatureCollection with color-coded markers.

**Query Params:** `risk_level`, `asset_type`

---

### GET /map/nearby
Find assets within a radius.

**Query Params:** `lat`, `lon`, `radius_km`

---

### GET /map/connections
Returns all asset connection edges for network graph visualization.
