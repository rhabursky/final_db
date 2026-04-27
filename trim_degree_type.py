import sqlite3

# Connect to the database
conn = sqlite3.connect('mercyhurst_courses.db')
cursor = conn.cursor()

# Update degree_type to remove everything after the comma
cursor.execute('''
UPDATE courses
SET degree_type = TRIM(SUBSTR(degree_type, 1, INSTR(degree_type, ',') - 1))
WHERE INSTR(degree_type, ',') > 0
''')

# Commit and close
conn.commit()
conn.close()

print("Degree type column updated to remove text after comma.")