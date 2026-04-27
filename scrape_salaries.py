import requests
from bs4 import BeautifulSoup
import re

# Base URL
base_url = "https://www.payscale.com"

# Main degree page
main_url = base_url + "/research/US/Degree"

# Fetch main page
response = requests.get(main_url)
response.raise_for_status()
soup = BeautifulSoup(response.content, 'html.parser')

# Find category links
categories = {}
category_links = soup.find_all('a', href=re.compile(r'/research/US/Degree/'))

for link in category_links:
    href = link.get('href')
    text = link.get_text(strip=True)
    if href and text:
        categories[text] = base_url + href

print("Categories found:")
for cat, url in categories.items():
    print(f"{cat}: {url}")

# Now, for each category, fetch the page and find degrees
all_degrees = {}

for cat, cat_url in categories.items():
    print(f"Fetching category: {cat}")
    try:
        response = requests.get(cat_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find degree links
        degree_links = soup.find_all('a', href=re.compile(r'/research/US/Degree=.*/Salary'))

        for link in degree_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            if href and text:
                degree_url = base_url + href
                all_degrees[text] = degree_url
    except Exception as e:
        print(f"Error fetching {cat}: {e}")

print(f"\nTotal degrees found: {len(all_degrees)}")

# Now, map programs to degrees
programs = [
    "Accounting", "Anthropology and Archaeology", "Applied Sociology", "Art", "Art Therapy",
    "Biochemistry", "Biology", "Business Administration", "Chemistry & Biochemistry", "Communication",
    "Computer Science", "Criminal Justice", "Dance", "Data Science", "Economics",
    "English", "Environmental Science", "Exercise Science", "Fashion Merchandising", "Finance",
    "Forensic Science", "Graphic Design", "History", "Hospitality Management", "Human Resource Management",
    "Information Systems", "Intelligence Studies", "International Business", "Journalism", "Liberal Studies",
    "Management", "Marketing", "Mathematics", "Music", "Music Education",
    "Neuroscience", "Nursing", "Philosophy", "Physics", "Political Science",
    "Pre_Athletic Training", "Psychology", "Public Health", "Religious Studies", "Russian Studies",
    "Social Work", "Sociology", "Spanish and Spanish Education", "Sport and Event Management",
    "Sport Business Management", "Sports Medicine", "Studio Art"
]

# Function to find best match
def find_best_match(program, degrees):
    # Simple matching: check if program is in degree name or vice versa
    for degree in degrees:
        if program.lower() in degree.lower() or degree.lower() in program.lower():
            return degree
    return None

matched_degrees = {}
for program in programs:
    match = find_best_match(program, all_degrees.keys())
    if match:
        matched_degrees[program] = (match, all_degrees[match])
    else:
        matched_degrees[program] = None

print("\nMatched degrees:")
for prog, match in matched_degrees.items():
    if match:
        print(f"{prog}: {match[0]} - {match[1]}")
    else:
        print(f"{prog}: No match")

# Now, for each matched degree, fetch the salary
results = []
for program, match in matched_degrees.items():
    if match:
        degree_name, url = match
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the salary span
            salary_span = soup.find('span', class_='default-overview__value')
            if salary_span:
                salary = salary_span.get_text(strip=True)
                results.append((program, salary))
            else:
                results.append((program, 'N/A'))
        except Exception as e:
            print(f"Error fetching salary for {program}: {e}")
            results.append((program, 'N/A'))
    else:
        results.append((program, 'N/A'))

# Print results
print("\nResults:")
for title, salary in results:
    print(f"('{title}', '{salary}'),")