# AeroIntel: Low-Level Design (LLD)

This document details the micro-interactions, data models, and agent workflows that power the AeroIntel platform.

## 1. Enforcement & Approval Pipeline (Sequence Diagram)

This diagram illustrates how a raw pollution signal (or manual inspector report) moves through the AI attribution phase, into the administrative holding pattern, and finally to enforcement.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#111111', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'secondaryColor': '#222222', 'tertiaryColor': '#000000', 'mainBkg': '#000000', 'textColor': '#ffffff', 'fontFamily': 'monospace'}}}%%
sequenceDiagram
    participant Sensor as IoT/Inspector (Client)
    participant API as FastAPI Backend
    participant Redis as Redis Queue
    participant Agent as Attribution Agent (AI)
    participant DB as PostgreSQL/PostGIS
    participant Admin as Govt Command Center

    Sensor->>API: 1. Submit Pollution Signal (Lat, Lon, AQI)
    API->>DB: 2. Save Signal (Status: PENDING)
    API->>Redis: 3. Enqueue Attribution Task
    Redis-->>Agent: 4. Consume Task
    
    Note over Agent: Agent cross-references satellite,<br/>land use, and thermal maps
    
    Agent->>Agent: 5. Calculate Source & Confidence Score
    Agent->>DB: 6. Update Signal (Source, AI_Summary)
    Agent->>Redis: 7. Publish Event (NEW_VIOLATION)
    
    Redis-->>Admin: 8. WebSocket Live Update
    Admin->>API: 9. Review & Approve Enforcement
    API->>DB: 10. Update Status: APPROVED
    API->>Admin: 11. Generate Legal Enforcement Notice
```

## 2. Citizen Health Risk Advisory Flow (Sequence Diagram)

This flow shows how the Epidemiological Zoning Agent predicts a viral fever outbreak based on AQI and triggers localized citizen alerts.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#111111', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'secondaryColor': '#222222', 'tertiaryColor': '#000000', 'mainBkg': '#000000', 'textColor': '#ffffff', 'fontFamily': 'monospace'}}}%%
sequenceDiagram
    participant API as Forecasting Service
    participant ZoneAgent as Epidemiological Agent
    participant DB as PostgreSQL
    participant LLM as Translation LLM
    participant Citizens as Vulnerable Populations

    API->>ZoneAgent: Stream 72hr AQI Forecast
    Note over ZoneAgent: Analyzes AQI + Humidity + History
    ZoneAgent->>DB: Create 'Red' Health Vulnerability Zone (Viral Fever Risk)
    ZoneAgent->>LLM: Request Localized Advisories (Hindi, Tamil, etc.)
    LLM-->>ZoneAgent: Return Translated SMS Copy
    ZoneAgent->>Citizens: Dispatch SMS/Push Notifications
```

## 3. Core Entity-Relationship Diagram (Database Schema)

The database schema is heavily optimized for geospatial queries (via PostGIS extensions) and rapid real-time status updates.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#111111', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'secondaryColor': '#222222', 'tertiaryColor': '#000000', 'mainBkg': '#000000', 'textColor': '#ffffff', 'fontFamily': 'monospace'}}}%%
erDiagram
    USERS ||--o{ ENFORCEMENT_ACTIONS : approves
    ZONES ||--o{ POLLUTION_SIGNALS : contains
    ZONES ||--o{ ALERTS : targets

    POLLUTION_SIGNALS {
        uuid id PK
        float latitude
        float longitude
        float aqi_value
        string attributed_source
        float ai_confidence
        string status "PENDING, APPROVED, REJECTED"
        timestamp recorded_at
    }

    ZONES {
        uuid id PK
        string name
        geometry boundary_polygon
        string health_risk_level "GREEN, YELLOW, RED"
        string predicted_threat "e.g., Viral Fever Surge"
    }

    ALERTS {
        uuid id PK
        string alert_type "SMS, PUSH, EMAIL"
        string message_content
        uuid zone_id FK
        timestamp sent_at
    }

    USERS {
        uuid id PK
        string email
        string role "ADMIN, INSPECTOR, SYSTEM"
    }
    
    ENFORCEMENT_ACTIONS {
        uuid id PK
        uuid signal_id FK
        uuid approved_by FK
        string action_taken
        timestamp action_date
    }
```

## 4. API Specification Highlights

### `POST /api/v1/signals/ingest`
- **Purpose**: High-throughput endpoint for IoT sensors and ground inspectors to log pollution spikes.
- **Handling**: Validates payload via Pydantic, inserts to DB asynchronously, and pushes an event to Redis.

### `GET /api/v1/zones/vulnerability`
- **Purpose**: Fetches the current geospatial multipolygons representing health risk zones for rendering on MapLibre.
- **Returns**: GeoJSON FeatureCollection with embedded metadata (risk_level, predicted_threat).

### `POST /api/v1/admin/enforce/{signal_id}`
- **Purpose**: The approval gateway. Changes a pollution signal's status from PENDING to APPROVED, officially initiating government intervention protocols.
