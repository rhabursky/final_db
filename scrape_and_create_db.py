import sqlite3
import requests
from bs4 import BeautifulSoup

# URL to scrape
url = "https://www.mercyhurst.edu/academics/all-academic-programs"

# Fetch the page
response = requests.get(url)
response.raise_for_status()

# Parse the HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Find all program list items
programs = soup.find_all('li', class_='component-academic-program-list__item')

# Extract data
data = []
for program in programs:
    title_span = program.find('span', class_='component-academic-program-list__item-name')
    degree_span = program.find('span', class_='component-academic-program-list__item-type')
    
    if title_span and degree_span:
        title = title_span.get_text(strip=True)
        degree_type = degree_span.get_text(strip=True)
        data.append((title, degree_type))

# Print the data as a list of tuples
print(data)

# Connect to SQLite database
conn = sqlite3.connect('mercyhurst_courses.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    degree_type TEXT
)
''')

# Insert data
for item in data:
    cursor.execute('''
    INSERT INTO courses (title, degree_type)
    VALUES (?, ?)
    ''', item)

# Commit and close
conn.commit()
conn.close()

print("Database created and populated successfully.")