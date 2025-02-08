import requests
import re
from selectolax.parser import HTMLParser
from urllib.parse import urljoin
from rich.console import Console
from rich.table import Table
from pprint import pprint

# URL de base du site à scraper
url = "https://books.toscrape.com/"
# Initialisation de la session de scraping
Session_scrapping = requests.session()
# Récupération de la page d'accueil du site
reponse = Session_scrapping.get(url)
# Parsing du contenu HTML de la page d'accueil
tree = HTMLParser(reponse.text)

# Initialisation de la console Rich pour l'affichage
console = Console()

# Dictionnaires pour stocker les URLs des catégories, des livres et les informations de stock
categorie_urls = {}
url_livre = {}
stock = {}


def recuperation_url_categorie(tree: HTMLParser) -> dict:
    """
    Récupère les URLs des différentes catégories de livres à partir de la page d'accueil.

    Args:
        tree (HTMLParser): L'arbre HTML de la page d'accueil.

    Returns:
        dict: Un dictionnaire contenant les noms des catégories comme clés et leurs URLs comme valeurs.
    """
    global categorie_urls
    categorie = tree.css("ul.nav.nav-list")
    categorie_urls = {
        categorie.text().strip(): url + categorie.attributes["href"]
        for t in tree.css("ul.nav.nav-list")
        for categorie in t.css("li > ul > li > a")
    }
    return categorie_urls


def parsing_categorie(categorie: str, url: str, tree: HTMLParser) -> str:
    """
    Parse les pages de chaque catégorie pour récupérer les URLs des livres.

    Args:
        categorie (str): Le nom de la catégorie.
        url (str): L'URL de la catégorie.
        tree (HTMLParser): L'arbre HTML de la page de la catégorie.

    Returns:
        str: Une chaîne vide si aucune page suivante n'est trouvée.
    """
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
    """
    Récupère les URLs des livres à partir de la page de la catégorie.

    Args:
        categorie (str): Le nom de la catégorie.
        url (str): L'URL de la catégorie.
        tree (HTMLParser): L'arbre HTML de la page de la catégorie.

    Returns:
        dict: Un dictionnaire contenant les titres des livres comme clés et leurs informations (catégorie et URL) comme valeurs.
    """
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
    """
    Récupère les informations de stock et de prix pour un livre donné.

    Args:
        titre_livre (str): Le titre du livre.
        url (str): L'URL du livre.
        categorie (str): La catégorie du livre.

    Returns:
        dict: Un dictionnaire contenant les informations de stock mises à jour.
    """
    session = Session_scrapping.get(url)
    tree_info_livre = HTMLParser(session.text)
    recup_stock = tree_info_livre.css_first("p.instock.availability")
    stock_livre = re.findall(r"\d{1,2}", recup_stock.text(strip=True))
    recup_livre = tree_info_livre.css_first("p.price_color")
    prix_livre = re.search(r"\d{1,2}\.\d{1,2}", recup_livre.text())
    if not stock_livre or not prix_livre:
        return stock
    prix_stock = int(stock_livre[0]) * float(prix_livre.group())
    if stock.get(categorie) is None:
        stock[categorie] = []
        stock[categorie].append({"Valeur_stock_total": 0, "Nombre_titre": 0})
    stock[categorie].append(
        {
            "titre": titre_livre,
            "Prix Unitaire": prix_livre.group(),
            "quantité": stock_livre[0],
            "Valeur Stock": prix_stock,
        }
    )
    stock[categorie][0]["Valeur_stock_total"] += prix_stock
    stock[categorie][0]["Nombre_titre"] += 1
    return stock


def affiche_etat_stock(stock: dict):
    """
    Affiche un résumé de l'état du stock par catégorie.

    Args:
        stock (dict): Le dictionnaire contenant les informations de stock.
    """
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
    """
    Affiche un détail complet de l'état du stock par catégorie et par livre.

    Args:
        stock (dict): Le dictionnaire contenant les informations de stock.
    """
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


# Récupération des URLs des catégories à partir de la page d'accueil
recuperation_url_categorie(tree)

# Récupération des livres pour chaque catégorie
with console.status("[bold green]Récupération des livres en cours ...") as status:
    for categorie, url_categorie in categorie_urls.items():
        parsing_categorie(categorie, url_categorie, tree)
        console.log(f"Parsing de la catégorie : {categorie} terminé")
    console.log(f"Parsing terminé", style="bold blue")

# Récupération des informations de stock pour chaque livre
with console.status("[bold green]Récupération du stock en cours...") as status:
    for titre_livre, livre_url in url_livre.items():
        recup_info_livre(titre_livre, livre_url["url"], livre_url["categorie"])
    console.log(f"Récupération du stock terminé", style="bold blue")

# Affichage du résumé de l'état du stock
affiche_etat_stock(stock)
# Affichage du détail complet de l'état du stock
affiche_etat_stock_detail(stock)
