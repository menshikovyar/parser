import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

base_url = "https://habr.com/ru/hub/machine_learning/"

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            logging.info(f"Fetching URL {url}")
            page_content = await response.text()
            logging.debug(page_content[:1000])  
            return page_content
    except aiohttp.ClientError as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None

async def fetch_articles(url):
    async with aiohttp.ClientSession() as session:
        response_text = await fetch(session, url)
        if response_text:
            soup = BeautifulSoup(response_text, "html.parser")
            logging.info("Parsing articles")
            articles = []

            
            article_elements = soup.select(".tm-article-snippet, .tm-articles-list__item, article")
            logging.debug(f"Found {len(article_elements)} article elements")

            seen_articles = set()
            for article in article_elements:
                title_tag = article.select_one(".tm-article-snippet__title-link, .tm-title__link")
                if title_tag:
                    title = title_tag.text.strip()
                    link = f"https://habr.com{title_tag['href']}"
                    if link not in seen_articles:
                        seen_articles.add(link)
                        articles.append({
                            'title': title,
                            'link': link
                        })
                else:
                    logging.debug("No title found in article element")
            logging.info(f"Found {len(articles)} articles")
            return articles
        else:
            logging.warning("Failed to fetch articles")
            return []

@app.route('/')
def home():
    return "Welcome to the Article Scraper API! Use /articles to fetch articles."

@app.route('/articles', methods=['GET'])
async def display_articles():
    articles = await fetch_articles(base_url)
    if articles:
        return render_template('articles.html', articles=articles)
    else:
        return render_template('articles.html', articles=[]), 404

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
