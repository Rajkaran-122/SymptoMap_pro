# SAAKSHYA Setup Guide (Template)

> **Note**: *This guide is a template generated based on the architectural specifications from the PDF. Exact setup commands and file paths will be updated upon reviewing the actual `Health_agent.git` repository.*

## Prerequisites
- **Node.js** (for Next.js frontend)
- **Python 3.10+** (for Flask microservices)
- **MongoDB** (Primary database)
- **Redis** (For caching and reducing database load by 60-70%)
- **LiveKit Server** (For real-time voice WebRTC infrastructure)

## Environment Variables
Create a `.env` file with the following keys:
- `OPENAI_API_KEY`, `CLAUDE_API_KEY`, `GROK_API_KEY` (for Multi-LLM failover)
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- `MONGO_URI`, `REDIS_URL`

## Running Locally
1. Start the Flask backend microservices.
2. Start the Next.js frontend (`npm run dev`).
3. Ensure MongoDB and Redis instances are active and reachable.
