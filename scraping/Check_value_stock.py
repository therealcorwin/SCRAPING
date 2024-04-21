import requests
import re
from bs4 import BeautifulSoup
from pprint import pprint
from urllib.parse import urljoin

url = "https://books.toscrape.com/"
Session_scrapping = requests.session()
Response = Session_scrapping.get(url)
categorie_url = {}


def recuperation_url_categorie(session: requests) -> dict:
    soup = BeautifulSoup(session.text, "html.parser")
    aside = soup.find("div", class_="side_categories")
    categories = aside.find("ul").find("li").find("ul").find_all("a", href=True)
    for cat in categories:
        link_category = cat.get("href")
        categorie = cat.text.strip()
        categorie_url[categorie] = url + link_category
    return categorie_url


def recuperation_url_livre(url: str, categorie: str) -> list:
    pass


def parsing_categorie(url: str) -> str:
    Response2 = Session_scrapping.get(url)
    soup = BeautifulSoup(Response2.text, "html.parser")
    next_link = soup.select("li.next")
    if len(next_link) == 0:
        print(f"Fin de la page pour {url}")
        return ""

    for i in next_link:
        plop = i.a["href"]
        # p = re.findall(r"page-\d{1,2}.html", plop)
        next_url = urljoin(url, plop)
        print(next_url)
        # next_link = ""
        parsing_categorie(next_url)

    # print(next_url)


# recuperation_url_categorie(Response)
# for i, cle in enumerate(categorie_url.items(), start=2):
#    print(i, cle[0], cle[1])


parsing_categorie(url)
