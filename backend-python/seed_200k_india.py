import sqlite3
import random
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "symptomap.db")

HOSPITALS = [
    {"name": "AIIMS Delhi", "city": "New Delhi", "state": "Delhi", "lat": 28.5659, "lon": 77.2066},
    {"name": "Safdarjung Hospital", "city": "New Delhi", "state": "Delhi", "lat": 28.5685, "lon": 77.2057},
    {"name": "Apollo Hospital Chennai", "city": "Chennai", "state": "Tamil Nadu", "lat": 13.0645, "lon": 80.2483},
    {"name": "Fortis Hospital Mumbai", "city": "Mumbai", "state": "Maharashtra", "lat": 19.1551, "lon": 72.9365},
    {"name": "Lilavati Hospital", "city": "Mumbai", "state": "Maharashtra", "lat": 19.0511, "lon": 72.8288},
    {"name": "Manipal Hospital Bengaluru", "city": "Bengaluru", "state": "Karnataka", "lat": 12.9592, "lon": 77.6444},
    {"name": "Narayana Health", "city": "Bengaluru", "state": "Karnataka", "lat": 12.8122, "lon": 77.6836},
    {"name": "PGIMER Chandigarh", "city": "Chandigarh", "state": "Chandigarh", "lat": 30.7634, "lon": 76.7766},
    {"name": "Christian Medical College", "city": "Vellore", "state": "Tamil Nadu", "lat": 12.9254, "lon": 79.1320},
    {"name": "Medanta The Medicity", "city": "Gurugram", "state": "Haryana", "lat": 28.4357, "lon": 77.0425},
    {"name": "Kokilaben Hospital", "city": "Mumbai", "state": "Maharashtra", "lat": 19.1311, "lon": 72.8287},
    {"name": "Sanjay Gandhi PGI", "city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.7454, "lon": 80.9333},
    {"name": "KEM Hospital", "city": "Mumbai", "state": "Maharashtra", "lat": 19.0031, "lon": 72.8427},
    {"name": "Apollo Gleneagles", "city": "Kolkata", "state": "West Bengal", "lat": 22.5736, "lon": 88.4011},
    {"name": "Tata Memorial", "city": "Mumbai", "state": "Maharashtra", "lat": 19.0044, "lon": 72.8447},
    {"name": "Max Super Speciality", "city": "New Delhi", "state": "Delhi", "lat": 28.5273, "lon": 77.2155},
    {"name": "Amrita Hospital", "city": "Kochi", "state": "Kerala", "lat": 10.0402, "lon": 76.2925},
    {"name": "JIPMER", "city": "Puducherry", "state": "Puducherry", "lat": 11.9542, "lon": 79.8000},
    {"name": "Sir Ganga Ram Hospital", "city": "New Delhi", "state": "Delhi", "lat": 28.6385, "lon": 77.1901},
    {"name": "Rajiv Gandhi Super Speciality", "city": "New Delhi", "state": "Delhi", "lat": 28.6826, "lon": 77.3117},
]

DISEASES = ["Viral Fever", "Dengue", "Malaria", "Typhoid", "Chikungunya", "Cholera", "Respiratory Distress"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["pending", "pending", "pending", "pending", "pending", "pending", "pending", "pending", "approved"] # mostly pending for admin console

def generate_data(num_records=200000):
    print(f"Connecting to DB at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Generating {num_records} records...")
    records = []
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    
    for i in range(num_records):
        h = random.choice(HOSPITALS)
        d = random.choice(DISEASES)
        s = random.choice(SEVERITIES)
        count = random.randint(5, 100)
        
        # Jitter coordinates slightly
        lat = float(h["lat"]) + random.uniform(-0.05, 0.05)
        lon = float(h["lon"]) + random.uniform(-0.05, 0.05)
        
        date_rep = start_date + datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        records.append((
            d,
            count,
            s,
            lat,
            lon,
            h["name"],
            h["city"],
            h["state"],
            f"Mass influx of {d} patients reported from {h['name']}.",
            date_rep.isoformat(),
            f"Dr. {random.choice(['Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Rao', 'Iyer', 'Menon', 'Gupta', 'Jain'])}",
            date_rep.isoformat(),
            random.choice(STATUSES)
        ))
        
    print("Executing batch insert...")
    cursor.executemany(
        """
        INSERT INTO doctor_outbreaks (
            disease_type, patient_count, severity, latitude, longitude, 
            location_name, city, state, description, date_reported, 
            submitted_by, created_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        records
    )
    
    conn.commit()
    conn.close()
    print("Successfully inserted 200,000 records!")

if __name__ == "__main__":
    generate_data()
