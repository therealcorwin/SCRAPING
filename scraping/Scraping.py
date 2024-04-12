import requests
from bs4 import BeautifulSoup
from pprint import pprint

url = "https://books.toscrape.com/"
Response = requests.get(url)
soup = BeautifulSoup(Response.text, 'html.parser')

'''
Type Objet

find ==> TAG
    Methode find_*, children etc disponible

find_all ==> ResultSet
    Methode find_* etc indisponible, equivalent a peu pres à une liste python
'''
# Récupération catégorie

# Methode 1
print("\nRecupération Catégorie Methode 1\n")
aside = soup.find("div", class_="side_categories")
categorie = aside.find("ul").find("li").find("ul")
for cat in categorie.children:
    if cat.name:
        print(cat.text.strip())

# Methode 2
print("\nRecupération Catégorie Methode 2\n")
categorie2 = aside.find("ul").find("li").find("ul").find_all("li")
list = []
for i in categorie2:
    if i:
        # list.append(i.text.strip())
        print(i.text.strip())

# Recuperer Images Page Acceuil
'''
Données récupérées :
 <div class="image_container">
  <a href="catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html">
        <img
            alt="Mesaerion: The Best Science Fiction Stories 1800-1849" class="thumbnail"
            src="media/cache/09/a3/09a3aef48557576e1a85ba7efea8ecb7.jpg"
        />
  </a>
 </div>
im.img ==> Permet d'aller dans la baslise <img>. POssible de descendre dans les balises suivantes par ex: im.balise1.balise2 
im.img["src"] ==> Récupére l'attribut "src" de la balise <img>
'''

# Methode 1
print("\nRecupération image page d'acceuil\n")
image = soup.find("ol", class_="row").find_all("div", class_="image_container")
for im in image:
    print(im.img.get("src"))

# Methode2
'''
Donnée récupérées :
 <img
   alt="It's Only the Himalayas" class="thumbnail"
   src="media/cache/27/a5/27a53d0bb95bdd88288eaf66c9230d7e.jpg"
 />
im2.get("src") ==> Permet de récupérer l'attribu "src" de la balise <img>
'''

image2 = soup.find("section").find_all("img")
for im2 in image2:
    print(im2.get("src"))

# Récupérer tous les titres de livre de la page d'acceuil
'''
Donnée récupérées :

<article class="product_pod">
<div class="image_container">
<a href="catalogue/a-light-in-the-attic_1000/index.html"><img alt="A Light in the Attic" class="thumbnail" src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg"/></a>
</div>
<p class="star-rating Three">
<i class="icon-star"></i>
<i class="icon-star"></i>
<i class="icon-star"></i>
<i class="icon-star"></i>
<i class="icon-star"></i>
</p>
<h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>       
<div class="product_price">
<p class="price_color">Â£51.77</p>
<p class="instock availability">
<i class="icon-ok"></i>

        In stock

</p>
<form>
<button class="btn btn-primary btn-lock" data-loading-text="Adding..." type="submit">Add to basket</button>
</form>
</div>
'''
print("\nRecupération des titres des livre de la page d'acceuil\n")

titres = soup.find("ol", class_="row").find_all(
    "article", class_="product_pod")
for titre in titres:
    print(titre.h3.a.get("title"))

# Methode 2 Docstrings
print("\nRecupération des titres des livre de la page d'acceuil methode docstrings\n")

articles = soup.find_all("article", class_="product_pod")

'''
Données récupérées :

[<a href="catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html">
<img alt="Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991" class="thumbnail" 
src="media/cache/54/60/54607fe8945897cdcced0044103b10b6.jpg"/></a>, 
<a href="catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html" 
title="Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991">Our Band Could Be ...</a>]

'''
# Recupere toutes les balises articles avec la classe product_pod
for a in articles:
    # Recupere toutes les balises a
    titres = a.find_all("a")
# Teste s'il y a au moins 2 items dans les resultats obtenus
    if len(titres) >= 2:
        # Récupère le second item de la liste. Possible de faire avec titres[-1] pour prendre le dernier item.
        # Seulement s'il n'y a que deux elemens car le titre se trouve dans le scd item
        titre = titres[1]
# Recupere le contenu de la balise title.
# Titre["title"] utilisable mais si la cle n'existe pas ==> Erreur.  Donc on utilse get() pour eviter une erreur.
        print(titre.get("title"))

# Methode 3 Docstrings
print("\nRecupération des titres des livre de la page d'acceuil methode 2 docstrings\n")

# Cherche toutes les balises a contenant title
# possibilité de cibler un titre précis avec soup.find_all("a", title="Mon Titre")
titles_tag = soup.find_all("a", title=True)
# Comprenhension de liste
titles = [a["title"] for a in titles_tag]
pprint(titles)
