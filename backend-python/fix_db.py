import sqlite3
import os

db_path = r"c:\Users\digital metro\Documents\sympto-pulse-map-main\backend-python\symptomap.db"
db = sqlite3.connect(db_path)
try:
    db.execute('ALTER TABLE doctor_outbreaks ADD COLUMN ai_summary TEXT')
    db.commit()
    print("Column added successfully.")
except Exception as e:
    print("Error:", e)
