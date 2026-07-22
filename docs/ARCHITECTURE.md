# System Architecture
## SymptoMap Healthcare Intelligence Platform — V1 Reality and V2 Target Design

This document provides a rigorous technical analysis of the current V1 architecture, identifies its structural bottlenecks at scale, and defines the target V2 enterprise architecture that resolves each bottleneck with established distributed systems patterns.

---

## 1. V1 Architecture: Implemented Reality

SymptoMap V1 is a functional proof-of-concept demonstrating the full surveillance workflow. The current deployment runs a React 18 frontend against a FastAPI async backend backed by SQLite, with 200,000+ seeded disease records across Indian hospitals and real-time communication via WebSockets with a Mock Redis pub/sub layer when a production Redis instance is unavailable.

### 1.1 V1 Architecture Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#1a1a2e', 'primaryTextColor': '#e0e0e0', 'primaryBorderColor': '#4a4a8a', 'lineColor': '#7a7aaa', 'secondaryColor': '#16213e', 'mainBkg': '#0f0f1a', 'textColor': '#e0e0e0', 'fontFamily': 'monospace'}}}%%
graph TD
    subgraph Clients["Client Layer"]
        AdminUI["Admin Command Center\nReact 18 + TypeScript + MapLibre GL"]
        DoctorUI["Doctor Station\nAuthenticated Submission Portal"]
        PublicUI["Public Disease Map\nMapLibre GL + Leaflet"]
        HealthAgent["Health Agent\nhealthzy.app — External"]
    end

    subgraph Gateway["API Gateway — FastAPI Async"]
        Auth["JWT Authentication\nRole: admin / doctor / public"]
        RateLimit["Rate Limiting\n100 req/min per IP"]
        Sanitizer["Input Sanitization\nPydantic v2 + HTML sanitizer"]
    end

    subgraph Routes["API Route Layer"]
        OutbreakRoute["POST /outbreaks/\nGET /outbreaks/all\nGET /outbreaks/stats"]
        DoctorRoute["POST /doctor/outbreak\nPOST /doctor/alert\nGET /doctor/stats"]
        AdminRoute["GET /admin/pending\nPOST /admin/approve\nPOST /broadcasts"]
        StatsRoute["GET /stats/dashboard\nGET /stats/zones\nGET /analytics/*"]
        WSRoute["WS /ws\nWebSocket Event Stream"]
    end

    subgraph Workers["Celery AI Worker Cluster"]
        Summarizer["Outbreak Summarizer\nLLM-based AI summary generation"]
        Triage["Triage Agent\nSeverity scoring + prioritization"]
        ZoneAgent["Epidemiological Zoning Agent\nRisk zone classification by density"]
        AQIAgent["AQI Intelligence Agent\nViral fever risk prediction from AQI data"]
    end

    subgraph Data["Data Layer"]
        SQLite[("SQLite — symptomap.db\n200,002 records\ndoctor_outbreaks + hospitals")]
        MockRedis["Mock Redis / Redis\nPub-Sub + Task Queue\nFallback: in-memory"]
        AuditDB["Audit Log Table\nAll write operations tracked"]
    end

    AdminUI & DoctorUI & PublicUI --> Auth
    HealthAgent -->|"Outbreak alert subscription"| WSRoute
    Auth --> RateLimit --> Sanitizer
    Sanitizer --> OutbreakRoute & DoctorRoute & AdminRoute & StatsRoute
    OutbreakRoute & DoctorRoute --> SQLite
    OutbreakRoute & DoctorRoute -->|"Enqueue AI task"| MockRedis
    StatsRoute & AdminRoute --> SQLite
    MockRedis -->|"Consume task"| Workers
    Workers --> SQLite
    Workers -->|"Publish event"| MockRedis
    MockRedis --> WSRoute
    WSRoute -->|"Push delta"| AdminUI & PublicUI & HealthAgent
    SQLite --> AuditDB
