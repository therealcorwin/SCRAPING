import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rich.console import Console
from rich.table import Table
from pprint import pprint

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
        return ""
    for i in next_url_button:
        next_link = i.a["href"]
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


def affiche_etat_stock(stock: dict):
    table = Table(title="Stock Information")
    table.add_column("Category", style="cyan", justify="center")
    table.add_column("Number of Titles", style="magenta", justify="center")
    table.add_column("Total Stock Value", style="yellow", justify="right")
    valeur_stock = 0
    for categorie in stock.keys():
        table.add_row(
            categorie,
            str(stock[categorie][0]["Nombre_titre"]),
            str(stock[categorie][0]["Valeur_stock_total"]),
        )
        valeur_stock += stock[categorie][0]["Valeur_stock_total"]
    table.add_row("Valeur Totale", "", str(valeur_stock))
    console.print(table)


def affiche_etat_stock_detail(stock: dict):
    table = Table(title="Stock Information")
    table.add_column("Category", style="cyan", justify="center")
    table.add_column("Titre", style="magenta", justify="center")
    table.add_column("Stock Dispo", style="magenta", justify="center")
    table.add_column("Prix Unit.", style="magenta", justify="center")
    table.add_column("Valeur Stock", style="yellow", justify="right")
    valeur_stock_global = 0
    for categorie, stock_item in stock.items():
        valeur_stock_categorie = 0
        for livre in stock[categorie][1:]:
            table.add_row(
                categorie,
                livre["titre"],
                str(livre["quantité"]),
                str(livre["Prix Unitaire"]),
                str(livre["Valeur Stock"]),
            )
            valeur_stock_categorie += livre["Valeur Stock"]
        valeur_stock_global += valeur_stock_categorie
        table.add_row("Valeur Stock", "", "", "", str(valeur_stock_categorie))
        table.add_row("******", "******", "******", "******", "******")
    table.add_row("Valeur Stock Global", "", "", "", str(valeur_stock_global))

    console.print(table)


# parsing_categorie(
#    "Fantasy",
#    "https://books.toscrape.com/catalogue/category/books/fantasy_19/index.html",
# )
# for url, livre in url_livre.items():
#    print(url)


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

# affiche_etat_stock(stock)
affiche_etat_stock_detail(stock)
