# SymptoMap - AeroIntel: AI-Powered Urban Air Quality, Viral Fever Prediction & Public Health Chatbot

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](docs/PROPRIETARY_NOTICE.md)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)

**SymptoMap** is a comprehensive, multi-agent AI ecosystem. It fuses real-time IoT urban air quality monitoring with predictive data systems for viral fevers, and provides a direct-to-patient AI Health Chatbot. This holistic approach stops pollution at the source while forecasting and mitigating public health crises before they overwhelm medical infrastructure.

*This repository is submitted for the **AI-Powered Urban Air Quality Intelligence for Smart City Intervention** challenge.*

---

## Hackathon Documentation Directory

To evaluate this project, please review the core architectural and proposal documents located in the `docs/` folder:

1. **[The Winning Pitch / Project Proposal](docs/URBAN_AIR_QUALITY_INTELLIGENCE.md)**: Details the problem context, challenge statement, and exactly how AeroIntel dominates the evaluation criteria.
2. **[High-Level Design (HLD)](docs/AEROINTEL_HLD.md)**: Visual architecture of the IoT ingestion, Celery Multi-Agent AI core, and Geospatial Command Center.
3. **[Low-Level Design (LLD)](docs/AEROINTEL_LLD.md)**: Sequence diagrams for the Enforcement Approval Pipeline, Epidemiological Zoning flows, and core Database Schemas.
4. **[Proprietary Notice & Licensing](docs/PROPRIETARY_NOTICE.md)**: Legal terms for evaluating this repository.

---

## Core Platform Capabilities

- **Geospatial Source Attribution**: AI identifies exact pollution sources (waste burning, factories) at the ward level using satellite (Sentinel/MODIS) and land-use data.
- **Viral Fever Prediction**: Correlates AQI spikes with epidemiological data to dynamically generate Health Vulnerability Zones (Red/Yellow/Green).
- **Enforcement Approval Pipeline**: Ensures data integrity by requiring city administrators to approve AI-generated interventions before dispatching authorities.
- **Hyperlocal Alerting**: Triggers real-time WebSocket dashboard updates and targeted, multilingual SMS/IVR advisories to vulnerable populations.

---

## Associated Public Health Ecosystem: AI Health Chatbot

While AeroIntel handles population-level surveillance, our ecosystem extends to individual patient care through our dedicated AI Health Chatbot (Healthzy).

**Repository**: [Health_agent.git](https://github.com/Rajkaran-122/Health_agent.git)

### What the AI Health Chatbot Does
The chatbot operates as a highly advanced **Adaptive Clinical Reasoning Engine**. Unlike standard chatbots, it executes a structured, dynamic medical triage flowchart:
1. **Context Building**: Collects primary symptoms, age, gender, and onset timeline.
2. **Intelligent Triage**: The AI generates specific, relevant questions with examples (e.g., pinpointing exact pain locations or sensations).
3. **Real-Time SOAP Generation**: Subjective, Objective, Assessment, and Plan (SOAP) findings are updated in real-time in the background as the conversation progresses.
4. **Transparent Clinical Reasoning**: The AI is engineered to provide the reasoning behind every response and question it generates.
5. **Comprehensive History Taking**: It systematically drills down into:
   - Factors that make symptoms better or worse.
   - Historical instances of similar symptoms.
   - Current medications, supplements, and allergies.
6. **Diagnostic Output**: Once sufficient clinical context is gathered, it generates a full Consultation Summary, Diagnostic Report, and clear next steps for the patient.

---

## Quick Start (Local Deployment)

AeroIntel is built for rapid, instant bootstrapping for any Tier 1 or Tier 2 city.

### Prerequisites
* Node.js 18+
* Python 3.10+
* Redis (Required for Multi-Agent Task Queuing & WebSockets)

### 1. Backend (FastAPI + Celery Agents)
```bash
cd backend-python
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*(Note: On the first boot, the system auto-seeds CAAQMS mock sensors and historical alerts for immediate evaluation).*

### 2. Frontend (React + MapLibre)
```bash
cd frontend
npm install
npm run dev
```
Access the Government Command Center at `http://localhost:3000`.

---
*Developed by Rajkaran Yadav*
