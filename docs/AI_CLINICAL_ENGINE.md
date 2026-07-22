# AI Clinical Reasoning Engine (Template)

## Overview
The Clinical Reasoning Engine powers SAAKSHYA, facilitating an intelligent, multi-modal interaction flow that adapts to patient inputs in real time.

## Core Capabilities
- **True Multimodal**: Processes Image, Voice, and Text in one seamless flow.
- **Multilingual First**: Designed for global accessibility from day one (not just English-centric).
- **Low-End Device Compatibility**: Operates efficiently on basic phones with 2G connectivity.

## Consultation Workflow
1. **Patient Entry**: User uploads a photo or speaks symptoms in a local language.
2. **Context Building**: The AI gathers demographics and builds medical context.
3. **Targeted Questions**: An intelligent medical interview is conducted. The engine adaptively asks questions based on previous answers (utilizing LangGraph for state management).
4. **History & Deep Dive**: The system analyzes symptoms against the user's medical history.
5. **Drug/Allergy Check**: Aggregates data and checks for contraindications.
6. **Summary & Report**: Generates a diagnostic report with confidence scores and personalized health recommendations.

## Multi-LLM Reliability
The engine implements a robust failover strategy across OpenAI, Claude, and Grok, achieving 99.9% uptime for continuous AI support.
