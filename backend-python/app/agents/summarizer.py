import asyncio
from app.core.celery_app import celery_app
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.doctor import DoctorOutbreak
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

# System prompt for the summarizer
SUMMARIZER_PROMPT = """
You are an expert Epidemiologist AI acting as the Outbreak Summarizer.
Your goal is to digest raw outbreak data and output a concise, 3-bullet-point executive summary.

Disease: {disease_type}
Cases: {patient_count}
Severity: {severity}
Location: {location_name}, {city}, {state}
Description/Notes: {description}

Please provide exactly 3 bullet points that cover:
1. The immediate severity and scale.
2. The geographical context.
3. Recommended immediate clinical or administrative action based on the notes provided.
"""

prompt = PromptTemplate(
    input_variables=["disease_type", "patient_count", "severity", "location_name", "city", "state", "description"],
    template=SUMMARIZER_PROMPT
)

async def _process_summarize(outbreak_id: str):
    logger.info(f"Summarizer Agent triggered for Outbreak ID: {outbreak_id}")
    
    # Needs API key to function
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set. Cannot run summarizer.")
        return
        
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini", temperature=0.2)
    chain = prompt | llm
    
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    LocalSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with LocalSession() as db:
        # Fetch outbreak
        outbreak = await db.get(DoctorOutbreak, outbreak_id)
        if not outbreak:
            logger.error(f"Outbreak {outbreak_id} not found.")
            return
            
        # Run LangChain
        logger.info("Invoking LLM for summary generation...")
        try:
            response = await chain.ainvoke({
                "disease_type": outbreak.disease_type,
                "patient_count": outbreak.patient_count,
                "severity": outbreak.severity,
                "location_name": outbreak.location_name,
                "city": outbreak.city,
                "state": outbreak.state,
                "description": outbreak.description or "No additional notes provided."
            })
            
            content = response.content
            if isinstance(content, list):
                content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
            elif not isinstance(content, str):
                content = str(content)
                
            summary_text = content.strip()
            logger.info(f"Generated summary: {summary_text}")
            
            # Save back to database
            outbreak.ai_summary = summary_text  # type: ignore
            await db.commit()
            logger.info("Summary saved to database successfully.")
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
        finally:
            await engine.dispose()


@celery_app.task(name="app.agents.summarizer.summarize_outbreak_task")
def summarize_outbreak_task(outbreak_id: str):
    """
    Celery task wrapper to run the async summarization process.
    Triggered when a new outbreak report is submitted.
    """
    asyncio.run(_process_summarize(outbreak_id))
