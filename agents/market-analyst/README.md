# Market Analyst Agent

**専門分野**: 株式投資・マーケット分析

---

## 概要

Market Analystは、地政学的背景、世界情勢、企業ニュースから**ファクトベース**で投資判断の材料を提供する専門エージェントです。

### 特徴

- 📰 **自動ニュース取得** - workspace/news/に最新ニュースが自動保存される
- 🌍 **多層分析** - 地政学 → マクロ経済 → 業界 → 企業の4層分析
- 📊 **データ駆動** - 推測ではなくデータに基づく分析
- 💾 **分析の蓄積** - 過去の分析をworkspace/analysis/に保存
- 🔍 **クロスリファレンス** - 複数ソースで事実確認

---

## Workspace構造

```
agents/market-analyst/workspace/
├── news/                    # 最新ニュース（自動更新）
│   ├── geopolitics/         # 地政学ニュース
│   ├── economics/           # 経済指標・中央銀行
│   ├── markets/             # 市場動向
│   └── companies/           # 企業ニュース
│
├── analysis/                # 保存された分析
│   ├── YYYY-MM-DD_topic.md  # 日付別分析
│   └── sectors/             # セクター別分析
│
└── data/                    # データファイル
    ├── financials/          # 財務データ
    ├── reports/             # レポート・PDF
    └── historical/          # 過去データ
```

---

## 使用方法

### 起動

```bash
# 環境変数設定
$env:PYTHONUNBUFFERED = "1"

# Market Analyst起動
uv run python run.py ./agents/market-analyst
```

### Discord上での使い方

#### 1. 個別銘柄分析

```
@ai-agent テスラ(TSLA)の投資判断を分析して
```

**エージェントの動作:**
1. workspace/news/companies/ で Tesla関連ニュースを確認
2. workspace/data/financials/ で財務データを確認
3. 地政学リスク（EV政策、中国市場など）を評価
4. 結論をworkspace/analysis/に保存

#### 2. セクター分析

```
@ai-agent 半導体セクターの現状を分析して。地政学リスクも含めて
```

**エージェントの動作:**
1. workspace/news/geopolitics/ で米中関係のニュースを確認
2. workspace/news/markets/ で半導体需要のニュースを確認
3. 複数企業（NVDA, TSM, INTC等）の動向を調査
4. セクター全体の分析を保存

#### 3. マクロ経済分析

```
@ai-agent 今週のFOMC結果が市場に与える影響を分析して
```

**エージェントの動作:**
1. workspace/news/economics/ でFOMC関連ニュースを確認
2. 金利変動の影響をセクター別に分析
3. リスク資産への影響を評価

#### 4. 過去の分析を参照

```
@ai-agent 先週のNVIDIA分析を見せて
```

**エージェントの動作:**
1. workspace/analysis/ から該当ファイルを検索
2. 現在の状況と比較
3. 変化点をハイライト

---

## 分析フレームワーク

### 4層分析アプローチ

```
Layer 1: 地政学 (Geopolitics)
├── 米中関係
├── 地域紛争
├── 貿易政策
└── 規制動向

Layer 2: マクロ経済 (Macroeconomics)
├── 金利・インフレ
├── GDP成長率
├── 雇用統計
└── 中央銀行政策

Layer 3: 業界分析 (Industry)
├── セクタートレンド
├── 競合環境
├── 技術革新
└── 需給バランス

Layer 4: 企業分析 (Company)
├── 財務健全性
├── 収益性
├── 競争優位性
└── 経営陣の質
```

### 分析出力フォーマット

```markdown
# [企業名/セクター] 投資分析

**日付**: YYYY-MM-DD
**分析者**: Market Analyst Agent

## エグゼクティブサマリー
- 結論: [買い/中立/売り] (信頼度: 70%)
- 主要根拠: ...

## 地政学リスク評価
- リスク1: ...
- リスク2: ...

## マクロ経済環境
- 金利動向: ...
- 景気サイクル: ...

## 業界動向
- セクター成長率: ...
- 競合状況: ...

## 企業ファンダメンタルズ
- 売上成長率: ...
- 利益率: ...
- ROE: ...

## 主要リスク
1. ...
2. ...

## 情報源
- [Source 1] workspace/news/...
- [Source 2] Web: https://...

## 免責事項
本分析は投資助言ではありません。投資判断は自己責任で行ってください。
```

---

## ニュース自動取得の設定

### 推奨ニュースソース

**地政学 (geopolitics/)**
- Reuters World News
- Bloomberg Politics
- Financial Times
- Nikkei Asia

**経済指標 (economics/)**
- Federal Reserve (FOMC)
- ECB, BOJ announcements
- BLS (雇用統計)
- BEA (GDP)

**市場動向 (markets/)**
- Bloomberg Markets
- CNBC
- MarketWatch
- Yahoo Finance

**企業ニュース (companies/)**
- SEC Filings (Edgar)
- Company Press Releases
- Earnings Reports
- Analyst Reports

### ニュース取得スクリプト（例）

```python
# news_fetcher.py (ユーザーが作成)
import os
from pathlib import Path

NEWS_DIR = Path("agents/market-analyst/workspace/news")

def fetch_news():
    """
    各カテゴリのニュースを取得してworkspace/news/に保存
    """
    # 地政学ニュース
    fetch_geopolitics()
    
    # 経済指標
    fetch_economics()
    
    # 市場動向
    fetch_markets()
    
    # 企業ニュース
    fetch_companies()

# Cron/タスクスケジューラで定期実行
# Windows: Task Scheduler
# Linux: crontab -e
# */30 * * * * python news_fetcher.py
```

