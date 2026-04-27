#!/usr/bin/env python3
import sqlite3
import os
from jinja2 import Template

# Ensure templates directory exists
os.makedirs('static_site', exist_ok=True)
os.makedirs('static_site/program', exist_ok=True)

# Copy base.html and modify for static
with open('templates/base.html', 'r') as f:
    base_template = f.read()

# Replace dynamic title with static
base_template = base_template.replace('{{ title if title else \'College to The Real World\' }}', '📚 Mercyhurst to The Real World 💰')
base_template = base_template.replace('{% if subtitle %}{{ subtitle }}{% endif %}', 'Click a program to view its degree type, minor status, and salary.')

# Remove Jinja blocks for static
base_template = base_template.replace('{% block content %}{% endblock %}', '{{ content }}')

template = Template(base_template)

def get_db_connection():
    conn = sqlite3.connect('mercyhurst_courses.db')
    conn.row_factory = sqlite3.Row
    return conn

# Generate index.html
conn = get_db_connection()
programs = conn.execute('SELECT id, title FROM courses ORDER BY title').fetchall()
conn.close()

program_links = '\n'.join([f'<a class="program-link" href="program/{p["id"]}.html">{p["title"]}</a>' for p in programs])
content = f'<div class="card">{program_links}</div>'

html = template.render(content=content)
with open('static_site/index.html', 'w') as f:
    f.write(html)

# Generate program detail pages
conn = get_db_connection()
for program in conn.execute('SELECT c.id, c.title, c.degree_type, c.minor, s.average_salary, s.source_degree FROM courses c LEFT JOIN salaries s ON c.id = s.id'):
    minor_value = 'yes' if program['minor'] == 'yes' else 'no'
    salary_value = program['average_salary'] if program['average_salary'] else 'N/A'
    source_degree = program['source_degree'] if program['source_degree'] else 'No source available'

    content = f'''
    <div class="card">
        <h2>{program['title']}</h2>
        <p><strong>Degree Type:</strong> {program['degree_type']}</p>
        <p><strong>Minor:</strong> {minor_value}</p>
        <button class="button-green" onclick="showSalary()">Show Me The Money</button>
        <div class="salary-box" id="salary-box" style="display: none;">
            Average Salary: {salary_value}
            <div class="source-degree">Source: {source_degree}</div>
        </div>
    </div>
    <div class="card">
        <a href="../index.html">← Back to programs</a>
    </div>
    <script>
        function showSalary() {{
            document.getElementById('salary-box').style.display = 'block';
            event.target.style.display = 'none';
        }}
    </script>
    '''

    html = template.render(content=content)
    with open(f'static_site/program/{program["id"]}.html', 'w') as f:
        f.write(html)

conn.close()

print('Static site generated in static_site/')