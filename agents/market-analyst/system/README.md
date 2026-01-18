# Market Analyst News Server

GASからニュース記事を受信し、Market Analystのワークスペースに保存するFastAPIサーバーです。

## 概要

- **受信エンドポイント**: `POST /articles`
- **保存場所**: `../workspace/news/YYYY/MM/DD/`
- **ファイル形式**: 
  - `{timestamp}-{index}.txt` - 記事本文
  - `index.json` - メタデータ（タイトル、説明、URL）

## セットアップ

### 1. 依存関係のインストール

```bash
cd agents/market-analyst/system
uv sync
# または
pip install -r pyproject.toml
```

### 2. サーバー起動

#### 開発環境
```bash
uv run uvicorn news_server:app --reload --port 8000
```

#### 本番環境（バックグラウンド実行）
```bash
# Linux/Mac
nohup uv run uvicorn news_server:app --host 0.0.0.0 --port 8000 &

# または start.sh を使用
chmod +x start.sh
./start.sh
```

#### Windows
```powershell
# PowerShell
Start-Process -NoNewWindow uvicorn -ArgumentList "news_server:app --host 0.0.0.0 --port 8000"
```

### 3. サーバー停止

```bash
# プロセスIDを確認
ps aux | grep uvicorn

# 停止
kill <PID>

# または stop.sh を使用
./stop.sh
```

## API仕様

### POST /articles

GASから記事データを受信します。

**リクエストボディ**:
```json
[
  {
    "title": "記事タイトル",
    "description": "記事の説明",
    "body": "記事本文（全文）",
    "url": "https://example.com/article"
  }
]
```

**レスポンス**:
```json
{
  "status": "ok",
  "saved": 3
}
```

## ディレクトリ構造

```
agents/market-analyst/
├── system/
│   ├── news_server.py    # FastAPIサーバー
│   ├── main.py           # エントリーポイント
│   ├── pyproject.toml    # 依存関係
│   ├── README.md         # このファイル
│   ├── start.sh          # 起動スクリプト（Linux/Mac）
│   └── stop.sh           # 停止スクリプト（Linux/Mac）
└── workspace/
    └── news/
        └── 2026/
            └── 01/
                └── 18/
                    ├── index.json
                    ├── 1737187200-0.txt
                    └── 1737187200-1.txt
```

## GAS連携

GASスクリプトから以下のようにPOSTリクエストを送信:

```javascript
function sendNewsToServer(articles) {
  const url = 'http://your-server:8000/articles';
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(articles)
  };
  
  const response = UrlFetchApp.fetch(url, options);
  Logger.log(response.getContentText());
}
```

## トラブルシューティング

### ポートが既に使用されている
```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# プロセスを終了
kill <PID>
```

### ニュースディレクトリが作成されない
- `../workspace/news/`が存在するか確認
- サーバーに書き込み権限があるか確認

### GASからの接続エラー
- ファイアウォール設定を確認
- サーバーが`0.0.0.0`でリッスンしているか確認
- GASのIPアドレスがアクセス許可されているか確認
