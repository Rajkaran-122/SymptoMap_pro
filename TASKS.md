# V2 Implementation Tasks & Roadmap

This document outlines the epics and specific engineering tasks required to transition SymptoMap from V1 to the enterprise-grade V2 architecture.

---

## Epic 1: Database Migration & PostGIS (High Priority)
*The foundational layer must be upgraded before any advanced analytics can occur.*

- [ ] **TSK-101:** Provision PostgreSQL database instance (Dev, Staging, Prod).
- [ ] **TSK-102:** Install and configure the `PostGIS` extension on the database.
- [ ] **TSK-103:** Create Alembic/SQLAlchemy migration scripts to generate the V2 schema (including Geometry/Geography columns).
- [ ] **TSK-104:** Write a Python ETL script to migrate historical data from `symptomap.db` (SQLite) to PostgreSQL.
- [ ] **TSK-105:** Update backend repository connection strings and ORM models to support PostgreSQL.

## Epic 2: Real-Time Infrastructure (WebSockets & Pub/Sub)
*Replacing the 30-second polling bottleneck.*

- [ ] **TSK-201:** Provision a Redis instance for Pub/Sub messaging.
- [ ] **TSK-202:** Refactor the FastAPI `POST /outbreak` endpoint to publish an event to Redis upon successful DB write.
- [ ] **TSK-203:** Implement a FastAPI WebSocket (`/ws/updates`) endpoint to broadcast Redis events to connected clients.
- [ ] **TSK-204:** Update React Frontend to connect to the WebSocket and patch the Redux/Zustand state incrementally instead of polling.
- [ ] **TSK-205:** Implement WebSocket connection retry and fallback mechanisms in the frontend.

## Epic 3: Enterprise Auth & RBAC
*Replacing the single shared password.*

- [ ] **TSK-301:** Integrate a robust OAuth2.0 / JWT provider (e.g., Auth0, Clerk, or custom FastAPI-Users implementation).
- [ ] **TSK-302:** Define user roles in the database (`admin`, `epidemiologist`, `analyst`, `reporter`, `viewer`).
- [ ] **TSK-303:** Implement backend middleware to enforce RBAC on specific endpoints.
- [ ] **TSK-304:** Create a User Management Dashboard for Admins to invite users and assign roles.

## Epic 4: Machine Learning Microservice (Forecasting)
*Adding the predictive intelligence layer.*

- [ ] **TSK-401:** Initialize a new Python repository (`ml-service`) using FastAPI or Ray Serve.
- [ ] **TSK-402:** Implement a daily CRON job to pull historical data and train/update the Prophet time-series models for major diseases.
- [ ] **TSK-403:** Build the SEIR compartmental model simulation endpoint (`POST /predict/seir`).
- [ ] **TSK-404:** Expose forecasting results via an API so the main dashboard can visualize them.

## Epic 5: AI & Agentic Workflows
*Automating manual analysis and reporting.*

- [ ] **TSK-501:** Integrate LangChain/CrewAI into the backend to manage autonomous agents.
- [ ] **TSK-502:** Develop the "Outbreak Summarizer Agent" to generate natural language summaries of complex clusters.
- [ ] **TSK-503:** Develop the "Alert Triage Agent" to evaluate anomaly thresholds and route critical alerts via SendGrid (Email) or Twilio (SMS).
- [ ] **TSK-504:** Create the Executive Dashboard view to render the LLM-generated reports.

## Epic 6: Geospatial Dashboard Overhaul
*Upgrading the UI for enterprise visibility.*

- [ ] **TSK-601:** Migrate from basic MapLibre markers to Mapbox GL JS Vector Tiles for rendering >100k points.
- [ ] **TSK-602:** Implement dynamic Density Heatmaps toggles in the React app.
- [ ] **TSK-603:** Utilize PostGIS `ST_ClusterDBSCAN` via an API endpoint to draw polygon bounding boxes around active disease clusters.
- [ ] **TSK-604:** Build the Forecast and Risk Dashboards (incorporating Recharts/Chart.js for time-series data).

---
*Document prepared by Antigravity HealthTech Solutions.*
