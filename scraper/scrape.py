import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://books.toscrape.com"
API_URL = "http://localhost:8000/api/books/upload/"
OUTPUT_PATH = Path(__file__).parent / "books_raw.json"

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def make_driver() -> webdriver.Chrome:
  options = Options()
  options.add_argument("--headless=new")
  options.add_argument("--disable-gpu")
  options.add_argument("--no-sandbox")
  return webdriver.Chrome(options=options)


def parse_book_detail(driver: webdriver.Chrome, detail_url: str) -> tuple[str, str]:
  driver.get(detail_url)
  soup = BeautifulSoup(driver.page_source, "html.parser")
  desc_node = soup.select_one("#product_description ~ p")
  image_node = soup.select_one(".item.active img")
  description = desc_node.get_text(strip=True) if desc_node else ""
  image_url = ""
  if image_node and image_node.get("src"):
      image_url = BASE_URL + "/" + image_node["src"].replace("../", "")
  return description, image_url


def scrape_books(pages: int = 5):
  driver = make_driver()
  all_books = []

  try:
      for page in range(1, pages + 1):
          list_url = f"{BASE_URL}/catalogue/page-{page}.html"
          driver.get(list_url)
          soup = BeautifulSoup(driver.page_source, "html.parser")
          cards = soup.select("article.product_pod")

          for card in cards:
              title_node = card.select_one("h3 a")
              if not title_node:
                  continue
              title = title_node.get("title", "Unknown")
              rel_link = title_node.get("href", "")
              detail_url = f"{BASE_URL}/catalogue/{rel_link.replace('../../../', '')}"
              rating_text = card.select_one("p.star-rating").get("class", ["", "Zero"])[1]
              rating = RATING_MAP.get(rating_text, 0)
              price = card.select_one("p.price_color").get_text(strip=True)

              description, cover_image_url = parse_book_detail(driver, detail_url)

              book = {
                  "title": title,
                  "author": "Unknown",
                  "rating": rating,
                  "price": price,
                  "description": description,
                  "cover_image_url": cover_image_url,
                  "book_url": detail_url,
              }
              all_books.append(book)

              try:
                  requests.post(API_URL, json=book, timeout=30).raise_for_status()
              except requests.RequestException as exc:
                  print(f"Failed to upload {title}: {exc}")

              time.sleep(1)
  finally:
      driver.quit()

  OUTPUT_PATH.write_text(json.dumps(all_books, indent=2))
  print(f"Scraped {len(all_books)} books")


if __name__ == "__main__":
  scrape_books(pages=5)
