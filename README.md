# 🌍 SymptoMap V2: AI-Powered Disease Intelligence & Surveillance Platform

![SymptoMap Banner](https://via.placeholder.com/1200x400.png?text=SymptoMap+Version+2)

> **Enterprise Edition (V2):** SymptoMap has evolved from a simple reporting tool (V1) into a massive, real-time epidemiological intelligence engine. Built for Public Health Authorities, Epidemiologists, and Governments to predict, monitor, and mitigate disease outbreaks before they escalate.

---

## 🚀 The Vision

While V1 answered the question *"What happened yesterday?"*, V2 answers the critical question **"What will happen tomorrow?"**

By ingesting high-throughput data streams from hospital EHRs, leveraging WebSockets for sub-second real-time dashboard updates, and utilizing LLM agents and SEIR forecasting models, SymptoMap V2 enables proactive public health interventions.

---

## 🏗️ Enterprise Architecture Highlights

- **Data Layer:** PostgreSQL with **PostGIS** for lightning-fast geospatial vector querying and dynamic heatmap generation.
- **Real-Time Engine:** Kafka/Redis Pub-Sub driving a WebSocket layer, eliminating legacy API polling.
- **Predictive ML:** Python microservices running time-series (Prophet) and compartmental (SEIR) models to forecast outbreak trajectories.
- **Agentic AI:** LangChain-powered autonomous agents that synthesize raw clinical data into executive briefing documents and manage intelligent alert triage.
- **Security:** Strict Role-Based Access Control (RBAC), Row-Level Security for jurisdiction-masking, and OAuth2.0 SSO.

---

## 📚 V2 Technical Documentation

Please refer to the detailed V2 documentation generated for this evolution:

1. [**BRD.md**](./BRD.md) - Comprehensive Business Requirements (20-30 pages of Executive & Functional details).
2. [**PRD.md**](./PRD.md) - Product Requirements and Epic breakdowns for engineering.
3. [**ARCHITECTURE.md**](./ARCHITECTURE.md) - A brutal analysis of V1 flaws and the robust V2 Microservices design.
4. [**DATABASE_SCHEMA.md**](./DATABASE_SCHEMA.md) - PostGIS schema, spatial indexing, and time-series optimizations.
5. [**API_SPEC.md**](./API_SPEC.md) - WebSocket events, Geospatial clustering APIs, and ML forecasting endpoints.
6. [**AGENTS.md**](./AGENTS.md) - The design of the Autonomous LLM agents governing the intelligence layer.
7. [**TASKS.md**](./TASKS.md) - The engineering roadmap to transition from V1 to V2.
8. [**AI_CONTEXT.md**](./AI_CONTEXT.md) - Context rules for AI copilots developing within this repository.

---

## ⚙️ Getting Started (V2 Dev Environment)

*Note: The V2 architecture requires Docker to orchestrate the microservices.*

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/sympto-pulse-map.git
cd sympto-pulse-map

# 2. Start the V2 Infrastructure (Postgres/PostGIS, Redis, Kafka)
docker-compose -f docker-compose.v2.yml up -d db redis broker

# 3. Start the Core API & ML Microservices
docker-compose -f docker-compose.v2.yml up -d core-api ml-service

# 4. Run the frontend development server
cd frontend
npm install
npm run dev
```

---

## 🛡️ License & Compliance

SymptoMap V2 is designed to support HIPAA and GDPR compliance requirements. Open source under the MIT License.


