# Importation des modules nécessaires
import requests  # Pour effectuer des requêtes HTTP
import re  # Pour les expressions régulières
from bs4 import BeautifulSoup  # Pour parser le contenu HTML avec BeautifulSoup
from urllib.parse import urljoin  # Pour manipuler les URLs
from rich.console import Console  # Pour l'affichage dans la console
from rich.table import Table  # Pour afficher des tableaux dans la console
from pprint import pprint  # Pour afficher des données de manière formatée

# URL de base du site à scraper
url = "https://books.toscrape.com/"

# Initialisation de la console Rich pour l'affichage
console = Console()

# Initialisation de la session de scraping
Session_scrapping = requests.session()

# Récupération de la page d'accueil du site
Response = Session_scrapping.get(url)

# Dictionnaires pour stocker les URLs des catégories, des livres et les informations de stock
categorie_url = {}
url_livre = {}
stock = {}


def recuperation_url_categorie(session: requests) -> dict:
    """
    Récupère les URLs des différentes catégories de livres à partir de la page d'accueil.

    Args:
        session (requests): La session de scraping.

    Returns:
        dict: Un dictionnaire contenant les noms des catégories comme clés et leurs URLs comme valeurs.
    """
    # Parsing du contenu HTML de la page d'accueil
    soup = BeautifulSoup(session.text, "html.parser")
    # Sélection de la section des catégories
    aside = soup.find("div", class_="side_categories")
    # Sélection des liens des catégories
    categories = aside.find("ul").find("li").find("ul").find_all("a", href=True)
    # Boucle sur les catégories pour extraire les URLs
    for cat in categories:
        # Récupération du lien de la catégorie
        link_category = cat.get("href")
        # Récupération du nom de la catégorie
        categorie = cat.text.strip()
        # Ajout de la catégorie et de son URL au dictionnaire
        categorie_url[categorie] = url + link_category
    # Retourne le dictionnaire des catégories
    return categorie_url


def parsing_categorie(categorie: str, url: str) -> str:
    """
    Parse les pages de chaque catégorie pour récupérer les URLs des livres.

    Args:
        categorie (str): Le nom de la catégorie.
        url (str): L'URL de la catégorie.

    Returns:
        str: Une chaîne vide si aucune page suivante n'est trouvée.
    """
    # Appel de la fonction pour récupérer les URLs des livres
    recuperation_url_livre(categorie, url)
    # Requête HTTP pour récupérer la page de la catégorie
    Response2 = Session_scrapping.get(url)
    # Parsing du contenu HTML de la page de la catégorie
    soup = BeautifulSoup(Response2.text, "html.parser")
    # Sélection du bouton de la page suivante
    next_url_button = soup.select("li.next")
    # Si aucun bouton de page suivante n'est trouvé
    if len(next_url_button) == 0:
        # Retourne une chaîne vide
        return ""
    # Boucle sur les boutons de page suivante
    for i in next_url_button:
        # Récupération de l'URL de la page suivante
        next_link = i.a["href"]
        # Construction de l'URL complète de la page suivante
        next_url = urljoin(url, next_link)
        # Appel récursif de la fonction pour parser la page suivante
        parsing_categorie(categorie, next_url)


