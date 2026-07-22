# SymptoMap: Actual Implementation Documentation

## 1. What This Repository Actually Does
The `sympto-pulse-map-main` repository is a monorepo containing the functional implementation of **SymptoMap**, a Real-time Disease Surveillance Platform. It is actively designed for outbreak reporting, approval workflows, public risk visibility, and automated health broadcast operations.

It is broken down into two main services:
- **Backend**: A Python FastAPI application handling APIs, real-time WebSockets via Redis Pub/Sub, and background AI processing.
- **Frontend**: A modern React 18 SPA (Single Page Application) built with Vite, TypeScript, and Tailwind CSS.

## 2. Core Operational Workflows
Based on the actual codebase, the platform supports the following core workflows:

### A. The Doctor & Admin Workflow
*   **Outbreak Reporting**: Doctors log in via a dedicated portal and submit outbreak reports.
*   **Approval Pipeline**: Submitted outbreaks go into a "Pending" state in the database. System Admins can review, approve, or reject these submissions.
*   **Alert Generation**: The system supports generating and managing multiple types of alerts (email, SMS, push) targeted at specific geographical zones. There is an advanced seeding mechanism generating realistic alerts for Dengue, Malaria, COVID-19, Flu, Typhoid, and Viral Fever.

### B. The Public Visibility Workflow
*   **Live Geospatial Maps**: Using `maplibre-gl` on the frontend, the app renders interactive maps of confirmed outbreaks for public visibility.
*   **Real-time Broadcasts**: Critical health broadcasts (e.g., Dengue Advisories or COVID-19 Booster Drives) are stored in the database and pushed to the frontend via WebSockets in real time.

### C. The AI Agent Orchestration
*   **Autonomous Agents**: The `backend-python/app/agents` module (e.g., `triage.py`) indicates the use of autonomous AI workers.
*   **Triaging & Summarization**: The system uses LLMs (likely via LangChain as seen in project docs) and Celery background tasks to summarize outbreak intelligence and triage severe issues autonomously, lessening the manual burden on human admins.

## 3. Technology Stack Actually In Use

### Backend (`/backend-python`)
*   **Framework**: FastAPI with Pydantic for request validation.
*   **Database Layer**: Uses SQLAlchemy 2.0 with async support. It defaults to an async SQLite database (`aiosqlite`) for local development, with a clear migration path to PostgreSQL.
*   **Real-Time & Tasks**: Redis is actively utilized for WebSocket message broadcasting (`app.websocket.manager`) and Celery task queuing.
*   **Security**: Implementation includes `slowapi` for Rate Limiting, JWT-based authentication for doctor/admin roles, and robust CORS handling (with dynamic regex to support Vercel preview environments).

### Frontend (`/frontend`)
*   **Framework**: React 18, bootstrapped with Vite and strictly typed with TypeScript.
*   **State Management**: `zustand` is used for lightweight, scalable global state management.
*   **Data Fetching**: `@tanstack/react-query` handles API caching and synchronization with the backend.
*   **UI & Visualization**: Tailwind CSS for styling, `lucide-react` for icons, `recharts` for analytics dashboards, and `maplibre-gl` for the core geospatial outbreak mapping.
*   **Routing**: `react-router-dom` v6 for client-side routing.

## 4. Current State & Deployment Readiness
*   **Seeding & Bootstrapping**: The backend has highly sophisticated auto-seeding logic (`/seed`, `/force-seed`, `/seed-alerts`) in `main.py`. Upon startup, if the database is empty, it automatically populates realistic mock data (hospitals, users, active alerts, and broadcasts) so the app is instantly usable.
*   **Containerization**: Root-level Docker Compose configuration allows spinning up the API, Frontend, and Redis/Celery workers simultaneously.
*   **Vercel Optimized**: The frontend is fully configured (`vercel.json`) and the backend explicitly allows Vercel preview URLs, meaning the frontend is built to be hosted on Vercel while the backend runs elsewhere (e.g., Render or AWS).

**Summary**: This repository represents the tangible, highly-deployable half of the broader "Healthcare AI Ecosystem". While the PDF discussed an AI Chatbot (SAAKSHYA), this specific repository is dedicated squarely to **SYMPTOMAP**: the population-level disease surveillance, mapping, and rapid alert propagation platform.
