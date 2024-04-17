import requests
from bs4 import BeautifulSoup
from pprint import pprint

url_cat = {}
url = "https://books.toscrape.com/"
Session_scrapping = requests.session()
Response = Session_scrapping.get(url)
soup = BeautifulSoup(Response.text, "html.parser")


aside = soup.find("div", class_="side_categories")
categories = aside.find("ul").find("li").find("ul").find_all("a", href=True)
for cat in categories:
    link_category = cat.get("href")
    categorie = cat.text.strip()
    url_cat[categorie] = url + link_category


def check_vol_cat(category, url, seuil, session):
    response2 = session.get(url)
    soup2 = BeautifulSoup(response2.text, "html.parser")
    qty = soup2.find("form", class_="form-horizontal")
    if int(qty.strong.get_text()) <= seuil:
        print(category, qty.strong.get_text())


for c, u in url_cat.items():
    check_vol_cat(c, u, 1, Session_scrapping)