```

### 1.2 V1 Bottlenecks at Scale

| Bottleneck | V1 Reality | Impact at Scale |
|:---|:---|:---|
| Polling anti-pattern | Frontend polls `/outbreaks/all` every 30 seconds | 10,000 active users = 20,000 requests/minute fetching unchanged JSON |
| SQLite write locks | Single-file DB locks on every write | 500 concurrent doctor submissions cause lock contention and request timeouts |
| Monolithic read/write path | Dashboard reads and outbreak writes share the same Uvicorn worker pool | Dashboard traffic starves the write path; critical outbreak data is delayed |
| No predictive intelligence | System is a CRUD map — it shows what happened, not what will happen | Zero outbreak forecasting; no anomaly detection; reactive not proactive |
| Mock Redis | In-memory Redis replacement resets on restart | No message durability; tasks lost on process restart in local dev |

---

## 2. V2 Target Architecture: Enterprise Design

V2 adopts an event-driven, microservices architecture with Command Query Responsibility Segregation (CQRS), resolving each V1 bottleneck with a proven distributed systems pattern.

### 2.1 V2 Architecture Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#1a1a2e', 'primaryTextColor': '#e0e0e0', 'primaryBorderColor': '#4a4a8a', 'lineColor': '#7a7aaa', 'secondaryColor': '#16213e', 'mainBkg': '#0f0f1a', 'textColor': '#e0e0e0', 'fontFamily': 'monospace'}}}%%
graph TD
    subgraph Clients["Client Layer"]
        Web["Web App\nReact 18 + PWA"]
        Mobile["Native Mobile\niOS / Android"]
        HealthAgent["Health Agent\nhealthzy.app"]
    end

    subgraph EdgeLayer["Edge and Load Balancing"]
        CDN["CDN\nCloudflare / Vercel Edge"]
        LB["API Gateway / Load Balancer\nNginx / Kong"]
    end

    subgraph CommandPath["Write Path — Command Side (CQRS)"]
        WriteAPI["Core Ingestion API\nFastAPI — Write-Optimized"]
        EventBus["Event Bus\nApache Kafka / Redis Streams"]
        IngestionWorkers["Data Ingestion Workers\nPython — Kafka Consumers"]
    end

    subgraph QueryPath["Read Path — Query Side (CQRS)"]
        ReadAPI["Read API Service\nFastAPI — Read-Optimized"]
        ReadReplica[("Read Replica\nPostgreSQL — Async Replication")]
        TileCache["Geospatial Tile Cache\nRedis — Heatmap vector cache\nInvalidated per-region on new event"]
    end

    subgraph RealtimePath["Real-Time Path"]
        WSService["WebSocket Notification Service\nNode.js / Socket.io"]
        PubSub["Redis Pub/Sub\nEvent fan-out to clients"]
    end

    subgraph DataLayer["Primary Data Layer"]
        PrimaryDB[("PostgreSQL + PostGIS\nPrimary Write DB\nSpatial indexes on GEOGRAPHY columns\nST_DWithin for radius queries")]
    end

    subgraph AILayer["AI and ML Services"]
        CeleryCluster["Celery Worker Cluster\nSummarizer + Triage + Zoning + AQI"]
        MLService["ML Forecasting Microservice\nSEIR model + Prophet time-series\nRay distributed compute"]
        LLMAgents["LLM Agentic Layer\nLangGraph orchestration\nGPT-4o + Claude + Grok failover"]
    end

    subgraph Monitoring["Observability"]
        Metrics["Metrics\nPrometheus + Grafana"]
        Tracing["Distributed Tracing\nOpenTelemetry + Jaeger"]
        AuditLog["Audit Trail\nImmutable append-only log"]
    end

    Web & Mobile & HealthAgent --> CDN --> LB
    LB -->|"Writes — doctor submissions, reports"| WriteAPI
    LB -->|"Reads — dashboard, map, analytics"| ReadAPI
    LB -->|"WebSocket upgrade"| WSService

    WriteAPI -->|"Validates, returns 200ms"| EventBus
    EventBus --> IngestionWorkers
    IngestionWorkers --> PrimaryDB
    IngestionWorkers -->|"Triggers AI pipeline"| CeleryCluster
    IngestionWorkers -->|"Publishes OUTBREAK_REPORTED event"| PubSub

    ReadAPI --> TileCache
    TileCache -->|"Cache miss"| ReadReplica
    PrimaryDB -->|"Async replication"| ReadReplica
    TileCache -->|"Cache invalidation on event"| PubSub

    CeleryCluster --> PrimaryDB
    CeleryCluster -->|"Triggers on threshold"| LLMAgents
    MLService -->|"Batch forecast writes"| PrimaryDB
    LLMAgents -->|"Advisory content"| PubSub

    PubSub --> WSService
    WSService -->|"Delta push — no polling"| Web & Mobile & HealthAgent

    WriteAPI & ReadAPI & WSService --> Metrics & Tracing
    PrimaryDB --> AuditLog
```

### 2.2 Core Design Patterns Applied

**CQRS — Command Query Responsibility Segregation**
The write path (doctor submissions, outbreak reports) is completely separated from the read path (dashboard queries, map data). The Core Ingestion API validates and acknowledges a submission in under 20ms by publishing to the event bus — it never waits for the database write to complete. Background workers drain the event queue and persist data. Dashboards read from a read-optimized replica, never touching the primary write database.

**Event-Driven Architecture with Kafka**
Every outbreak submission produces an immutable event to the Kafka topic. This gives: (a) zero data loss during traffic spikes — the queue absorbs all writes while workers process at their own rate; (b) full replay capability — if an AI agent is upgraded, it can reprocess all historical events; (c) decoupled consumers — adding a new downstream service (e.g., a new notification channel) requires no changes to the ingestion API.

