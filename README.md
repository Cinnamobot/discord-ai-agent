# Discord AI Agent Bot

**Version**: 3.0.3  
**Status**: Production Ready

Discord上で動作する高機能AIエージェントボットです。**Claude Agent SDK**を使用して、8つの専門エージェントを実行できます。

---

## ✨ 特徴

- 🤖 **8つの専門エージェント** - 汎用から投資分析まで
- 🔄 **セッション継続** - 返信で会話を記憶
- 🛡️ **本番環境対応** - セキュリティ・レート制限・エラーハンドリング
- 📊 **リアルタイム表示** - エージェントの思考プロセスを可視化
- 📈 **Market Analyst** - ローカルニュース連携の本格投資分析

---

## 🚀 クイックスタート

### 1. インストール

```bash
# リポジトリをクローン
git clone https://github.com/cinnamobot/discord-ai-agent.git
cd discord-ai-agent

# 依存関係をインストール
uv sync
# または
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env` ファイルを作成:

```bash
cp .env.example .env
```

`.env` を編集:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic  # Z.AI使用時
```

### 3. 起動

```bash
# リアルタイム表示を有効化
$env:PYTHONUNBUFFERED = "1"  # Windows
export PYTHONUNBUFFERED=1    # Linux/Mac

# Default Agent起動
uv run python run.py
```

### 4. Discordで使用

```
@ai-agent こんにちは！何ができる？
```

**詳細**: `QUICKSTART_v3.md` を参照

---

## 🎭 エージェント一覧

| # | エージェント | 専門分野 | 用途 |
|---|-------------|---------|------|
| 1 | **Default** | 汎用 | 日常的な質問・タスク |
| 2 | **Minimal** | 実験用 | Agent SDK動作観察 |
| 3 | **Creative** | クリエイティブ | コンテンツ作成・アイデア出し |
| 4 | **Idea Digger** | アイデア発掘 | イノベーション探索 |
| 5 | **Brainstorm Partner** | 壁打ち | 思考の整理 |
| 6 | **Technical Expert** | 技術専門家 | システム設計・デバッグ |
| 7 | **Python Tutor** | Python学習 | コード学習サポート |
| 8 | **Market Analyst** ⭐ | 投資分析 | ファクトベース投資判断 |

**起動例**:
```bash
# アイデア発掘
uv run python run.py ./agents/idea-digger

# 投資分析（ニュース取得スクリプト設定後）
uv run python run.py ./agents/market-analyst
```

**詳細**: `AGENTS_SUMMARY.md` を参照

---

## 📚 ドキュメント

### スタートガイド
- **`QUICKSTART_v3.md`** - 5分で始める
- **`AGENTS_SUMMARY.md`** - 全エージェント総覧

### エージェント
- **`docs/AGENT_PROFILES.md`** - エージェントプロファイル詳細
- **`docs/SPECIALIZED_AGENTS.md`** - 専門エージェントガイド
- **`agents/market-analyst/README.md`** - Market Analyst完全ガイド

### 開発
- **`docs/PROCESS_DISPLAY.md`** - プロセス表示・デバッグ
- **`docs/PERMISSIONS.md`** - セキュリティ・権限管理
- **`REALTIME_DISPLAY.md`** - リアルタイム表示設定

### プロジェクト
- **`CHANGELOG_v3.md`** - 変更履歴
- **`PLANS.md`** - プロジェクト計画

---

## 🎯 主な機能

### 1. Agent SDK統合

- **68%コード削減** (1,470行 → 470行)
- エージェントループ自動化
- ツール実行の自律化
- セキュリティ内蔵

### 2. セッション継続

```
ユーザー: @ai-agent こんにちは
Bot: こんにちは！

ユーザー: @ai-agent さっきの会話覚えてる？（返信）
Bot: はい、先ほど挨拶をしていただきましたね！ ← 記憶している
```

### 3. リアルタイムプロセス表示

```
================================================================================
🤖 Agent SDK 実行開始
📝 User Message: ファイルを読んで
================================================================================

💭 Claude Thinking:
   I'll read the file for you.

