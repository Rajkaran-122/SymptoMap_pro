import asyncio
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.doctor import DoctorOutbreak
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from sqlalchemy import select
from datetime import datetime, timezone
import logging
import uuid
import json
from app.models.outbreak import Alert

logger = logging.getLogger(__name__)

FORECASTER_PROMPT = """
You are the SymptoMap Epidemiological Forecaster.
Analyze the following active outbreaks and generate a daily epidemiological briefing.
Translate complex mathematical trajectories into human-readable risk assessments.

Active Outbreaks:
{outbreaks_data}

Please generate a briefing document formatted as plain text containing:
1. Executive Summary (1 paragraph)
2. High-Risk Zones (List zones and forecasted trajectory)
3. Resource Recommendations (e.g., "Expected to peak in 14 days, potentially exhausting 85% of regional ICU capacity.")
"""

prompt = PromptTemplate(
    input_variables=["outbreaks_data"],
    template=FORECASTER_PROMPT
)

async def _generate_briefing():
    logger.info("Forecaster Agent triggered for daily briefing generation.")
    
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set. Cannot run forecaster.")
        return
        
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.3)
    chain = prompt | llm
    
    async with AsyncSessionLocal() as db:
        # Fetch active outbreaks (for simulation, we fetch top 10 recent ones)
        result = await db.execute(select(DoctorOutbreak).order_by(DoctorOutbreak.created_at.desc()).limit(10))
        outbreaks = result.scalars().all()
        
        if not outbreaks:
            logger.info("No active outbreaks found for forecasting.")
            return
            
        outbreaks_data = "\n".join([
            f"- {o.disease_type} in {o.location_name}, {o.city} ({o.patient_count} cases, Severity: {o.severity})"
            for o in outbreaks
        ])
            
        logger.info("Invoking LLM for forecasting...")
        try:
            response = await chain.ainvoke({
                "outbreaks_data": outbreaks_data
            })
            
            briefing = response.content
            logger.info(f"Daily Briefing generated:\n{briefing}")
            
            # Save the briefing as a high-level system alert / broadcast
            new_alert = Alert(
                id=uuid.uuid4(),
                alert_type="email", 
                severity="info",
                title=f"Daily Epidemiological Forecast - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                message=briefing,
                zone_name="National",
                recipients=["admin@symptomap.com"],
                delivery_status={"email": "sent"},
                acknowledged_by=[],
                sent_at=datetime.now(timezone.utc)
            )
            db.add(new_alert)
            await db.commit()
            logger.info("Daily Briefing saved as System Alert.")
            
        except Exception as e:
            logger.error(f"Failed to generate forecast: {e}")

@celery_app.task(name="app.agents.forecaster.generate_daily_briefing")
def generate_daily_briefing():
    """
    Celery task wrapper to run the daily forecast process.
    Triggered by Celery Beat on a CRON schedule.
    """
    asyncio.run(_generate_briefing())
