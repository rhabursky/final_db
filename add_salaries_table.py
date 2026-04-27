import sqlite3

# Connect to the database
conn = sqlite3.connect('mercyhurst_courses.db')
cursor = conn.cursor()

# Drop the table if it exists
cursor.execute('DROP TABLE IF EXISTS salaries')

# Create the salaries table
cursor.execute('''
CREATE TABLE salaries (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    average_salary TEXT,
    source_degree TEXT
)
''')

# Data from Payscale with similar matches and source degrees
salaries_data = [
    ('Accounting', '$86k', 'Master of Business Administration (MBA), Accounting'),
    ('Anthropology and Archaeology', '$60k', 'Anthropology'),
    ('Applied Sociology', '$55k', 'Sociology'),
    ('Art', '$50k', 'Fine Arts'),
    ('Art Therapy', '$70k', 'Psychology'),
    ('Biochemistry', '$80k', 'Biochemistry'),
    ('Biology', '$75k', 'Biology'),
    ('Business Administration', '$72k', 'Business Administration'),
    ('Chemistry & Biochemistry', '$80k', 'Chemistry'),
    ('Communication', '$55k', 'Communications'),
    ('Computer Science', '$126k', 'Computer Science'),
    ('Criminal Justice', '$50k', 'Criminal Justice'),
    ('Dance', '$45k', 'Performing Arts'),
    ('Data Science', '$110k', 'Data Science'),
    ('Economics', '$85k', 'Economics'),
    ('English', '$55k', 'English'),
    ('Environmental Science', '$65k', 'Environmental Science'),
    ('Exercise Science', '$50k', 'Kinesiology'),
    ('Fashion Merchandising', '$50k', 'Fashion Design'),
    ('Finance', '$82k', 'Finance'),
    ('Forensic Science', '$60k', 'Forensic Science'),
    ('Graphic Design', '$55k', 'Graphic Design'),
    ('History', '$60k', 'History'),
    ('Hospitality Management', '$50k', 'Hospitality Management'),
    ('Human Resource Management', '$70k', 'Human Resources'),
    ('Information Systems', '$96k', 'Information Technology'),
    ('Intelligence Studies', '$75k', 'International Relations'),
    ('International Business', '$78k', 'International Business'),
    ('Journalism', '$50k', 'Journalism'),
    ('Liberal Studies', '$55k', 'Liberal Arts'),
    ('Management', '$80k', 'Management'),
    ('Marketing', '$72k', 'Marketing'),
    ('Mathematics', '$85k', 'Mathematics'),
    ('Music', '$50k', 'Music'),
    ('Music Education', '$55k', 'Education'),
    ('Neuroscience', '$75k', 'Neuroscience'),
    ('Nursing', '$77k', 'Nursing'),
    ('Philosophy', '$60k', 'Philosophy'),
    ('Physics', '$90k', 'Physics'),
    ('Political Science', '$70k', 'Political Science'),
    ('Pre_Athletic Training', '$50k', 'Sports Medicine'),
    ('Psychology', '$70k', 'Psychology'),
    ('Public Health', '$65k', 'Public Health'),
    ('Religious Studies', '$50k', 'Religious Studies'),
    ('Russian Studies', '$55k', 'Foreign Languages'),
    ('Social Work', '$50k', 'Social Work'),
    ('Sociology', '$55k', 'Sociology'),
    ('Spanish and Spanish Education', '$55k', 'Spanish'),
    ('Sport and Event Management', '$50k', 'Sports Management'),
    ('Sport Business Management', '$50k', 'Sports Management'),
    ('Sports Medicine', '$50k', 'Sports Medicine'),
    ('Studio Art', '$50k', 'Fine Arts')
]

# Get the ids from courses table
cursor.execute('SELECT id, title FROM courses ORDER BY id')
courses = cursor.fetchall()

# Create a dict for title to id
title_to_id = {row[1]: row[0] for row in courses}

# Insert into salaries
for title, salary, source in salaries_data:
    if title in title_to_id:
        cursor.execute('''
        INSERT INTO salaries (id, title, average_salary, source_degree)
        VALUES (?, ?, ?, ?)
        ''', (title_to_id[title], title, salary, source))

# Commit and close
conn.commit()
conn.close()

print("Salaries table created and populated.")