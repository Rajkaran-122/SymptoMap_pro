# Product Requirements Document (PRD)
## SymptoMap: AI-Powered Disease Intelligence & Surveillance Platform
**Version:** 2.0 (Evolution from V1)
**Date:** June 2026

---

## 1. Product Vision & Scope
SymptoMap V2 bridges the gap between reactive healthcare reporting and proactive epidemiological intelligence. The product aims to deliver real-time data ingestion, predictive machine learning models, and actionable geospatial dashboards to help governments and health organizations mitigate disease outbreaks before they escalate.

**Scope of V2:**
- Migration from SQLite to scalable PostgreSQL/PostGIS.
- Replacement of 30-second client polling with WebSocket real-time updates.
- Introduction of an AI/ML microservice for automated forecasting (SEIR) and risk assessment.
- Enhanced Role-Based Access Control (RBAC) and data segmentation.
- Comprehensive alerting system based on user-defined and AI-generated thresholds.

---

## 2. Target Audience & Personas
1. **Epidemiologists:** Need complex data export, SEIR model tweaking, and forecasting visualizations.
2. **Public Health Officers:** Need local alerts, regional heatmaps, and resource impact estimates.
3. **Hospital Administrators:** Need to report cases quickly and receive alerts on incoming patient surges.
4. **Data Entry Staff / Doctors:** Need a rapid, frictionless way to log new cases (upgrading the V1 portal).

---

## 3. Features & Requirements

### 3.1. Real-Time Data Ingestion & Sync (Epic 1)
**Description:** The system must process incoming disease reports instantly without overwhelming the database.
- **Req 1.1:** Implement an API Gateway to handle high-throughput case submissions.
- **Req 1.2:** Integrate a message broker (e.g., Kafka or RabbitMQ) to decouple ingestion from database writes.
- **Req 1.3:** Clients (Dashboard) must receive updates via WebSockets (Socket.io/FastAPI WebSockets) instead of polling.
- **Acceptance Criteria:** A submitted case appears on active dashboards worldwide in < 1 second.

### 3.2. Advanced Geospatial Analytics (Epic 2)
**Description:** V1 map markers are insufficient for enterprise intelligence.
- **Req 2.1:** Integrate PostGIS for native spatial querying.
- **Req 2.2:** Support for dynamic heatmaps based on case density.
- **Req 2.3:** Spatial clustering using DBSCAN to automatically group nearby cases into "Active Outbreak Zones."
- **Acceptance Criteria:** Map renders >100,000 data points smoothly using vector tiles (e.g., Mapbox/Deck.gl).

### 3.3. Predictive AI & ML Microservices (Epic 3)
**Description:** Shift from historical reporting to predictive intelligence.
- **Req 3.1:** Deploy a dedicated Python microservice running Prophet (time-series) and SEIR models.
- **Req 3.2:** Generate 14-day and 30-day case trajectory forecasts for active clusters.
- **Req 3.3:** NLP summarization of weekly outbreak data into short executive briefs.
- **Acceptance Criteria:** The Forecast Dashboard successfully displays the R0 (reproduction number) and trajectory curve for major diseases daily.

### 3.4. Smart Alerting Engine (Epic 4)
**Description:** Users need to know when action is required without staring at a dashboard.
- **Req 4.1:** Users can create custom thresholds (e.g., "Alert me if Dengue cases > 50 in 24 hours in Jaipur").
- **Req 4.2:** AI-generated anomaly alerts (e.g., "Unusual 300% spike in respiratory symptoms detected in Zone 4").
- **Req 4.3:** Multi-channel delivery (Email, SMS, In-App push notifications).
- **Acceptance Criteria:** Alerts fire within 1 minute of a threshold breach.

### 3.5. Enterprise Security & RBAC (Epic 5)
**Description:** V1 single-password architecture must be replaced.
- **Req 5.1:** Implement JWT-based Auth with refresh tokens and SSO integration (SAML/OAuth).
- **Req 5.2:** Role-based access: Admin, Epidemiologist, Regional Officer, Reporter, Viewer.
- **Req 5.3:** Row-level security to ensure Regional Officers only see PII for their jurisdiction.
- **Acceptance Criteria:** Penetration testing validates that cross-tenant data access is blocked.

---

## 4. UI / UX Requirements
- **Design System:** Transition to a comprehensive design system (e.g., Shadcn UI + Tailwind) customized for high data-density interfaces (dark mode optimized for long surveillance sessions).
- **Responsiveness:** The Reporter portal must be mobile-first (PWA) for rural clinics. Dashboards must be optimized for 1080p+ widescreen monitors in command centers.

---

## 5. Metrics & Telemetry
- Track User Session Time (especially on Dashboards).
- API Latency (< 200ms target).
- ML Model Drift (monitor forecasting accuracy vs. actuals over time).
- Alert Open/Acknowledge Rates.

---

## 6. Release Phases
- **Phase 1 (Month 1-2):** Database migration (SQLite to PostgreSQL/PostGIS), Auth implementation, and WebSocket real-time layer.
- **Phase 2 (Month 3-4):** Dashboard UI overhaul, Heatmaps, and Clustering algorithms.
- **Phase 3 (Month 5-6):** AI/ML Microservice deployment, Forecasting engine, and Smart Alerts.
