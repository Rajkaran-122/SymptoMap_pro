import asyncio
from app.core.celery_app import celery_app
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.doctor import DoctorAlert
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

TRIAGE_PROMPT = """
You are the Alert Triage Manager for SymptoMap, an epidemiological intelligence system.
Your job is to prevent "Alert Fatigue". You receive a proposed alert and must evaluate if its severity should be upgraded, downgraded, or kept the same based on typical epidemiological context (e.g. Dengue during monsoon is normal, a single Ebola case is critical).

Proposed Alert Title: {title}
Proposed Message: {message}
Original Severity: {severity}
Location: {affected_area}

Respond with exactly two lines:
Line 1: FINAL SEVERITY: [critical/warning/info]
Line 2: RATIONALE: [Brief 1-sentence explanation]
"""

prompt = PromptTemplate(
    input_variables=["title", "message", "severity", "affected_area"],
    template=TRIAGE_PROMPT
)

async def _process_triage(alert_id: str):
    logger.info(f"Triage Agent triggered for Alert ID: {alert_id}")
    
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set. Cannot run triage.")
        return
        
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.0)
    chain = prompt | llm
    
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    LocalSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with LocalSession() as db:
        # Fetch alert
        alert = await db.get(DoctorAlert, alert_id)
        if not alert:
            logger.error(f"Alert {alert_id} not found.")
            return
            
        logger.info("Invoking LLM for alert triage...")
        try:
            response = await chain.ainvoke({
                "title": alert.title,
                "message": alert.message,
                "severity": alert.alert_type,
                "affected_area": alert.affected_area
            })
            
            content = response.content
            if isinstance(content, list):
                content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
            elif not isinstance(content, str):
                content = str(content)
                
            output = content.strip()
            logger.info(f"Triage output:\n{output}")
            
            lines = output.split("\n")
            if len(lines) >= 1 and "FINAL SEVERITY:" in lines[0]:
                final_severity = lines[0].split("FINAL SEVERITY:")[1].strip().lower()
                if final_severity in ["critical", "warning", "info"]:
                    # Update database with new severity and save rationale if possible
                    alert.alert_type = final_severity  # type: ignore
                    
                    if len(lines) >= 2 and "RATIONALE:" in lines[1]:
                        rationale = lines[1].split("RATIONALE:")[1].strip()
                        alert.message = f"{alert.message}\n\n[AI Triage Rationale: {rationale}]"  # type: ignore
                    
                    await db.commit()
                    logger.info(f"Alert {alert_id} triaged to {final_severity}")
                else:
                    logger.error(f"Invalid severity returned by LLM: {final_severity}")
            
            
        except Exception as e:
            logger.error(f"Failed to triage alert: {e}")
        finally:
            await engine.dispose()

@celery_app.task(name="app.agents.triage.triage_alert_task")
def triage_alert_task(alert_id: str):
    """
    Celery task wrapper to run the async triage process.
    Triggered when a new alert is submitted.
    """
    asyncio.run(_process_triage(alert_id))
