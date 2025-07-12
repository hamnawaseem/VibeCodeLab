# cli_version/css_daily_digest.py

import requests
from bs4 import BeautifulSoup
from langchain.llms import OpenAI
from crewai import Agent
import os

llm = OpenAI(temperature=0.3)

def get_article_links():
    url = "https://www.dawn.com/opinion"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    def extract_articles(heading_text, limit):
        heading = soup.find(lambda tag: tag.name == "h2" and heading_text in tag.text)
        articles = []
        if heading:
            for sibling in heading.find_all_next():
                if sibling.name == "article":
                    title_tag = sibling.find("h2", class_="story__title")
                    if title_tag and title_tag.a:
                        title = title_tag.a.get_text(strip=True)
                        link = title_tag.a['href']
                        articles.append({"title": title, "link": link})
                    if len(articles) == limit:
                        break
        return articles

    opinion = extract_articles("Opinion", 4)
    editorial = extract_articles("Editorial", 3)
    return opinion + editorial

def fetch_article_text(link):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    article_body = soup.find("div", class_="story__content")
    if not article_body:
        return ""
    return "\n".join(tag.get_text(" ", strip=True) for tag in article_body.find_all(['p', 'h2', 'li']))

def summarize_article(text):
    return llm(f"Summarize this article for CSS aspirants in 3-4 lines:\n\n{text}")

def extract_vocabulary(text):
    return llm(f"""Extract 10 vocabulary words from this article with definitions, synonyms, antonyms, examples:\n{text}""")

def extract_quotes(text):
    return llm(f"""Extract facts, stats, or quotes for CSS essays from this article:\n{text}""")

def run_daily_digest():
    print("Fetching articles...")
    articles = get_article_links()
    texts = [fetch_article_text(a['link']) for a in articles]
    summaries = [summarize_article(t) for t in texts]
    vocab_lists = [extract_vocabulary(t) for t in texts]
    quotes = [extract_quotes(t) for t in texts]

    print("\nCSS Daily Digest\n")
    for i, article in enumerate(articles):
        print(f"=== {article['title']} ===")
        print(f"Link: {article['link']}\n")
        print(f"Summary:\n{summaries[i]}\n")
        print(f"Vocabulary:\n{vocab_lists[i]}\n")
        print(f"Quotes/Facts:\n{quotes[i]}\n")
        print("-" * 40)

if __name__ == "__main__":
    run_daily_digest()
