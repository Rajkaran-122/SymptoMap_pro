# SymptoMap: Low-Level Design (LLD)

This document details the micro-interactions, data models, agent workflows, and API contracts that power the SymptoMap platform.

## 1. Doctor Outbreak Submission & Approval Pipeline

This diagram illustrates how a doctor's outbreak report moves through the AI triage phase, into the admin approval workflow, and finally to verified status and real-time broadcast.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#111111', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'secondaryColor': '#222222', 'tertiaryColor': '#000000', 'mainBkg': '#000000', 'textColor': '#ffffff', 'fontFamily': 'monospace'}}}%%
sequenceDiagram
    participant Doctor as Doctor (Authenticated)
    participant API as FastAPI Backend
    participant DB as SQLite / PostgreSQL
    participant Redis as Redis / Mock Redis
    participant Celery as Celery AI Workers
    participant Admin as Admin Command Center
    participant Public as Public Map + Health Agent

    Doctor->>API: 1. POST /api/v1/doctor/outbreak (JWT Token)
    API->>API: 2. Validate via Pydantic + Sanitize Input
    API->>DB: 3. INSERT doctor_outbreaks (status: pending)
    API->>Redis: 4. Enqueue: summarize_outbreak_task + triage_alert_task

    Redis-->>Celery: 5. Consume Tasks (async)
    Note over Celery: Summarizer generates AI summary<br/>Triage scores severity<br/>Zoning agent updates risk zones

    Celery->>DB: 6. Update record (ai_summary, severity_score)
    Celery->>Redis: 7. Publish Event: NEW_OUTBREAK

    Redis-->>Admin: 8. WebSocket Live Update (new pin on map)
    Admin->>API: 9. GET /api/v1/admin/pending (review queue)
    Admin->>API: 10. POST /api/v1/admin/approve/{id}
    API->>DB: 11. UPDATE status: approved, verified: true
    API->>Redis: 12. Publish Event: OUTBREAK_APPROVED

    Redis-->>Public: 13. WebSocket → Map refreshes
    Redis-->>Public: 14. Health Agent receives outbreak warning → alerts nearby users
```

## 2. Health Agent Consultation Flow (Sequence Diagram)

This flow shows how the AI Health Agent receives an outbreak warning from SymptoMap and integrates it into a user consultation.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#111111', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'secondaryColor': '#222222', 'tertiaryColor': '#000000', 'mainBkg': '#000000', 'textColor': '#ffffff', 'fontFamily': 'monospace'}}}%%
sequenceDiagram
    participant User as Patient (Voice/Image/Text)
    participant HA as Health Agent (healthzy.app)
    participant LangGraph as LangGraph Orchestrator
    participant LLM as Multi-LLM (GPT-4o → Claude → Grok)
    participant SM as SymptoMap WebSocket Bridge
    participant DB as MongoDB (Health Records)

    User->>HA: 1. Input: voice/image/text symptoms
    HA->>LangGraph: 2. Start clinical interview session
    LangGraph->>LLM: 3. Patient intake + adaptive questioning
    LLM-->>LangGraph: 4. Follow-up questions (failover if needed)

    SM-->>HA: 5. ASYNC: Outbreak alert for user's area
    HA->>LangGraph: 6. Inject outbreak context into session

    LangGraph->>LLM: 7. Differential diagnosis with outbreak context
    LLM-->>LangGraph: 8. Top-3 diagnoses with confidence scores
    LangGraph->>LLM: 9. Generate SOAP note + recommendations
    LLM-->>LangGraph: 10. SOAP note + localized advisory

    LangGraph->>DB: 11. Store health record (encrypted)
    LangGraph->>HA: 12. Return complete diagnostic report
    HA->>User: 13. Display report + outbreak warning + next steps
```

## 3. Core Entity-Relationship Diagram (Database Schema)