def recuperation_url_livre(categorie: str, url: str) -> dict:
    """
    Récupère les URLs des livres à partir de la page de la catégorie.

    Args:
        categorie (str): Le nom de la catégorie.
        url (str): L'URL de la catégorie.

    Returns:
        dict: Un dictionnaire contenant les titres des livres comme clés et leurs informations (catégorie et URL) comme valeurs.
    """
    # Utilisation de la variable globale url_livre
    global url_livre
    # Requête HTTP pour récupérer la page de la catégorie
    soup_url_livre = Session_scrapping.get(url)
    # Parsing du contenu HTML de la page de la catégorie
    recup2 = BeautifulSoup(soup_url_livre.text, "html.parser")
    # Sélection des liens des livres
    recup_url_livre = recup2.select("article.product_pod")
    # Boucle sur les liens des livres
    for i in recup_url_livre:
        # Si le titre du livre n'est pas déjà dans le dictionnaire
        if i.h3.a["title"] not in url_livre:
            # Ajout du livre au dictionnaire
            url_livre[i.h3.a["title"]] = {
                # Ajout de la catégorie du livre
                "categorie": categorie,
                # Remplacement de l'URL relative par l'URL absolue
                "url": re.sub(
                    r"\.\./\.\./\.\./",
                    "https://books.toscrape.com/catalogue/",
                    i.a["href"],
                ),
            }
        # Si le titre du livre est déjà dans le dictionnaire
        else:
            # Recherche d'un identifiant unique pour le titre dupliqué
            id_duplicate_title = re.search(r"_\d+", i.h3.a["href"])
            # Ajout du titre dupliqué avec un identifiant unique
            url_livre[i.h3.a["title"] + " DUPLICATE " + id_duplicate_title.group()] = {
                # Ajout de la catégorie du livre
                "categorie": categorie,
                # Remplacement de l'URL relative par l'URL absolue
                "url": re.sub(
                    r"\.\./\.\./\.\./",
                    "https://books.toscrape.com/catalogue/",
                    i.a["href"],
                ),
            }
    # Retourne le dictionnaire des livres
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
    # Requête HTTP pour récupérer la page du livre
    session = Session_scrapping.get(url)
    # Parsing du contenu HTML de la page du livre
    soup_info_livre = BeautifulSoup(session.text, "html.parser")
    # Sélection de l'élément contenant les informations de stock
    recup_stock = soup_info_livre.find("p", class_="instock availability")
    # Extraction du nombre de livres en stock
    stock_livre = re.findall(r"\d{1,2}", recup_stock.get_text(strip=True))
    # Sélection de l'élément contenant le prix du livre
    recup_livre = soup_info_livre.select_one("p.price_color")
    # Extraction du prix du livre
    prix_livre = re.search(r"\d{1,2}\.\d{1,2}", recup_livre.get_text())
    # Calcul de la valeur totale du stock pour ce livre
    prix_stock = int(stock_livre[0]) * float(prix_livre[0])
    # Si la catégorie n'existe pas encore dans le dictionnaire de stock
    if stock.get(categorie) is None:
        # Initialisation de la liste pour cette catégorie
        stock[categorie] = []
        # Ajout des informations de stock initiales pour cette catégorie
        stock[categorie].append({"Valeur_stock_total": 0, "Nombre_titre": 0})
    # Ajout des informations de stock pour ce livre
    stock[categorie].append(
        {
            # Titre du livre
            "titre": titre_livre,
            # Prix unitaire du livre
            "Prix Unitaire": prix_livre[0],
            # Quantité en stock
            "quantité": stock_livre[0],
            # Valeur totale du stock pour ce livre
            "Valeur Stock": prix_stock,
        }
    )
    # Mise à jour de la valeur totale du stock pour cette catégorie
    stock[categorie][0]["Valeur_stock_total"] += prix_stock
    # Incrémentation du nombre de titres pour cette catégorie
    stock[categorie][0]["Nombre_titre"] += 1
    # Retourne le dictionnaire de stock mis à jour
    return stock


def affiche_etat_stock(stock: dict):
    """
    Affiche un résumé de l'état du stock par catégorie.

    Args:
        stock (dict): Le dictionnaire contenant les informations de stock.
    """
    # Création d'un tableau pour afficher les informations de stock
    table = Table(title="Stock Information")
    # Ajout de la colonne "Category"
    table.add_column("Category", style="cyan", justify="center")
    # Ajout de la colonne "Number of Titles"
    table.add_column("Number of Titles", style="magenta", justify="center")
    # Ajout de la colonne "Total Stock Value"
    table.add_column("Total Stock Value", style="yellow", justify="right")
    # Initialisation de la valeur totale du stock
    valeur_stock = 0
    # Boucle sur les catégories
    for categorie in stock.keys():
        # Ajout d'une ligne au tableau pour chaque catégorie
        table.add_row(
            # Nom de la catégorie
            categorie,
            # Nombre de titres dans cette catégorie
            str(stock[categorie][0]["Nombre_titre"]),
            # Valeur totale du stock pour cette catégorie
            str(stock[categorie][0]["Valeur_stock_total"]),
        )
        # Ajout de la valeur du stock de cette catégorie à la valeur totale
        valeur_stock += stock[categorie][0]["Valeur_stock_total"]
    # Ajout de la ligne pour la valeur totale du stock
    table.add_row("Valeur Totale", "", str(valeur_stock))
    # Affichage du tableau
    console.print(table)


