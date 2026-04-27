import sqlite3
import os

# Delete existing database if it exists
if os.path.exists('mercyhurst_courses.db'):
    os.remove('mercyhurst_courses.db')

# Connect to SQLite database
conn = sqlite3.connect('mercyhurst_courses.db')
cursor = conn.cursor()

# Read and execute the SQL file
with open('mercyhurst_courses_fixed.sql', 'r') as sql_file:
    sql_script = sql_file.read()

cursor.executescript(sql_script)

# Commit and close
conn.commit()
conn.close()

print("Database created and populated successfully from mercyhurst_courses.sql.")