**PostGIS for Geospatial Query Performance**
SQLite is replaced by PostgreSQL with the PostGIS extension. All location data is stored as native `GEOGRAPHY(POINT, 4326)` columns with GiST (R-Tree) spatial indexes. A query like "find all outbreaks within 50km of a given coordinate" executes as a single indexed spatial query (`ST_DWithin`) in milliseconds on millions of rows — versus pulling all records into Python memory in V1.

**Multi-Tier Redis Caching for Geospatial Tiles**
Heatmap vector calculations are expensive. In V2, the computed GeoJSON tile for each viewport region is cached in Redis with a region-keyed TTL. Ten thousand simultaneous dashboard users hitting the same national map view result in exactly one database query. Cache entries are selectively invalidated only when a new outbreak event lands in that specific geographic region, via the Pub/Sub event stream.

**WebSocket Push Replacing Polling**
Clients connect once via WebSocket. When the event bus processes a new outbreak, it publishes a delta event to Redis Pub/Sub. The WebSocket Notification Service fans this out to all connected clients. Clients apply the delta to their local state in-place. No polling. No redundant full-payload fetches.

**ML Microservice Decoupling**
Forecasting models (SEIR epidemiological simulation, Prophet time-series) are CPU-bound and take seconds to minutes to run. In V2 they run in a dedicated ML microservice cluster managed by Ray for distributed compute. The ML service periodically writes forecast records to a dedicated `predictions` table. If the ML cluster fails, the surveillance dashboard degrades gracefully — it hides the forecast tab and shows historical data. Core outbreak reporting is entirely unaffected.

### 2.3 Tech Stack: V1 to V2 Upgrade Path

| Component | V1 Current | V2 Target | Justification |
|:---|:---|:---|:---|
| Database | SQLite (file lock on write) | PostgreSQL + PostGIS | Concurrent writes, spatial indexing, replication |
| Real-time | HTTP polling every 30 seconds | WebSockets + Redis Pub/Sub | Zero-latency deltas, no redundant bandwidth |
| Message Queue | Celery + Mock Redis | Apache Kafka / Redis Streams | Durable event log, zero data loss on restart |
| Caching | None | Redis multi-tier (tile + query) | Sub-millisecond dashboard reads at scale |
| AI/ML | Synchronous Celery tasks | Ray distributed ML microservice | CPU-bound forecasting isolated from API latency |
| LLM Orchestration | Direct calls in worker threads | LangGraph stateful agent framework | Stateful multi-turn reasoning, prompt versioning |
| Auth | JWT shared password | OAuth 2.0 + RBAC with per-doctor tokens | Enterprise security, individual accountability |
| Observability | Print statements | Prometheus + Grafana + OpenTelemetry | Production alerting and distributed tracing |
| Deployment | Single Uvicorn process | Kubernetes with HPA auto-scaling | Horizontal scale on demand, zero-downtime deploys |

### 2.4 Failure Mode Analysis

| Failure | V1 Behavior | V2 Behavior |
|:---|:---|:---|
| Database becomes unavailable | All API endpoints return 500; submissions are lost | Write API continues accepting submissions into Kafka queue; data is persisted once DB recovers (eventual consistency) |
| ML service crashes | None (no ML service) | Dashboard hides forecast tab; real-time surveillance continues unaffected |
| Redis unavailable | Falls back to Mock Redis (in-memory, resets on restart) | WebSocket push degrades to client-side polling fallback; no data loss |
| Traffic spike (10x normal load) | Uvicorn workers exhaust; requests queue or timeout | Kubernetes HPA scales API pods based on CPU and Kafka queue depth; event bus absorbs write burst |
| Single AI worker crashes | Task is lost | Kafka consumer group rebalances; another worker picks up the task from the committed offset |

---

## 3. Health Agent Architecture Integration

The Health Agent at [healthzy.app](https://healthzy.app/) connects to SymptoMap as an event consumer via the WebSocket bridge. In V2, this becomes a dedicated integration point:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#1a1a2e', 'primaryTextColor': '#e0e0e0', 'lineColor': '#7a7aaa', 'mainBkg': '#0f0f1a', 'textColor': '#e0e0e0', 'fontFamily': 'monospace'}}}%%
sequenceDiagram
    participant SM as SymptoMap Event Bus
    participant Bridge as Integration Bridge API
    participant HA as Health Agent LangGraph
    participant LLM as Multi-LLM Layer
    participant User as Patient

    SM->>Bridge: OUTBREAK_APPROVED event (disease, location, severity)
    Bridge->>Bridge: Geocode affected radius
    Bridge->>HA: POST /api/outbreak-context (structured alert payload)
    HA->>HA: Identify active sessions in affected area
    HA->>LLM: Inject outbreak context into session state
    LLM-->>HA: Updated recommendations with outbreak awareness
    HA->>User: Real-time advisory: outbreak in your area, avoid X, do Y
```

This integration ensures that when a doctor reports a severe outbreak in Mumbai via SymptoMap, every active Health Agent consultation session for a user in the affected radius receives contextual outbreak awareness injected into their ongoing diagnostic session — without the user needing to do anything.
