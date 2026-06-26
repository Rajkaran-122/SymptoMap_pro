# Autonomous Agent Architecture (Version 2)
## SymptoMap: AI-Powered Disease Intelligence Platform

To transition SymptoMap from a passive data repository into an active "Intelligence" platform, V2 introduces an Agentic AI layer utilizing frameworks such as LangChain or CrewAI. These agents operate asynchronously, analyzing incoming data and synthesizing actionable intelligence.

---

## 1. Agent Design Principles
- **Non-Blocking:** Agents must never execute on the main HTTP event loop. They are triggered by Pub/Sub events or CRON schedules and execute in isolated worker nodes (e.g., Celery).
- **Tool-Augmented:** Agents are provided specific, tightly scoped tools (e.g., "Query DB for last 24h Cholera cases", "Calculate R0"). They cannot execute arbitrary SQL.
- **Human-in-the-Loop (HITL):** Before a high-severity alert (e.g., National Pandemic Warning) is broadcast by an agent to public channels, it must be staged for review by a human Epidemiologist.

---

## 2. Core Agents

### Agent 1: The Outbreak Summarizer (Data Synthesis)
**Trigger:** Whenever the ML Cluster detection algorithm identifies a new `cluster_id` or an existing cluster grows by >50% in 24 hours.
**Role:** To digest raw tabular data and unstructured clinical notes into a 3-bullet-point executive summary.
**Tools Provided:**
- `GetClusterDemographics(cluster_id)`
- `GetClinicalNotes(cluster_id)`
- `GetWeatherCorrelations(lat, lon)`
**Output:** Updates the `ai_summary` field in the `clusters` table.

### Agent 2: The Epidemiological Forecaster (Analysis)
**Trigger:** Daily at 02:00 AM UTC.
**Role:** To interact with the SEIR modeling endpoint. It analyzes the model's output trajectory and translates complex mathematical curves into human-readable risk assessments.
**Tools Provided:**
- `RunSEIRSimulation(disease, region)`
- `CompareHistoricalOutbreaks(disease, trajectory)`
**Output:** Generates a daily Briefing Document stored in the Data Warehouse. Example output: *"Based on current SEIR trajectories, the Cholera outbreak in Zone A is expected to peak in 14 days, potentially exhausting 85% of regional ICU capacity."*

### Agent 3: The Alert Triage Manager (Action)
**Trigger:** Continuous evaluation of the Kafka ingestion stream.
**Role:** To prevent "Alert Fatigue." Rather than firing an email every time a threshold is breached, this agent evaluates the context of the breach.
**Logic:** If the threshold for Dengue is breached, but it is currently the peak of monsoon season (historically normal), the agent downgrades the alert from `CRITICAL` to `WARNING` and groups it into a daily digest rather than sending an immediate push notification.

---

## 3. Implementation Stack
- **Framework:** `LangChain` for tool binding and execution chaining.
- **LLM Provider:** Enterprise-grade, HIPAA-compliant models (e.g., Azure OpenAI GPT-4 or Anthropic Claude 3.5 Sonnet on AWS Bedrock) ensuring no patient data is used for public model training.
- **Orchestration:** `Celery` workers utilizing `Redis` as the broker to handle agent task queues.

---
*Document prepared by Antigravity HealthTech Solutions.*