The database schema supports both the SYMPTOMAP disease surveillance data and the extended air quality intelligence feature.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#111111', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'secondaryColor': '#222222', 'tertiaryColor': '#000000', 'mainBkg': '#000000', 'textColor': '#ffffff', 'fontFamily': 'monospace'}}}%%
erDiagram
    USERS ||--o{ DOCTOR_OUTBREAKS : submits
    USERS ||--o{ OUTBREAKS : reports
    HOSPITALS ||--o{ OUTBREAKS : hosts
    OUTBREAKS ||--o{ PREDICTIONS : generates
    ZONES ||--o{ ALERTS : targets
    ZONES ||--o{ AQI_SIGNALS : contains

    USERS {
        uuid id PK
        string email
        string full_name
        string role "admin, doctor, public"
        string hashed_password
        timestamp created_at
    }

    HOSPITALS {
        uuid id PK
        string name
        string address
        float latitude
        float longitude
        string city
        string state
        string country
        int total_beds
        int icu_beds
        string hospital_type
        timestamp created_at
    }

    OUTBREAKS {
        uuid id PK
        uuid hospital_id FK
        uuid reported_by FK
        string disease_type
        int patient_count
        string severity "mild, moderate, severe"
        boolean verified
        float latitude
        float longitude
        timestamp date_started
        timestamp date_reported
        json symptoms
        text notes
    }

    DOCTOR_OUTBREAKS {
        uuid id PK
        string disease_type
        int patient_count
        string severity "mild, moderate, severe"
        float latitude
        float longitude
        string location_name
        string city
        string state
        string status "pending, approved, rejected"
        string submitted_by
        timestamp date_reported
        text description
        text ai_summary
    }

    PREDICTIONS {
        uuid id PK
        uuid reference_outbreak_id FK
        string disease_type
        string zone_name
        timestamp prediction_date
        int predicted_cases
        int risk_score
        string risk_level "safe, low, medium, high, critical"
        int probability_of_spread
        string model_version
    }

    ZONES {
        uuid id PK
        string name
        string health_risk_level "mild, moderate, severe"
        string predicted_threat
        float center_lat
        float center_lng
        float radius_km
        timestamp created_at
    }

    ALERTS {
        uuid id PK
        string alert_type "outbreak, high_risk, critical"
        string severity "info, warning, critical"
        string title
        text message
        string zone_name
        json recipients
        json delivery_status
        timestamp sent_at
        timestamp expires_at
    }

    AQI_SIGNALS {
        uuid id PK
        float latitude
        float longitude
        float aqi_value
        string attributed_source
        float ai_confidence
        string status "PENDING, APPROVED, REJECTED"
        timestamp recorded_at
    }
```

## 4. API Specification Highlights

### `POST /api/v1/doctor/outbreak`
- **Auth**: JWT Bearer token (Doctor or Admin role)
- **Purpose**: High-speed outbreak submission from doctor portal
- **Handling**: Validates via Pydantic, inserts to `doctor_outbreaks`, triggers Celery AI tasks
- **Response**: `{ id, hospital_name, disease_type, patient_count, severity, message }`

### `GET /api/v1/outbreaks/all`
- **Auth**: Public
- **Purpose**: Aggregate outbreak data for the public map and admin dashboard
- **Returns**: Combined records from `doctor_outbreaks` + ORM `outbreaks` table, last 30 days by default
- **Params**: `days`, `severity`, `disease_type`, `limit`

### `GET /api/v1/outbreaks/stats`
- **Auth**: Public
- **Purpose**: Dashboard summary — total reports, pending review, high priority, active cases
- **Returns**: `{ total_reports, pending_review, high_priority, active_cases }` — combining both tables

### `POST /api/v1/admin/approve/{id}`
- **Auth**: Admin JWT only
- **Purpose**: Approval gateway — changes status from `pending` to `approved`, triggers broadcast
- **Effect**: Updates `doctor_outbreaks.status`, publishes `OUTBREAK_APPROVED` WebSocket event

### `GET /api/v1/stats/dashboard`
- **Auth**: Admin JWT
- **Purpose**: Full dashboard statistics including zone counts, weekly comparisons, disease distribution

### `POST /api/v1/broadcasts`
- **Auth**: Admin JWT
- **Purpose**: Create and send a public health advisory broadcast
- **Body**: `{ title, message, severity, target_regions, expires_at }`

### `WS /api/v1/ws`
- **Auth**: None (public WebSocket)
- **Purpose**: Real-time event stream for map updates, new outbreaks, broadcasts, and alerts

## 5. Security Architecture

```
Authentication:  JWT tokens · bcrypt hashing · 24-hour auto-expiry
Authorization:   Role-based (admin / doctor / public) · Endpoint-level guards
Input Safety:    Pydantic v2 validation · HTML sanitization · SQL parameterization
Network:         CORS enforcement · Rate limiting (100 req/min) · HTTPS-only in production
Audit:           All write operations logged to audit_log table with actor, IP, timestamp
Data:            User passwords never stored in plain text · Sensitive fields encrypted at rest
```
