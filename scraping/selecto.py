import requests
import re
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
from rich.console import Console
from rich.table import Table
from loguru import logger

url = "https://books.toscrape.com/"
Session_scrapping = requests.session()
reponse = Session_scrapping.get(url)
tree = HTMLParser(reponse.text)

console = Console()

categorie_urls = {}
url_livre = {}
stock = {}


def recuperation_url_categorie(session: requests) -> dict:
    tree = HTMLParser(session.text)
    categories = tree.css("div.side_categories > ul > li > ul > li > a")
    for cat in categories:
        link_category = cat.attributes["href"]
        categorie = cat.text().strip()
        categorie_url[categorie] = urljoin(url, link_category)
    return categorie_url


def parsing_categorie(categorie: str, url: str) -> str:
    recuperation_url_livre(categorie, url)
    Response2 = Session_scrapping.get(url)
    tree = HTMLParser(Response2.text)
    next_url_button = tree.css_first("li.next > a")
    if next_url_button:
        next_url = urljoin(url, next_url_button.attributes["href"])
        parsing_categorie(categorie, next_url)


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
    return url_livre


def recup_info_livre(titre_livre: str, url: str, categorie: str) -> dict:
    print(url)
    session = Session_scrapping.get(url)
    tree_info_livre = HTMLParser(session.text)
    recup_stock = tree_info_livre.css_first("p.availability.instock")
    print(recup_stock.text())
    # stock_livre = re.findall(r"\d{1,2}", recup_stock.get_text(strip=True))
    # recup_livre = tree_info_livre.css("p.price_color")
    # prix_livre = re.search(r"\d{1,2}\.\d{1,2}", recup_livre.get_text())
    # prix_stock = int(stock_livre[0]) * float(prix_livre[0])
    # if stock.get(categorie) is None:
    #    stock[categorie] = []
    #    stock[categorie].append({"Valeur_stock_total": 0, "Nombre_titre": 0})
    # stock[categorie].append(
    #    {
    #        "titre": titre_livre,
    #        "Prix Unitaire": prix_livre[0],
    #        "quantité": stock_livre[0],
    #        "Valeur Stock": prix_stock,
    #    }
    # )
    # stock[categorie][0]["Valeur_stock_total"] += prix_stock
    # stock[categorie][0]["Nombre_titre"] += 1
    # return stock


# def recup_info_livre(titre_livre: str, url: str, categorie: str) -> dict:
#    session = Session_scrapping.get(url)
#    tree = HTMLParser(session.text)
#
#    # Récupération du stock
#    recup_stock = tree.css_first("p.instock.availability")
#    if recup_stock:
#        stock_livre = re.findall(r"\d+", recup_stock.text(strip=True))
#        if stock_livre:
#            stock_livre = stock_livre[0]
#        else:
#            logger.warning(f"Aucune quantité trouvée pour {titre_livre}")
#            stock_livre = "0"
#    else:
#        logger.warning(f"Aucune information de stock trouvée pour {titre_livre}")
#        stock_livre = "0"
#
#    # Récupération du prix
#    recup_livre = tree.css_first("p.price_color")
#    if recup_livre:
#        prix_livre = re.search(r"\d+\.\d{2}", recup_livre.text())
#        if prix_livre:
#            prix_livre = prix_livre.group()
#        else:
#            logger.warning(f"Format de prix invalide pour {titre_livre}")
#            prix_livre = "0.00"
#    else:
#        logger.warning(f"Aucun prix trouvé pour {titre_livre}")
#        prix_livre = "0.00"
#
#    # Calcul de la valeur du stock
#    prix_stock = float(stock_livre) * float(prix_livre)
#
#    logger.info(
#        f"Livre: {titre_livre}, Stock: {stock_livre}, Prix: {prix_livre}, Valeur stock: {prix_stock}"
#    )
#
#    if stock.get(categorie) is None:
#        stock[categorie] = []
#        stock[categorie].append({"Valeur_stock_total": 0, "Nombre_titre": 0})
#    stock[categorie].append(
#        {
#            "titre": titre_livre,
#            "Prix Unitaire": prix_livre,
#            "quantité": stock_livre,
#            "Valeur Stock": prix_stock,
#        }
#    )
#    stock[categorie][0]["Valeur_stock_total"] += prix_stock
#    stock[categorie][0]["Nombre_titre"] += 1
#    return stock


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

affiche_etat_stock(stock)
affiche_etat_stock_detail(stock)
