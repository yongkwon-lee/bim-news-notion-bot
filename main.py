import feedparser
import openai
import requests
import os
from datetime import datetime

RSS_URL = "https://news.google.com/rss/search?q=BIM&hl=ko&gl=KR&ceid=KR:ko"
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DB_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def summarize(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "뉴스를 한국어로 세 줄 요약해줘."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

def save_to_notion(title, url, summary):
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": title}}]},
            "링크": {"url": url},
            "요약": {"rich_text": [{"text": {"content": summary}}]},
            "날짜": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)

feed = feedparser.parse(RSS_URL)
for entry in feed.entries[:3]:
    summary = summarize(entry.summary)
    save_to_notion(entry.title, entry.link, summary)
