# API Specification (Version 2)
## SymptoMap: AI-Powered Disease Intelligence Platform

This document outlines the OpenAPI specifications for the newly decoupled V2 microservices architecture, specifically focusing on the advanced analytical and real-time endpoints.

---

## 1. Real-Time WebSockets

### `WS /api/v2/ws/updates`
**Description:** Connects the client to the real-time notification broker (Redis Pub/Sub -> Socket.io/FastAPI).
**Auth:** Requires valid JWT passed as a query parameter `?token=...`
**Events Emitted by Server:**
- `NEW_OUTBREAK`: Fired when a new case is ingested and validated.
- `ALERT_TRIGGERED`: Fired when a threshold is breached.
- `CLUSTER_UPDATED`: Fired when the ML engine identifies a new geospatial cluster.

---

## 2. Geospatial Intelligence API (Core Service)

### `GET /api/v2/geo/clusters`
**Description:** Retrieves algorithmically generated disease clusters utilizing PostGIS `ST_ClusterDBSCAN`.
**Parameters:**
- `disease_type` (string, optional)
- `bbox` (string, required): Bounding box coordinates `[min_lon, min_lat, max_lon, max_lat]`
- `eps_meters` (integer, default 5000): The maximum distance between two cases to be considered in the same cluster.

**Response:** (GeoJSON format)
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[...]]]
      },
      "properties": {
        "cluster_id": 42,
        "disease": "Dengue",
        "case_count": 145,
        "risk_level": "CRITICAL"
      }
    }
  ]
}
```

### `GET /api/v2/geo/heatmap`
**Description:** Returns aggregated density matrices for rapid heatmap rendering on the client.
**Parameters:**
- `zoom_level` (integer, required): To dictate aggregation granularity.
- `bbox` (string, required).

---

## 3. ML Forecasting Service (ML Microservice)

### `POST /api/v2/ml/forecast/seir`
**Description:** Triggers a SEIR compartmental model simulation.
**Auth:** Role `epidemiologist` or `admin`.

**Request:**
```json
{
  "disease_type": "Cholera",
  "region_id": "DIST-104",
  "days_to_simulate": 30,
  "parameters": {
    "R0": 1.8,
    "incubation_period_days": 2.5,
    "recovery_rate": 0.14
  }
}
```

**Response:**
```json
{
  "simulation_id": "sim_892nf",
  "peak_infection_date": "2026-07-15",
  "estimated_peak_cases": 14500,
  "daily_projections": [
    { "date": "2026-06-25", "susceptible": 90000, "exposed": 500, "infectious": 150, "recovered": 20 }
    // ... 30 days of data
  ]
}
```

---

## 4. Autonomous Agent API (AI Service)

### `POST /api/v2/ai/summarize-cluster`
**Description:** Utilizes an LLM to generate an executive summary of a specific geographic outbreak cluster, incorporating local news, weather, and clinical data.

**Request:**
```json
{
  "cluster_id": 42,
  "target_audience": "EXECUTIVE",
  "include_recommendations": true
}
```

**Response:**
```json
{
  "summary": "A rapid cluster of 145 Dengue cases has emerged in the Jaipur region over the last 48 hours. This correlates strongly with unseasonably heavy monsoon rains (↑40% precipitation).",
  "recommendations": [
    "Deploy vector control units to Zone B.",
    "Increase blood bank reserves at SMS Hospital by 20%."
  ],
  "confidence_score": 0.92
}
```

---

## 5. Ingestion API

### `POST /api/v2/ingest/hl7-fhir`
**Description:** High-throughput endpoint for automated hospital EHR integrations. Pushes data directly to Kafka.
**Auth:** Requires machine-to-machine OAuth2 token.

**Response:** `202 Accepted` (Processed asynchronously).
