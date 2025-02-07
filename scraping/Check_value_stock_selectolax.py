import requests
import re
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
from rich.console import Console
from rich.table import Table
from pprint import pprint

url = "https://books.toscrape.com/"
Session_scrapping = requests.session()
reponse = Session_scrapping.get(url)
tree = HTMLParser(reponse.text)

console = Console()

categorie_urls = {}
url_livre = {}
stock = {}


def recuperation_url_categorie(tree: HTMLParser) -> dict:
    global categorie_urls
    categorie = tree.css("ul.nav.nav-list")
    categorie_urls = {
        categorie.text().strip(): url + categorie.attributes["href"]
        for t in tree.css("ul.nav.nav-list")
        for categorie in t.css("li > ul > li > a")
    }
    return categorie_urls


def parsing_categorie(categorie: str, url: str, tree: HTMLParser) -> str:
    recuperation_url_livre(categorie, url, tree)
    response = requests.get(url)
    tree_next_url = HTMLParser(response.text)
    next_url_button = tree_next_url.css("li.next > a")
    if len(next_url_button) == 0:
        return ""
    for i in next_url_button:
        next_link = i.attributes["href"]
        next_url = urljoin(url, next_link)
        parsing_categorie(categorie, next_url, tree_next_url)


def recuperation_url_livre(categorie: str, url: str, tree: HTMLParser) -> dict:
    global url_livre
    Response3 = Session_scrapping.get(url)
    tree_recup_url_livre = HTMLParser(Response3.text)
    recup_url_livre = tree_recup_url_livre.css("article.product_pod > h3 > a")
    for i in recup_url_livre:
        if i.attributes["title"] not in url_livre:
            url_livre[i.attributes["title"]] = {
                "categorie": categorie,
                "url": re.sub(
                    r"\.\./\.\./\.\./",
                    "https://books.toscrape.com/catalogue/",
                    i.attributes["href"],
                ),
            }
        else:
            id_duplicate_title = re.search(r"_\d+", i.attributes["href"])
            url_livre[
                i.attributes["title"] + " DUPLICATE " + id_duplicate_title.group()
            ] = {
                "categorie": categorie,
                "url": re.sub(
                    r"\.\./\.\./\.\./",
                    "https://books.toscrape.com/catalogue/",
                    i.attributes["href"],
                ),
            }
    print(url_livre)
    exit()
    return url_livre


def recup_info_livre(titre_livre: str, url: str, categorie: str) -> dict:
    session = Session_scrapping.get(url)
    tree_info_livre = HTMLParser(session.text)
    recup_stock = tree_info_livre.css("p.instock_availability")
    stock_livre = re.findall(r"\d{1,2}", recup_stock.get_text(strip=True))
    recup_livre = tree_info_livre.css("p.price_color")
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


recuperation_url_categorie(tree)

with console.status("[bold green]Récupération des livres en cours ...") as status:
    for categorie, url_categorie in categorie_urls.items():
        parsing_categorie(categorie, url_categorie, tree)
        console.log(f"Parsing de la catégoire : {categorie} terminé")
    console.log(f"Parsing terminé", style="bold blue")

with console.status("[bold green]Récupération du stock en cours...") as status:
    for titre_livre, livre_url in url_livre.items():
        print(livre_url["url"])
        recup_info_livre(titre_livre, livre_url["url"], livre_url["categorie"])
    console.log(f"Récupération du stock terminé", style="bold blue")

affiche_etat_stock(stock)
affiche_etat_stock_detail(stock)
