import requests
import time
import json
import uuid
import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_outbreak_summarizer():
    print("--- Testing Outbreak Summarizer Agent ---")
    
    # 1. Login to get token
    login_data = {"password": "Doctor@SymptoMap2025"}
    print("Logging in...")
    resp = requests.post(f"{BASE_URL}/doctor/login", json=login_data)
    
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
        
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Submit outbreak
    print("Submitting outbreak report...")
    outbreak_data = {
        "disease_type": "Dengue",
        "patient_count": 45,
        "severity": "severe",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "location_name": "Connaught Place Clinic",
        "city": "New Delhi",
        "state": "Delhi",
        "description": "Patients presenting with high fever, severe joint pain, and dropping platelet counts. Nearby construction site has stagnant water. Bed capacity is reaching 90%. Need immediate fogging.",
        "date_reported": datetime.datetime.now().isoformat() + "Z"
    }
    
    resp = requests.post(f"{BASE_URL}/doctor/outbreak", json=outbreak_data, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to submit outbreak: {resp.text}")
        return
        
    print("Outbreak submitted successfully!")
    print("Check Celery logs for LangChain Summarizer processing...")

def test_triage_manager():
    print("\n--- Testing Alert Triage Manager ---")
    
    # 1. Login to get token
    login_data = {"password": "Doctor@SymptoMap2025"}
    resp = requests.post(f"{BASE_URL}/doctor/login", json=login_data)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Submit alert
    print("Submitting alert...")
    alert_data = {
        "alert_type": "critical",
        "title": "Malaria Spikes in Mumbai Suburbs",
        "message": "Routine surveillance shows a 5% increase in Malaria cases in the last 2 weeks.",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "affected_area": "Mumbai",
        "expiry_hours": 24
    }
    
    resp = requests.post(f"{BASE_URL}/doctor/alert", json=alert_data, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to submit alert: {resp.text}")
        return
        
    print("Alert submitted successfully!")
    print("Check Celery logs for LangChain Triage Manager deciding if 'critical' should be downgraded to 'info/warning' because 5% isn't an outbreak...")

if __name__ == "__main__":
    # Wait for the servers to be up
    test_outbreak_summarizer()
    test_triage_manager()
    print("\nEnd-to-End Test Dispatched. Check `docker-compose logs celery_worker` to see the agents in action.")
