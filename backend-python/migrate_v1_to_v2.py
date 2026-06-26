import asyncio
import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def run_migration():
    print("Starting ETL Migration from SQLite to PostgreSQL (V1 -> V2)")

    # 1. Connect to local SQLite (V1)
    sqlite_db_path = "symptomap.db"
    if not os.path.exists(sqlite_db_path):
        print(f"Error: {sqlite_db_path} not found. Ensure you run this from backend-python.")
        return

    print("Connecting to SQLite...")
    conn_sqlite = sqlite3.connect(sqlite_db_path)
    conn_sqlite.row_factory = sqlite3.Row
    cursor = conn_sqlite.cursor()

    # 2. Connect to PostgreSQL (V2)
    # This expects the new .env settings
    pg_url = settings.DATABASE_URL
    if "postgresql" not in pg_url:
        print("Error: Settings are not pointing to PostgreSQL.")
        print(f"Current DATABASE_URL: {pg_url}")
        return

    print(f"Connecting to PostgreSQL: {pg_url}")
    pg_engine = create_async_engine(pg_url)
    
    # Need to create tables using sync engine because create_all does not support async directly
    # Wait, async engine supports run_sync
    
    from app.core.database import Base
    # import models so they are registered
    from app.models import User, Hospital, Outbreak, Prediction, Alert, ChatbotConversation, AnonymousSymptomReport, DiseaseInfo, DoctorOutbreak, DoctorAlert, Broadcast, NotificationPreference

    async with pg_engine.begin() as conn:
        print("Creating PostGIS extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created.")

    AsyncSessionLocal = async_sessionmaker(pg_engine, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        # Fetch all outbreaks from SQLite
        cursor.execute("SELECT * FROM outbreaks")
        from datetime import datetime

        def parse_date(d_str):
            if not d_str:
                return None
            try:
                return datetime.fromisoformat(d_str)
            except ValueError:
                import dateutil.parser
                return dateutil.parser.parse(d_str)

        # Migrate Users
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            data = dict(row)
            try:
                await session.execute(
                    text("""
                    INSERT INTO users (id, email, password_hash, full_name, role, is_active)
                    VALUES (:id, :email, :password_hash, :full_name, :role, :is_active)
                    ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": data.get("id"),
                        "email": data.get("email"),
                        "password_hash": data.get("password_hash"),
                        "full_name": data.get("full_name"),
                        "role": data.get("role", "doctor"),
                        "is_active": data.get("is_active", True)
                    }
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
        await session.commit()

        # Migrate Hospitals
        cursor.execute("SELECT * FROM hospitals")
        for row in cursor.fetchall():
            data = dict(row)
            try:
                lat = data.get("latitude")
                lon = data.get("longitude")
                loc = f"SRID=4326;POINT({lon} {lat})" if lat and lon else None
                await session.execute(
                    text("""
                    INSERT INTO hospitals (id, name, address, latitude, longitude, location)
                    VALUES (:id, :name, :address, :lat, :lon, ST_GeomFromEWKT(:loc))
                    ON CONFLICT (id) DO NOTHING
                    """),
                    {"id": data.get("id"), "name": data.get("name"), "address": data.get("address"), "lat": lat, "lon": lon, "loc": loc}
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
        await session.commit()

        # Fetch all outbreaks from SQLite
        cursor.execute("SELECT * FROM outbreaks")
        outbreaks = cursor.fetchall()
        print(f"Found {len(outbreaks)} outbreaks in SQLite to migrate.")

        for row in outbreaks:
            data = dict(row)
            
            # Extract basic lat/lon
            lat = data.get("latitude")
            lon = data.get("longitude")

            # PostGIS Geometry string (WKT)
            location_wkt = None
            if lat is not None and lon is not None:
                # WKT for POINT is: POINT(longitude latitude)
                location_wkt = f"SRID=4326;POINT({lon} {lat})"

            # Parse dates
            date_started_str = data.get("date_started")
            date_reported_str = data.get("date_reported")
            
            def parse_date(d_str):
                if not d_str:
                    return None
                try:
                    # SQLite date format: YYYY-MM-DD HH:MM:SS.mmmmmm or YYYY-MM-DD HH:MM:SS
                    return datetime.fromisoformat(d_str)
                except ValueError:
                    # try fallback
                    import dateutil.parser
                    return dateutil.parser.parse(d_str)

            date_started = parse_date(date_started_str)
            date_reported = parse_date(date_reported_str)

            # Insert into PostgreSQL using raw SQL for speed and bypass ORM overhead
            # We assume the schema is already generated via Alembic
            try:
                await session.execute(
                    text("""
                    INSERT INTO outbreaks (
                        id, hospital_id, reported_by, disease_type, patient_count, 
                        date_started, date_reported, severity, notes, latitude, longitude, location
                    ) VALUES (
                        :id, :hospital_id, :reported_by, :disease_type, :patient_count,
                        :date_started, :date_reported, :severity, :notes, :latitude, :longitude, ST_GeomFromEWKT(:location)
                    ) ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": data.get("id"),
                        "hospital_id": data.get("hospital_id"),
                        "reported_by": data.get("reported_by"),
                        "disease_type": data.get("disease_type"),
                        "patient_count": data.get("patient_count"),
                        "date_started": date_started,
                        "date_reported": date_reported,
                        "severity": data.get("severity"),
                        "notes": data.get("notes"),
                        "latitude": lat,
                        "longitude": lon,
                        "location": location_wkt
                    }
                )
                await session.commit()
            except Exception as e:
                print(f"Failed to migrate record {data.get('id')}: {e}")
                await session.rollback()
                # Keep going even if one fails
                
        print("Migration complete!")

    conn_sqlite.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
