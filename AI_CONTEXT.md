# AI Context & Guidelines
## SymptoMap: AI-Powered Disease Intelligence Platform (V2)

**For Future AI Agents (Auto-GPTs, Copilots, and Coding Assistants):** 
When operating within this repository, adhere to the following architectural, stylistic, and systemic guidelines.

---

## 1. Architectural Directives

- **Target Architecture:** We are migrating from a Monolithic SQLite/FastAPI setup (V1) to an Event-Driven Microservices architecture (V2) using PostgreSQL, Redis, and WebSockets.
- **Do Not Use Polling:** If tasked with updating real-time UI components, **do not** implement `setInterval` polling. Utilize the established WebSocket connection (`/ws/updates`).
- **Database Access:** Direct queries against the database should utilize `PostGIS` functions where spatial data is concerned. Avoid pulling raw geometries into Python to calculate distances. Use `ST_DWithin`, `ST_Intersects`, etc.
- **Asynchronous Operations:** Heavy ML computations (e.g., SEIR model runs) and external LLM API calls must be offloaded to background tasks (e.g., Celery or FastAPI `BackgroundTasks`) or pushed to the message broker. They must **never** block the main HTTP event loop.

## 2. Code Style & Standards

### Backend (Python)
- **Framework:** FastAPI
- **Validation:** Extensive use of Pydantic V2 models.
- **Typing:** Strict type hinting is mandatory. `mypy` must pass without errors.
- **ORM:** Use SQLAlchemy 2.0 with asynchronous drivers (`asyncpg`). Avoid synchronous DB calls.
- **Documentation:** Use Google-style docstrings. All endpoints must have rich OpenAPI annotations (tags, summaries, descriptive responses).

### Frontend (React/TypeScript)
- **Framework:** React 18+ (Vite).
- **Styling:** Tailwind CSS + Shadcn UI components. Do not write custom CSS unless absolutely necessary.
- **State Management:** Use Zustand for global state. Use React Query (`@tanstack/react-query`) for server-state fetching and caching.
- **Geospatial:** Use `react-map-gl` (Mapbox/MapLibre wrapper). For large datasets, consider `deck.gl` layers.

## 3. Autonomous AI Agents Integration (AGENTS.md Context)

When modifying or expanding the LangChain/CrewAI agentic frameworks:
1. **Prompt Isolation:** Store LLM prompts in separate `.yaml` or `prompts/` directory files, not hardcoded inline.
2. **Deterministic Fallbacks:** LLM-generated JSON or decisions must be parsed securely using `PydanticOutputParser` to ensure type safety before affecting system state.
3. **Traceability:** All actions taken by an Autonomous Agent must be logged to the `audit_logs` table with the `actor_type` set to `AGENT` and a reference to the specific model/version used.

## 4. Security Requirements for Code Generation

- **No Secrets in Code:** Never hardcode API keys, DB passwords, or JWT secrets. Always use `os.getenv()` or `pydantic-settings`.
- **SQL Injection:** Never use raw f-strings for SQL queries. Always use SQLAlchemy's parameter binding.
- **XSS Prevention:** Ensure React components correctly sanitize any user-submitted text or LLM-generated summaries before rendering.

---
**End of AI Context**
