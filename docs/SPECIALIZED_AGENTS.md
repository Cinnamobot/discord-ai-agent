# 専門エージェントガイド

**Version**: 3.0.3  
**Last Updated**: 2025-01-15

---

## 概要

Discord AI Agent Bot v3.0.3では、特定の用途に特化した専門エージェントを追加しました。
これらのエージェントは、それぞれ独自の専門性とワークフローを持っています。

---

## 🎯 専門エージェント一覧

### 1. Idea Digger（アイデア掘り出し専門家）

**専門分野**: イノベーション・アイデア発掘

**アプローチ**:
1. **深掘り質問** - 表面的な要求の裏にある本質的な問題を探る
2. **前提への挑戦** - "当たり前"を疑い、新しい視点を開く
3. **異質な概念の結合** - 一見無関係な分野から着想を得る
4. **類似ソリューションのリサーチ** - 既存の解決策から学ぶ
5. **複数案の提示** - トレードオフを明示した選択肢を提供

**典型的な対話例**:
```
User: 新しいアプリのアイデアが欲しい

Agent: まず、誰のどんな問題を解決したいですか？
       既存のアプリで不満に感じる点は？
       
User: 時間管理アプリが多すぎて選べない

Agent: なるほど。では「選ぶ」ことが問題なんですね。
       逆転の発想: アプリを選ばずに済む方法は？
       
       調べてみると、Decision Fatigueという研究があります...
       [Web検索でリサーチ]
       
       3つのアプローチを提案します:
       1. AIが自動選択 - [メリット・デメリット]
       2. 統合ダッシュボード - [メリット・デメリット]
       3. ミニマリストアプローチ - [メリット・デメリット]
```

**起動**:
```bash
uv run python run.py ./agents/idea-digger
```

---

### 2. Brainstorm Partner（壁打ち相手）

**専門分野**: 思考の整理・アイデアの精錬

**役割**:
1. **アクティブリスニング** - 言葉の裏にある意図を汲み取る
2. **反射的質問** - "つまり〜ということですか？"で理解を深める
3. **悪魔の代弁者** - "でもXXXの場合はどうなる？"と挑戦
4. **"Yes, and..." 思考** - アイデアを否定せず発展させる
5. **構造化支援** - 散らかった思考を整理

**特徴**:
- **判断しない** - アイデアの良し悪しを評価せず、探索を促進
- **高速対話** - 短いやり取りで思考を活性化
- **エネルギッシュ** - ポジティブで刺激的な対話

**典型的な対話例**:
```
User: AIを使ったビジネスを始めたい

Agent: いいですね！どんな問題を解決したいですか？

User: うーん、まだ決めてない

Agent: OK、考え方を変えましょう。
       あなたが日常で"面倒だな"と感じることは？

User: 毎日のメール整理が面倒

Agent: Yes! メール整理、他にも
       - 請求書の処理
       - 会議のスケジューリング
       - 報告書作成
       とか、似た"面倒"がありますよね？
       
       これらに共通するパターンは何だと思います？

User: 繰り返し作業？

Agent: まさに！そして、もし悪魔の代弁者になるなら...
       "既にメール自動整理ツールはあるのに、なぜ新しいのが必要？"
       
User: 既存ツールは設定が複雑すぎる

Agent: それだ！「複雑な設定なしで使える自動化」
       これが本当の価値ですね。
```

**起動**:
```bash
uv run python run.py ./agents/brainstorm-partner
```

---

### 3. Market Analyst（株式投資専門家）⭐

**専門分野**: ファクトベース投資分析

#### 🌟 最も高度な専門エージェント

Market Analystは、他のエージェントと一線を画す**本格的な専門システム**です。

**特徴**:

#### 1. 4層分析フレームワーク

```
┌─────────────────────────────────────┐
│  Layer 1: 地政学 (Geopolitics)      │
│  - 米中関係、地域紛争、貿易政策     │
│  - 規制動向、政権交代               │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Layer 2: マクロ経済 (Macro)        │
│  - 金利、インフレ、GDP              │
│  - 雇用統計、中央銀行政策           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Layer 3: 業界分析 (Industry)       │
│  - セクタートレンド、競合環境       │
│  - 技術革新、需給バランス           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  Layer 4: 企業分析 (Company)        │
│  - 財務健全性、収益性               │
│  - 競争優位性、経営陣の質           │
└─────────────────────────────────────┘
```

#### 2. ローカルニュースキャッシュ

**革新的な仕組み**:

```
あなたのニュース取得スクリプト (バックグラウンド)
    ↓ (30分ごとに自動実行)
workspace/news/
├── geopolitics/    ← 最新ニュース自動保存
├── economics/      ← 最新ニュース自動保存
├── markets/        ← 最新ニュース自動保存
└── companies/      ← 最新ニュース自動保存
    ↓ (エージェントが自動読み込み)
Market Analyst Agent
    ↓
包括的な投資分析
```

