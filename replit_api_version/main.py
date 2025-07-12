# replit_api_version/main.py

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from langchain.llms import OpenAI
import os

app = Flask(__name__)
llm = OpenAI(temperature=0.3)

def get_articles():
    url = "https://www.dawn.com/opinion"
    headers = {"User-Agent": "Mozilla/5.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

    def extract(heading, limit):
        h2 = soup.find(lambda tag: tag.name == "h2" and heading in tag.text)
        articles = []
        if h2:
            for sib in h2.find_all_next():
                if sib.name == "article":
                    tag = sib.find("h2", class_="story__title")
                    if tag and tag.a:
                        articles.append({"title": tag.a.get_text(strip=True), "link": tag.a["href"]})
                    if len(articles) == limit:
                        break
        return articles

    return extract("Opinion", 4) + extract("Editorial", 3)

def fetch_text(link):
    soup = BeautifulSoup(requests.get(link, headers={"User-Agent": "Mozilla/5.0"}).text, "html.parser")
    body = soup.find("div", class_="story__content")
    return "\n".join(tag.get_text(" ", strip=True) for tag in body.find_all(['p', 'h2', 'li'])) if body else ""

def summarize(text): return llm(f"Summarize for CSS aspirants:\n{text}")
def vocab(text): return llm(f"Extract 10 vocab words with details:\n{text}")
def quotes(text): return llm(f"Extract facts/stats/quotes:\n{text}")

@app.route("/", methods=["GET"])
def daily_digest():
    articles = get_articles()
    texts = [fetch_text(a["link"]) for a in articles]
    summaries = [summarize(t) for t in texts]
    vocabs = [vocab(t) for t in texts]
    quotes_list = [quotes(t) for t in texts]

    results = []
    for i, article in enumerate(articles):
        results.append({
            "title": article["title"],
            "link": article["link"],
            "summary": summaries[i],
            "vocabulary": vocabs[i],
            "quotes": quotes_list[i]
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