def affiche_etat_stock_detail(stock: dict):
    """
    Affiche un détail complet de l'état du stock par catégorie et par livre.

    Args:
        stock (dict): Le dictionnaire contenant les informations de stock.
    """
    # Création d'un tableau pour afficher les informations de stock
    table = Table(title="Stock Information")
    # Ajout de la colonne "Category"
    table.add_column("Category", style="cyan", justify="center")
    # Ajout de la colonne "Titre"
    table.add_column("Titre", style="magenta", justify="center")
    # Ajout de la colonne "Stock Dispo"
    table.add_column("Stock Dispo", style="magenta", justify="center")
    # Ajout de la colonne "Prix Unit."
    table.add_column("Prix Unit.", style="magenta", justify="center")
    # Ajout de la colonne "Valeur Stock"
    table.add_column("Valeur Stock", style="yellow", justify="right")
    # Initialisation de la valeur totale du stock global
    valeur_stock_global = 0
    # Boucle sur les catégories et leurs informations de stock
    for categorie, stock_item in stock.items():
        # Initialisation de la valeur totale du stock pour cette catégorie
        valeur_stock_categorie = 0
        # Boucle sur les livres de cette catégorie
        for livre in stock[categorie][1:]:
            # Ajout d'une ligne au tableau pour chaque livre
            table.add_row(
                # Nom de la catégorie
                categorie,
                # Titre du livre
                livre["titre"],
                # Quantité en stock
                str(livre["quantité"]),
                # Prix unitaire
                str(livre["Prix Unitaire"]),
                # Valeur totale du stock pour ce livre
                str(livre["Valeur Stock"]),
            )
            # Ajout de la valeur du stock de ce livre à la valeur totale de la catégorie
            valeur_stock_categorie += livre["Valeur Stock"]
        # Ajout de la valeur du stock de cette catégorie à la valeur totale globale
        valeur_stock_global += valeur_stock_categorie
        # Ajout de la ligne pour la valeur totale de la catégorie
        table.add_row("Valeur Stock", "", "", "", str(valeur_stock_categorie))
        # Ligne de séparation
        table.add_row("******", "******", "******", "******", "******")
    # Ajout de la ligne pour la valeur totale du stock global
    table.add_row("Valeur Stock Global", "", "", "", str(valeur_stock_global))

    # Affichage du tableau
    console.print(table)


# Récupération des URLs des catégories à partir de la page d'accueil
recuperation_url_categorie(Response)

# Récupération des livres pour chaque catégorie
with console.status("[bold green]Récupération des livres en cours ...") as status:
    # Boucle sur les catégories et leurs URLs
    for categorie, url_categorie in categorie_url.items():
        # Appel de la fonction pour parser les pages de chaque catégorie
        parsing_categorie(categorie, url_categorie)
        # Log de la fin du parsing de la catégorie
        console.log(f"Parsing de la catégorie : {categorie} terminé")
    # Log de la fin du parsing
    console.log(f"Parsing terminé", style="bold blue")

# Récupération des informations de stock pour chaque livre
with console.status("[bold green]Récupération du stock en cours...") as status:
    # Boucle sur les livres et leurs URLs
    for titre_livre, livre_url in url_livre.items():
        # Appel de la fonction pour récupérer les informations de stock
        recup_info_livre(titre_livre, livre_url["url"], livre_url["categorie"])
    # Log de la fin de la récupération du stock
    console.log(f"Récupération du stock terminé", style="bold blue")

# Affichage du résumé de l'état du stock
affiche_etat_stock(stock)

# Affichage du détail complet de l'état du stock
affiche_etat_stock_detail(stock)
