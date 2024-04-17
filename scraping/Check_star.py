import requests
from bs4 import BeautifulSoup
from pprint import pprint

url = "https://books.toscrape.com/"
Session_scrapping = requests.session()
Response = Session_scrapping.get(url)
soup = BeautifulSoup(Response.text, "html.parser")

one_star_book = soup.select("p.star-rating.One")
for book in one_star_book:
    print(book.find_next("h3").find("a")["href"])