**利点**:
- ⚡ **高速** - ローカルファイルから即座に分析
- 📊 **包括的** - 複数カテゴリを横断して分析
- 🔄 **常に最新** - バックグラウンドで自動更新
- 💾 **履歴保持** - 過去のニュースも参照可能

#### 3. 分析の蓄積

```
workspace/analysis/
├── 2025-01-15_tesla-q4-analysis.md
├── 2025-01-14_semiconductor-sector.md
├── 2025-01-13_fed-impact-assessment.md
└── ...

エージェントは過去の分析を参照して:
- トレンドの変化を追跡
- 予測の精度を検証
- 一貫性のある判断を維持
```

#### 4. データ駆動の意思決定

**情報源の優先順位**:
1. **ローカルニュース** (workspace/news/) - 第一優先
2. **過去の分析** (workspace/analysis/) - 文脈理解
3. **ローカルデータ** (workspace/data/) - 財務データ
4. **Web検索** - 必要に応じてリアルタイム情報

**クロスリファレンス**:
```python
# エージェントの思考プロセス
1. ローカルニュースで "NVIDIA earnings" を検索
2. 複数記事から共通点を抽出
3. 過去のNVIDIA分析と比較
4. 財務データで裏付けを確認
5. Web検索で最新情報を補完
6. 統合的な結論を導出
```

---

## 📋 使用シナリオ別ガイド

### シナリオ1: 新製品のアイデア出し

**エージェント選択**: Idea Digger → Brainstorm Partner

```
1. Idea Digger でアイデア発掘
   @ai-agent スマートホーム市場で未開拓の領域を探して
   
   → リサーチと分析で候補を提示

2. Brainstorm Partner で精錬
   @ai-agent さっきのアイデアを壁打ちしたい
   
   → 対話で具体化と問題点の発見
```

### シナリオ2: 技術的な問題解決

**エージェント選択**: Technical Expert

```
@ai-agent (Technical Expert) 
データベースのパフォーマンス問題を診断して

→ システマティックに調査・分析・提案
```

### シナリオ3: 投資判断の支援

**エージェント選択**: Market Analyst

```
# 事前準備
1. ニュース取得スクリプトを設定
2. workspace/news/に最新ニュースが蓄積

# Discord上で分析依頼
@ai-agent (Market Analyst)
テスラ(TSLA)の投資判断を、地政学リスクも含めて分析して

→ エージェントの動作:
  1. workspace/news/companies/tesla_*.txt を読み込み
  2. workspace/news/geopolitics/ で EV政策をチェック
  3. workspace/news/economics/ で金利動向をチェック
  4. workspace/data/financials/TSLA_*.json で財務確認
  5. 過去分析と比較 (workspace/analysis/TSLA_*.md)
  6. 4層分析を統合
  7. 結論を workspace/analysis/ に保存
```

### シナリオ4: 複数エージェントの連携

```
1. Idea Digger で市場機会を発掘
   @ai-agent 次世代エネルギー分野の投資機会は？

2. Market Analyst で投資分析
   @ai-agent (切り替え) 太陽光発電セクターを分析して

3. Technical Expert で実装検討
   @ai-agent (切り替え) 太陽光発電管理システムのアーキテクチャ設計
```

---

## 🔧 Market Analyst の詳細セットアップ

### ステップ1: ディレクトリ構造の確認

```bash
agents/market-analyst/workspace/
├── news/
│   ├── geopolitics/
│   ├── economics/
│   ├── markets/
│   └── companies/
├── analysis/
└── data/
```

### ステップ2: ニュース取得スクリプトの作成

**あなたが作成**するスクリプトの例:

```python
# market_news_fetcher.py
import requests
from pathlib import Path
from datetime import datetime

NEWS_DIR = Path("agents/market-analyst/workspace/news")

def fetch_company_news(ticker, source_api):
    """企業ニュースを取得"""
    # APIから取得（例: NewsAPI, Alpha Vantage, etc.）
    news_data = requests.get(f"{source_api}/news?ticker={ticker}").json()
    
    for article in news_data['articles']:
        filename = f"{datetime.now():%Y-%m-%d_%H-%M}_{ticker}_{article['id']}.txt"
        filepath = NEWS_DIR / "companies" / filename
        
        content = f"""Title: {article['title']}
Source: {article['source']}
Date: {article['date']}
URL: {article['url']}
Tickers: {ticker}

---

{article['content']}

---

Key Points:
{article.get('summary', 'N/A')}
"""
        filepath.write_text(content, encoding='utf-8')

def fetch_economics_news():
    """経済ニュースを取得"""
    # FRB, BLS, BEA等の公式情報
    pass

def fetch_geopolitics_news():
    """地政学ニュースを取得"""
    # Reuters, Bloomberg等の国際ニュース
    pass

def main():
    # 監視銘柄リスト
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    
    for ticker in tickers:
        fetch_company_news(ticker, YOUR_API_URL)
    
    fetch_economics_news()
    fetch_geopolitics_news()

if __name__ == "__main__":
    main()
```

