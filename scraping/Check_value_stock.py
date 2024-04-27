import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console

url = "https://books.toscrape.com/"
console = Console()
Session_scrapping = requests.session()
Response = Session_scrapping.get(url)

categorie_url = {}
url_livre = {}
stock = {}


def recuperation_url_categorie(session: requests) -> dict:
    soup = BeautifulSoup(session.text, "html.parser")
    aside = soup.find("div", class_="side_categories")
    categories = aside.find("ul").find("li").find("ul").find_all("a", href=True)
    for cat in categories:
        link_category = cat.get("href")
        categorie = cat.text.strip()
        categorie_url[categorie] = url + link_category
    return categorie_url


def parsing_categorie(categorie: str, url: str) -> str:
    recuperation_url_livre(categorie, url)
    Response2 = Session_scrapping.get(url)
    soup = BeautifulSoup(Response2.text, "html.parser")
    next_url_button = soup.select("li.next")
    if len(next_url_button) == 0:
        # print(f"Fin de la page pour {url}")
        return ""
    for i in next_url_button:
        next_link = i.a["href"]
        # p = re.findall(r"page-\d{1,2}.html", plop)
        next_url = urljoin(url, next_link)
        parsing_categorie(categorie, next_url)


def recuperation_url_livre(categorie: str, url: str) -> dict:
    global url_livre
    soup_url_livre = Session_scrapping.get(url)
    recup2 = BeautifulSoup(soup_url_livre.text, "html.parser")
    recup_url_livre = recup2.select("article.product_pod")
    for i in recup_url_livre:
        url_livre[i.h3.a["title"]] = {
            "categorie": categorie,
            "url": re.sub(
                r"\.\./\.\./\.\./", "https://books.toscrape.com/catalogue/", i.a["href"]
            ),
        }
    return url_livre


def recup_info_livre(titre_livre: str, url: str, categorie: str) -> dict:
    session = Session_scrapping.get(url)
    soup_info_livre = BeautifulSoup(session.text, "html.parser")
    recup_stock = soup_info_livre.find("p", class_="instock availability")
    stock_livre = re.findall(r"\d{1,2}", recup_stock.get_text(strip=True))
    recup_livre = soup_info_livre.select_one("p.price_color")
    prix_livre = re.search(r"\d{1,2}\.\d{1,2}", recup_livre.get_text())
    prix_stock = int(stock_livre[0]) * float(prix_livre[0])
    if stock.get(categorie) is None:
        stock[categorie] = []
        stock[categorie].append({"Valeur_stock_total": 0, "Nombre_titre": 0})

    stock[categorie].append(
        {
            "titre": titre_livre,
            "Prix Unitaire": prix_livre[0],
            "quantité": stock_livre[0],
            "Valeur Stock": prix_stock,
        }
    )
    stock[categorie][0]["Valeur_stock_total"] += prix_stock
    stock[categorie][0]["Nombre_titre"] += 1
    return stock


recuperation_url_categorie(Response)


with console.status("[bold green]Récupération des livres en cours ...") as status:
    for categorie, url_categorie in categorie_url.items():
        parsing_categorie(categorie, url_categorie)
        console.log(f"Parsing de la catégoire : {categorie} terminé")
    console.log(f"Parsing terminé", style="bold blue")


with console.status("[bold green]Récupération du stock en cours...") as status:
    for titre_livre, livre_url in url_livre.items():
        recup_info_livre(titre_livre, livre_url["url"], livre_url["categorie"])
    console.log(f"Récupération du stock terminé", style="bold blue")

    # pprint(stock)
