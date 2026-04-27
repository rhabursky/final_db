import sqlite3

# Connect to the database
conn = sqlite3.connect('mercyhurst_courses.db')
cursor = conn.cursor()

# Add the minor column
cursor.execute('ALTER TABLE courses ADD COLUMN minor TEXT')

# Update the minor column based on degree_type
cursor.execute('UPDATE courses SET minor = "yes" WHERE degree_type LIKE "%Undergraduate Minor%"')
cursor.execute('UPDATE courses SET minor = "no" WHERE minor IS NULL')

# Commit and close
conn.commit()
conn.close()

print("Minor column added and populated successfully.")