### ステップ3: 定期実行の設定

**Windows (Task Scheduler)**:
```
1. タスクスケジューラを開く
2. 「基本タスクの作成」
3. トリガー: 30分ごと
4. 操作: python market_news_fetcher.py
```

**Linux/Mac (cron)**:
```bash
# crontab -e
*/30 * * * * cd /path/to/project && python market_news_fetcher.py
```

### ステップ4: Market Analyst起動

```bash
$env:PYTHONUNBUFFERED = "1"
uv run python run.py ./agents/market-analyst
```

### ステップ5: 分析依頼

```
@ai-agent workspace/news/ の最新ニュースを確認して、
今週の市場概況をまとめて
```

---

## 💡 ベストプラクティス

### 1. エージェントの使い分け

| 目的 | 第一選択 | 代替 |
|------|---------|------|
| アイデアの種探し | Idea Digger | Creative |
| アイデアの精錬 | Brainstorm Partner | - |
| 投資判断 | Market Analyst | - |
| 技術調査 | Technical Expert | Default |
| Python学習 | Python Tutor | Default |
| 雑談・一般質問 | Default | Minimal |

### 2. Market Analyst の効果的な使い方

**❌ 避けるべき**:
```
@ai-agent テスラを買うべき？
```
→ 情報が不足、分析が浅い

**✅ 推奨**:
```
@ai-agent workspace/news/ の最新ニュースを基に、
テスラ(TSLA)の投資判断を以下の観点から分析して:
1. EVセクターの地政学リスク（中国市場、補助金政策）
2. マクロ経済環境（金利、景気サイクル）
3. 競合状況（伝統的OEM、新興EV企業）
4. 直近の財務パフォーマンス

分析結果はworkspace/analysis/に保存してください。
```
→ 包括的な4層分析が実行される

### 3. ニュースの質を高める

**推奨ソース**:
- **一次情報**: SEC filings, 企業IR, 政府統計
- **信頼性の高いメディア**: Reuters, Bloomberg, FT, WSJ
- **専門分析**: Goldman Sachs Research, McKinsey

**避けるべき**:
- ソーシャルメディアの噂
- 匿名掲示板の情報
- 裏付けのない予測

---

## 🔮 今後の拡張可能性

### Market Analyst の進化

1. **リアルタイムデータ統合**
```python
# API連携で株価・指標を自動取得
workspace/data/realtime/
├── prices/
├── indicators/
└── sentiment/
```

2. **機械学習モデルの統合**
```python
# 過去の分析から学習
- 予測精度の向上
- パターン認識
- リスク評価の自動化
```

3. **ポートフォリオ管理**
```python
# 保有銘柄の自動監視
workspace/portfolio.json
→ 毎日の評価
→ リバランス提案
→ アラート通知
```

4. **自動レポート生成**
```bash
# 毎朝のマーケットサマリー
cron: 0 8 * * * generate_daily_report.py
→ Discord自動投稿
```

---

## 📚 参考資料

### Market Analyst 関連

**書籍**:
- "The Intelligent Investor" - Benjamin Graham
- "Principles" - Ray Dalio
- "Market Wizards" - Jack Schwager

**データソース**:
- [FRED](https://fred.stlouisfed.org/) - 経済データ
- [SEC Edgar](https://www.sec.gov/edgar) - 企業開示
- [Trading Economics](https://tradingeconomics.com/) - グローバル指標

**ニュースAPI**:
- [NewsAPI](https://newsapi.org/)
- [Alpha Vantage](https://www.alphavantage.co/)
- [Finnhub](https://finnhub.io/)

### 一般

- `docs/AGENT_PROFILES.md` - 全エージェント概要
- `agents/market-analyst/README.md` - Market Analyst詳細
- `agents/market-analyst/workspace/news/README.md` - ニュース構造

---

## ❓ FAQ

**Q: 複数エージェントを同時に起動できる？**  
A: はい。別のターミナルまたは別のDiscord Botトークンで起動可能です。

**Q: Market Analystは実際の売買をする？**  
A: いいえ。分析のみを提供します。投資判断と実行は必ずご自身で行ってください。

**Q: ニュース取得スクリプトのサンプルは？**  
A: 基本テンプレートは`workspace/news/README.md`にあります。具体的なAPIは各自のAPI契約に依存します。

**Q: エージェントを自作できる？**  
A: はい。`docs/AGENT_PROFILES.md`の「カスタムプロファイルの作成」を参照してください。

---

**専門エージェントで、あなたの可能性を広げましょう！** 🚀