---

## ベストプラクティス

### 1. 複数ソースの確認

```
@ai-agent NVIDIAの最新ニュースを3つのソースから確認して分析して
```

エージェントは自動的に:
- workspace/news/companies/nvidia_*.txt
- workspace/data/financials/NVDA_latest.json
- Web検索（必要に応じて）

### 2. 時系列での変化追跡

```
@ai-agent テスラの過去1ヶ月の分析履歴を見せて。トレンドは？
```

workspace/analysis/内の関連ファイルを検索して時系列比較

### 3. リスクシナリオ分析

```
@ai-agent 金利が1%上昇した場合、グロース株への影響を分析して
```

マクロ経済データとセクターパフォーマンスをクロス分析

### 4. セクターローテーション

```
@ai-agent 現在の経済サイクルでどのセクターが有望か分析して
```

地政学・マクロ経済・業界データを統合分析

---

## エージェントの強み

### ✅ できること

- **多層分析**: 地政学 → マクロ → 業界 → 企業の総合的視点
- **ローカルデータ活用**: 事前取得されたニュースで高速分析
- **分析の蓄積**: 過去の分析を参照して一貫性を保つ
- **ファクトチェック**: 複数ソースでクロスリファレンス
- **リスク評価**: 多角的なリスク分析
- **Web検索**: 必要に応じてリアルタイム情報を取得

### ⚠️ できないこと

- リアルタイムの株価取得（別途APIが必要）
- 個別の投資アドバイス（分析のみ）
- 感情的な市場予測（データベースのみ）
- 100%の確実性（常に不確実性を明示）

---

## セキュリティと免責事項

### ⚠️ 重要な注意事項

1. **投資助言ではない**: 本エージェントの分析は情報提供のみを目的としています
2. **自己責任**: 投資判断は必ずご自身の責任で行ってください
3. **データの正確性**: ニュースソースの信頼性を確認してください
4. **過去実績**: 過去のパフォーマンスは将来を保証しません
5. **リスク**: 投資には損失のリスクが伴います

### データプライバシー

- workspace/内のデータはローカルに保存されます
- センシティブな財務情報の取り扱いに注意してください
- 必要に応じて暗号化を検討してください

---

## カスタマイズ

### システムプロンプトの調整

`agent.yaml`を編集して分析スタイルをカスタマイズ:

```yaml
system_prompt: |
  # より保守的な分析を重視
  Always emphasize downside risks over upside potential.
  
  # または、特定セクターに特化
  Specialize in technology sector analysis with focus on AI/ML companies.
```

### 許可コマンドの追加

```yaml
allowed_commands:
  - curl        # API呼び出し
  - wget        # データダウンロード
  - jq          # JSON解析
  - csvkit      # CSV分析
  - python      # データ処理
```

---

## トラブルシューティング

### ニュースが見つからない

**症状**: "No news files found in workspace/news/"

**解決策**:
1. ニュース取得スクリプトが動作しているか確認
2. workspace/news/に.txtまたは.mdファイルがあるか確認
3. ファイルパーミッションを確認

### 分析が保存されない

**症状**: "Failed to save analysis"

**解決策**:
1. workspace/analysis/ディレクトリが存在するか確認
2. 書き込み権限があるか確認
3. ディスク容量を確認

### Web検索が動作しない

**症状**: "Web search failed"

**解決策**:
1. インターネット接続を確認
2. allowed_commandsに`curl`または`wget`があるか確認
3. Agent SDKの設定を確認

---

## 今後の拡張アイデア

### 1. データソース統合

```python
# workspace/data/api_config.yaml
apis:
  - name: Alpha Vantage
    endpoint: https://www.alphavantage.co/query
    key: YOUR_API_KEY
  
  - name: Yahoo Finance
    endpoint: https://query1.finance.yahoo.com/
```

### 2. 自動レポート生成

毎朝のマーケットサマリーを自動生成:

```bash
# daily_report.sh
python run.py ./agents/market-analyst --task "Generate daily market summary"
```

### 3. アラート機能

特定のキーワード検出時に通知:

```python
# keywords: ["Fed rate hike", "earnings miss", "geopolitical risk"]
# → Discord DM送信
```

### 4. ポートフォリオ分析

workspace/data/portfolio.jsonを読み込んで:
- リスク評価
- セクター配分の最適化
- リバランス提案

---

## リソース

### 推奨学習資料

- **地政学**: "Principles for Dealing with the Changing World Order" - Ray Dalio
- **マクロ経済**: Federal Reserve Economic Data (FRED)
- **企業分析**: "The Intelligent Investor" - Benjamin Graham
- **リスク管理**: "Thinking, Fast and Slow" - Daniel Kahneman

### 有用なデータソース

- **経済データ**: FRED, Trading Economics, OECD
- **企業データ**: SEC Edgar, Yahoo Finance, Morningstar
- **ニュース**: Reuters, Bloomberg, Financial Times
- **レポート**: McKinsey, BCG, Goldman Sachs Research

---

## フィードバック

Market Analystエージェントの改善アイデアがあれば、プロジェクトのIssueにお願いします！

**Happy Investing!** 📈
