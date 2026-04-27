import requests
from bs4 import BeautifulSoup

url = "https://www.mercyhurst.edu/academics/all-academic-programs?field_program_type_target_id=19"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

titles = []
for span in soup.find_all('span', class_='component-academic-program-list__item-name'):
    title = span.get_text(strip=True)
    if title:
        titles.append(title)

titles.sort()
print(titles)