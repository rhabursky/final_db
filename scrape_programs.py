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
titles = []
for program in programs:
    title_span = program.find('span', class_='component-academic-program-list__item-name')
    
    if title_span:
        title = title_span.get_text(strip=True)
        titles.append(title)

titles.sort()
print(titles)