🔧 Tool Use: Read
   └─ filePath: config.yaml

✓ Tool Result: (2341 chars, 85 lines)
   agent:
     name: "Discord AI Agent"
   ...

📨 Final Result:
   Here's the content...
```

### 4. Market Analyst（最も高度）

**ローカルニュースキャッシュシステム**:

```
ユーザーのニュース取得スクリプト（バックグラウンド）
    ↓
workspace/news/に自動保存
    ├── geopolitics/
    ├── economics/
    ├── markets/
    └── companies/
    ↓
Market Analyst Agentが分析
```

**4層分析フレームワーク**:
1. 地政学コンテキスト
2. マクロ経済トレンド
3. 業界分析
4. 企業ファンダメンタルズ

---

## 🛠️ 技術スタック

- **Python 3.11+**
- **Claude Agent SDK** - エージェント実行
- **discord.py** - Discord統合
- **Z.AI API** - Claude APIアクセス
- **asyncio** - 非同期処理

---

## 📁 プロジェクト構造

```
discord-AI-agent/
├── run.py                         # 🚀 起動スクリプト
├── src/
│   ├── discord_bot.py            # メインボット
│   ├── session_adapter.py        # セッション管理
│   ├── rate_limit.py             # レート制限
│   └── file_manager.py           # ファイル管理
├── agents/                        # 8つのエージェント
│   ├── default/
│   ├── minimal/
│   ├── creative/
│   ├── idea-digger/
│   ├── brainstorm-partner/
│   ├── technical/
│   ├── python-tutor/
│   └── market-analyst/
│       └── workspace/            # ニュース・分析保存
├── docs/                          # ドキュメント
└── test_*.py                      # テストスクリプト
```

---

## 🔐 セキュリティ

### 実装済み

- ✅ **Permission Mode**: `acceptEdits` (ファイル操作自動承認)
- ✅ **Workspace隔離**: エージェントごとに独立
- ✅ **レート制限**: 10リクエスト/分、100リクエスト/時
- ✅ **ファイルサイズ制限**: 1MB
- ✅ **セッションTTL**: 30分自動期限切れ
- ✅ **コマンド制限**: allowed_commandsで制限

### 推奨設定

本番環境では：
1. Discord Reactionsで承認UI実装
2. ユーザーごとのworkspace分離
3. 監査ログ追加
4. カスタム権限フック

**詳細**: `docs/PERMISSIONS.md`

---

## 🎓 学習パス

### Level 1: 基礎（初日）
1. Default Agentで基本操作
2. メンション・返信の使い方
3. プロセス表示の確認

### Level 2: 活用（1週間）
1. 用途別エージェントの選択
2. 複数エージェントの使い分け
3. カスタムエージェントの作成

### Level 3: 上級（1ヶ月）
1. Market Analystのセットアップ
2. ニュース取得スクリプト実装
3. ワークフロー自動化

---

## 🤝 貢献

Issue・PRを歓迎します！

### 貢献エリア

- 新しいエージェントプロファイル
- ニュース取得スクリプト（Market Analyst用）
- Discord Reactions承認UI
- テストカバレッジ
- ドキュメント改善

---

## 📊 統計

| 項目 | v2.0 | v3.0.3 | 変化 |
|------|------|--------|------|
| コア実装 | 1,470行 | 470行 | -68% |
| エージェント数 | 2個 | 8個 | +300% |
| ドキュメント | 5個 | 11個 | +120% |

---

## 📝 ライセンス

MIT License

---

## 🔗 リンク

- **ドキュメント**: `docs/`
- **エージェント**: `agents/`
- **変更履歴**: `CHANGELOG_v3.md`
- **クイックスタート**: `QUICKSTART_v3.md`

---

## ⚠️ 免責事項

**Market Analystについて**:
- 本エージェントの分析は情報提供のみを目的としています
- 投資助言ではありません
- 投資判断は必ずご自身の責任で行ってください
- 過去のパフォーマンスは将来を保証しません

---

**Version**: 3.0.3 | **Author**: Discord AI Agent Team | **License**: MIT
