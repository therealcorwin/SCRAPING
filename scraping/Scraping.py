import requests
from bs4 import BeautifulSoup
from pprint import pprint

url = "https://books.toscrape.com/"
Response = requests.get(url)
soup = BeautifulSoup(Response.text, 'html.parser')
"""
titre = soup.find_all('article', class_='product_pod')

for t in titre:
    titres = t.find_all_next('a')[1]
    print(titres.get('title'))
"""

aside = soup.find("div", class_="side_categories")
categorie = aside.find("ul").find("li").find("ul").find_all("li")
cat = aside.find("ul").find("li").find("ul")

for c in cat.children:
    if c.name:
        print(c.text.strip())

list = []
for i in categorie:
    if i:
        list.append(i.text.strip())
# print(list)
