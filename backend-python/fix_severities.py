import sqlite3
import os

db_path = r"c:\Users\digital metro\Documents\sympto-pulse-map-main\backend-python\symptomap.db"
db = sqlite3.connect(db_path)
db.execute("UPDATE doctor_outbreaks SET severity = 'mild' WHERE severity = 'Low'")
db.execute("UPDATE doctor_outbreaks SET severity = 'moderate' WHERE severity = 'Medium'")
db.execute("UPDATE doctor_outbreaks SET severity = 'severe' WHERE severity IN ('High', 'Critical')")
db.commit()
print('Database severities updated')
