import requests
import json

data = {
    "hospital_name": "Test Hospital",
    "disease_type": "Viral Fever",
    "patient_count": 5,
    "severity": "moderate",
    "date_started": "2026-07-22T00:00:00Z",
    "location": {"lat": 19.0, "lng": 72.0}
}

response = requests.post("http://localhost:8000/api/v1/outbreaks/", json=data)
print(response.status_code)
print(response.text)
