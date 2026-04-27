import sqlite3

# Connect to the database
conn = sqlite3.connect('mercyhurst_courses.db')
cursor = conn.cursor()

# Query all records from courses
cursor.execute('SELECT id, title, degree_type, minor FROM courses ORDER BY title')
courses_rows = cursor.fetchall()

# Query all records from salaries
cursor.execute('SELECT id, title, average_salary, source_degree FROM salaries ORDER BY title')
salaries_rows = cursor.fetchall()

# Print courses
print("Mercyhurst University Undergraduate Courses")
print("=" * 50)
print(f"Total programs: {len(courses_rows)}")
print()
for row in courses_rows:
    print(f"ID: {row[0]}")
    print(f"Title: {row[1]}")
    print(f"Degree Type: {row[2]}")
    print(f"Minor: {row[3]}")
    print("-" * 30)

print("\n\nSalaries Table")
print("=" * 50)
print(f"Total entries: {len(salaries_rows)}")
print()
for row in salaries_rows:
    print(f"ID: {row[0]}")
    print(f"Title: {row[1]}")
    print(f"Average Salary: {row[2]}")
    print(f"Source Degree: {row[3]}")
    print("-" * 30)

# Close connection
conn.close()