# Importation des modules nécessaires
import requests  # Pour effectuer des requêtes HTTP
from bs4 import BeautifulSoup  # Pour parser le contenu HTML avec BeautifulSoup
from pprint import pprint  # Pour afficher des données de manière formatée

# Initialisation du dictionnaire pour stocker les URLs des catégories
url_cat = {}

# URL de base du site à scraper
url = "https://books.toscrape.com/"

# Initialisation de la session de scraping
Session_scrapping = requests.session()

# Récupération de la page d'accueil du site
Response = Session_scrapping.get(url)

# Parsing du contenu HTML de la page d'accueil
soup = BeautifulSoup(Response.text, "html.parser")

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
    url_cat[categorie] = url + link_category


def check_vol_cat(category, url, seuil, session):
    """
    Vérifie le volume de livres dans une catégorie et affiche ceux en dessous d'un seuil.

    Args:
        category (str): Le nom de la catégorie.
        url (str): L'URL de la catégorie.
        seuil (int): Le seuil de volume pour afficher la catégorie.
        session (requests.Session): La session de scraping.
    """
    # Requête HTTP pour récupérer la page de la catégorie
    response2 = session.get(url)
    # Parsing du contenu HTML de la page de la catégorie
    soup2 = BeautifulSoup(response2.text, "html.parser")
    # Sélection de l'élément contenant la quantité de livres
    qty = soup2.find("form", class_="form-horizontal")
    # Si la quantité de livres est inférieure ou égale au seuil
    if int(qty.strong.get_text()) <= seuil:
        # Affiche le nom de la catégorie et la quantité de livres
        print(category, qty.strong.get_text())


# Boucle sur les catégories et leurs URLs
for c, u in url_cat.items():
    # Appel de la fonction pour vérifier le volume de livres dans chaque catégorie
    check_vol_cat(c, u, 1, Session_scrapping)
