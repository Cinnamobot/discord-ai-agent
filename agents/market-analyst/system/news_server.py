from fastapi import FastAPI, Request
import json
import os
from datetime import datetime
import time

app = FastAPI()

# ベースパス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(BASE_DIR, "../workspace/news")

@app.post("/articles")
async def receive_articles(request: Request):
    articles = await request.json()
    
    # 日付ディレクトリ作成
    now = datetime.now()
    dir_path = f"{NEWS_DIR}/{now.year}/{now.month:02}/{now.day:02}"
    os.makedirs(dir_path, exist_ok=True)
    
    # index.json読み込み（あれば）
    index_path = f"{dir_path}/index.json"
    if os.path.exists(index_path):
        with open(index_path) as f:
            index = json.load(f)
    else:
        index = []
    
    # 記事を保存
    timestamp = int(time.time())
    for i, article in enumerate(articles):
        filename = f"{timestamp}-{i}.txt"
        
        # 本文保存
        with open(f"{dir_path}/{filename}", "w") as f:
            f.write(article["body"])
        
        # index追加
        index.append({
            "title": article["title"],
            "description": article["description"],
            "file": filename,
            "url": article["url"]
        })
    
    # index.json更新
    with open(index_path, "w") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    return {"status": "ok", "saved": len(articles)}
