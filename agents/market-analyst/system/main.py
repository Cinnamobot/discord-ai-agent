"""
Market Analyst News Server
GASからニュース記事を受信してワークスペースに保存するサーバー
"""

import uvicorn


def main():
    """サーバーを起動"""
    uvicorn.run(
        "news_server:app", host="0.0.0.0", port=8000, reload=False, log_level="info"
    )


if __name__ == "__main__":
    main()
