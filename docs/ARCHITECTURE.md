# System Architecture (Version 2)
## SymptoMap: AI-Powered Disease Intelligence Platform

This document provides a brutal, unvarnished analysis of the SymptoMap V1 architecture and outlines the robust, scalable, enterprise-grade architecture for Version 2.

---

## 1. V1 Architecture: The Brutal Reality

SymptoMap V1 was built as a proof-of-concept. While functional for a hackathon or a small clinic, it fundamentally fails at enterprise scale.

### 1.1. The "Polling" Problem (Client-to-Server)
**Current State:** The V1 React frontend polls the `/outbreaks/all` REST API every 30 seconds to fetch updates.
**The Brutal Reality:** If 10,000 users have the dashboard open, that's 20,000 requests per minute fetching identical, mostly unchanged JSON payloads. This wastes massive amounts of bandwidth, drains mobile batteries, and unnecessarily spikes server CPU. It is an anti-pattern for "real-time" dashboards.

### 1.2. The SQLite Bottleneck (Data Layer)
**Current State:** All data is written to a single `symptomap.db` SQLite file.
**The Brutal Reality:** SQLite locks the entire database on writes. During an outbreak, if 500 hospitals try to submit data concurrently, the database will lock, HTTP requests will timeout, and critical health data will be dropped. Furthermore, SQLite has no native geospatial indexing; determining "cases within 50km of X" requires pulling all records into Python memory and computing distances, which is computationally catastrophic at scale.

### 1.3. The Monolithic Coupling (Backend)
**Current State:** FastAPI serves authentication, data ingestion, reporting, and dashboard APIs from a single monolithic thread pool.
**The Brutal Reality:** A spike in read requests for the dashboard will consume all Uvicorn worker threads, effectively blocking doctors from submitting new life-saving outbreak data. The read-path and write-path are dangerously entangled.

### 1.4. The Missing "Intelligence" (AI/ML)
**Current State:** The system is just a CRUD app on a map.
**The Brutal Reality:** It tells you what happened yesterday, not what will happen tomorrow. There is no predictive capability, no anomaly detection, and no automated risk assessment.

---

## 2. V2 System Design: Enterprise Architecture

To solve the V1 bottlenecks, SymptoMap V2 adopts an **Event-Driven, Microservices Architecture** optimized for high-throughput ingestion and real-time geospatial intelligence.

### 2.1. High-Level Architecture Diagram

```text
[ Clients (Web / Mobile PWA) ]
         │ (HTTPS / WSS)
         ▼
[ API Gateway / Load Balancer (Nginx / Kong) ]
         │
         ├──► (WebSockets) ──► [ Real-time Notification Service (Node.js/Socket.io) ]
         │
         ├──► (REST API) ────► [ Core API Service (FastAPI) ] ──(Writes)──► [ Message Broker (Kafka/RabbitMQ) ]
         │                                   │ (Reads)                            │
         │                                   ▼                                    ▼
         │                        [ Redis Caching Layer ]               [ Data Ingestion Workers (Python) ]
         │                                                                        │
         ▼                                                                        ▼
[ ML & Forecasting Microservice (Python/Ray) ] <──(Batch/Stream)──> [ PostgreSQL + PostGIS (Primary DB) ]
         │                                                                        │
         ▼                                                                        ▼
[ LLM Agentic Framework (LangChain/CrewAI) ] ───────────────────────> [ Data Warehouse (ClickHouse) ] (Optional V3)
```

### 2.2. Core System Design Concepts Applied

#### A. Command Query Responsibility Segregation (CQRS) & Event Queues
- **Write Path:** When a doctor submits a case, the Core API instantly validates it and pushes an event (`case_submitted`) to **Kafka**. The API returns `200 OK` in < 20ms. Background workers consume the Kafka queue, perform heavy geocoding, and write to the database. This guarantees zero data loss during traffic spikes.
- **Read Path:** Dashboards read from a highly optimized, read-only replica of the database, heavily buffered by **Redis**.

#### B. WebSockets for Real-Time State
Instead of polling, clients connect via WebSockets. When the ingestion worker writes a new case to the database, it publishes a message to a Redis Pub/Sub channel. The Real-time Notification Service broadcasts this delta to all connected clients. Clients patch their local state instantly.

#### C. PostGIS for Geospatial Dominance
SQLite is replaced by **PostgreSQL** heavily utilizing the **PostGIS** extension.
- We utilize `GEOMETRY` and `GEOGRAPHY` data types.
- PostGIS enables lightning-fast spatial queries natively in the DB: e.g., `SELECT * FROM outbreaks WHERE ST_DWithin(location, ST_MakePoint(lon, lat), 50000)`.
- R-Tree (GiST) indexing ensures spatial queries execute in milliseconds, even with millions of rows.

#### D. AI & ML Microservices De-coupling
Forecasting models (SEIR, Prophet) are CPU-bound and computationally heavy. They run in a separate Microservice container cluster.
- The ML Service periodically pulls recent data, runs simulations, and writes forecast vectors back to a specific `forecasts` table.
- Agentic LLMs (e.g., automated report generators) operate asynchronously triggered by CRON or specific threshold events, ensuring they never block core HTTP traffic.

#### E. Multi-Tier Caching (Redis)
- **Geospatial Tiles:** Complex heatmap vector calculations are cached in Redis. If 10,000 users look at the National Map, the DB is hit exactly once. The cache is invalidated only when a new case in that region is processed via the Kafka queue.

### 2.3. Tech Stack Upgrades

| Component | V1 (Current) | V2 (Target) | Justification |
| :--- | :--- | :--- | :--- |
| **Database** | SQLite | PostgreSQL + PostGIS | Concurrency, Spatial queries, Reliability |
| **Real-time** | HTTP Polling (30s) | WebSockets (WSS) | Lower latency, reduced server load |
| **Queueing** | None (Synchronous) | Apache Kafka / Redis Streams | Durability during traffic spikes |
| **Caching** | None | Redis | Millisecond dashboard load times |
| **AI/ML** | None | Prophet, XGBoost, LangChain | Predictive capabilities, automated reporting |
| **Auth** | Basic JWT (1 shared pass) | OAuth2.0 / RBAC | Enterprise security, role separation |

### 2.4. Failure Modes & Resilience
- **Database Failure:** Core API continues to accept submissions, buffering them in Kafka. Once DB recovers, workers drain the queue. (Eventual Consistency).
- **ML Node Failure:** Dashboards degrade gracefully, showing historical data while hiding the 'Forecast' tab until ML nodes restart.
- **Traffic Spikes:** API Gateway auto-scales the Core API pods via Kubernetes HPA based on CPU/Queue depth.

---

