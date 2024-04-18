import requests
import re
from bs4 import BeautifulSoup
from pprint import pprint

url = "https://books.toscrape.com/"
Session_scrapping = requests.session()
Response = Session_scrapping.get(url)
soup = BeautifulSoup(Response.text, "html.parser")

one_star_book = soup.select("p.star-rating.One")
for livre in one_star_book:
    try:
        lien_livre = livre.find_next("h3").find("a")["href"]
    except AttributeError as e:
        print("Impossible de trouver la balise h3 ou a.")
        raise AttributeError from e
    except KeyError as e:
        print("Impossible de trouver l'attribut href.")
        raise KeyError from e
    try:
        titre_livre = livre.find_next("h3").find("a")["title"]
    except AttributeError as e:
        print("Impossible de trouver la balise h3 ou title.")
        raise AttributeError from e
    except KeyError as e:
        print("Impossible de trouver l'attribut title.")
        raise KeyError from e
    try:
        livre_id = re.findall(r"_\d+", lien_livre)[0][1:]
        # r"_\d+" == r"_\d{1,}
        print(f"titre à enlever : {titre_livre} ==> ID: {livre_id}")
    except IndexError as e:
        print("Impossible de trouver l'ID du livre.")
        raise IndexError from e
