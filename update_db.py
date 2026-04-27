#!/usr/bin/env python3
import os
import re
import sqlite3
from collections import Counter

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.payscale.com"
MAIN_URL = BASE_URL + "/research/US/Degree"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

manual_mapping = {
    'Anthropology and Archaeology': 'Anthropology',
    'Applied Sociology': 'Sociology',
    'Art Education': 'Education',
    'Art Therapy': 'Psychology',
    'Artificial Intelligence and Data Science': 'Data Science',
    'Business and Competitive Intelligence': 'Business Intelligence',
    'Business Economics': 'Economics',
    'Chemistry & Biochemistry': 'Chemistry',
    'Composition (Music)': 'Music',
    'Cyber Security': 'Cyber Security',
    'Early Childhood Education | Special Education': 'Education',
    'Exercise Science': 'Kinesiology',
    'Fashion Merchandising': 'Fashion Design',
    'Geology': 'Geology',
    'Graphic Design': 'Graphic Design',
    'Human Resource Management': 'Human Resources',
    'Information Systems': 'Information Technology',
    'Intelligence Studies': 'International Relations',
    'Liberal Studies': 'Liberal Arts',
    'Music Education': 'Music',
    'Nursing (RN to BSN)': 'Nursing',
    'Nursing (BSN)': 'Nursing',
    'Performance (Music)': 'Music',
    'Physical Therapist Assistant': 'Physical Therapy',
    'Pre_Athletic Training': 'Athletic Training',
    'Religious Studies': 'Religious Studies',
    'Russian Studies': 'Foreign Languages',
    'Applied Forensic Sciences': 'Bachelor of Science (BS / BSc), Biology',
    'Cyber Security': 'Bachelor of Science (BS / BSc), Cyber/Electronic Operations & Warfare',
    'Social Work': 'Social Work',
    'Spanish and Spanish Education': 'Spanish',
    'Sport and Event Management': 'Sports Management',
    'Sport Business Management': 'Sports Management',
    'Studio Art': 'Fine Arts',
    'Communication': 'Communications',
    'Biochemistry': 'Biochemistry',
    'Biology': 'Biology',
    'Criminal Justice': 'Criminal Justice',
    'Data Science': 'Data Science',
    'Economics': 'Economics',
    'English': 'English',
    'Environmental Science': 'Environmental Science',
    'Finance': 'Finance',
    'Forensic Science': 'Forensic Science',
    'History': 'History',
    'Hospitality Management': 'Hospitality Management',
    'International Business': 'International Business',
    'Journalism': 'Journalism',
    'Management': 'Management',
    'Marketing': 'Marketing',
    'Mathematics': 'Mathematics',
    'Music': 'Music',
    'Neuroscience': 'Neuroscience',
    'Philosophy': 'Philosophy',
    'Physics': 'Physics',
    'Political Science': 'Political Science',
    'Psychology': 'Psychology',
    'Public Health': 'Public Health',
    'Sociology': 'Sociology',
    'Sports Medicine': 'Sports Medicine',
}


def normalize(text):
    text = text or ''
    text = text.lower()
    text = text.replace('&', ' and ')
    text = re.sub(r"[^a-z0-9]+", ' ', text)
    return ' '.join(text.split())


def best_degree_match(program, degree_names):
    program_norm = normalize(program)
    if program in manual_mapping:
        target = normalize(manual_mapping[program])
    else:
        target = program_norm

    best = None
    best_score = -1

    for degree in degree_names:
        degree_norm = normalize(degree)
        if target == degree_norm or target in degree_norm or degree_norm in target:
            return degree

        program_tokens = set(program_norm.split())
        degree_tokens = set(degree_norm.split())
        score = len(program_tokens & degree_tokens)
        if score > best_score:
            best_score = score
            best = degree

    if best_score >= 2:
        return best
    return None


def fetch_url(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp


def collect_degree_links():
    response = fetch_url(MAIN_URL)
    soup = BeautifulSoup(response.content, 'html.parser')

    category_urls = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/research/US/Degree/') and '=' not in href:
            category_urls.add(BASE_URL + href)

    degree_links = {}
    for category_url in sorted(category_urls):
        try:
            resp = fetch_url(category_url)
            cat_soup = BeautifulSoup(resp.content, 'html.parser')
            for link in cat_soup.find_all('a', href=True):
                href = link['href']
                if '/Salary' in href and '/Degree=' in href:
                    text = link.get_text(strip=True)
                    if text:
                        degree_links[text] = BASE_URL + href
        except Exception:
            continue

    return degree_links


def fetch_salary_page(url):
    resp = fetch_url(url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    salary_span = soup.find('span', class_='default-overview__value')
    if salary_span:
        return salary_span.get_text(strip=True)
    return None


def main():
    if os.path.exists('mercyhurst_courses.db'):
        os.remove('mercyhurst_courses.db')
        print('Deleted existing database')

    conn = sqlite3.connect('mercyhurst_courses.db')
    cursor = conn.cursor()

    with open('mercyhurst_courses.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)
    print('Created courses table from mercyhurst_courses.sql')

    try:
        cursor.execute('ALTER TABLE courses ADD COLUMN minor TEXT')
    except sqlite3.OperationalError:
        pass

    cursor.execute("UPDATE courses SET minor = 'yes' WHERE degree_type LIKE '%Undergraduate Minor%'")
    cursor.execute("UPDATE courses SET minor = 'no' WHERE minor IS NULL")
    cursor.execute("UPDATE courses SET degree_type = TRIM(SUBSTR(degree_type, 1, INSTR(degree_type, ',') - 1)) WHERE INSTR(degree_type, ',') > 0")

    cursor.execute('DROP TABLE IF EXISTS salaries')
    cursor.execute('''
    CREATE TABLE salaries (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        average_salary TEXT,
        source_degree TEXT
    )
    ''')

    cursor.execute('SELECT id, title FROM courses ORDER BY id')
    courses = cursor.fetchall()
    titles = [row[1] for row in courses]

    degree_links = collect_degree_links()
    print(f'Found {len(degree_links)} Payscale degree salary pages')

    for course_id, title in courses:
        matched_degree = best_degree_match(title, degree_links.keys())
        if matched_degree:
            url = degree_links[matched_degree]
            try:
                avg_salary = fetch_salary_page(url) or 'N/A'
                source_degree = matched_degree
            except Exception:
                avg_salary = 'N/A'
                source_degree = matched_degree
        else:
            avg_salary = 'N/A'
            source_degree = 'No match'

        cursor.execute('INSERT INTO salaries (id, title, average_salary, source_degree) VALUES (?, ?, ?, ?)',
                       (course_id, title, avg_salary, source_degree))
        print(f'Inserted salary row for {title}: {avg_salary} ({source_degree})')

    conn.commit()
    conn.close()
    print('Database updated with salary data')


if __name__ == '__main__':
    main()
