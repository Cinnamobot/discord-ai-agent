# Agent Profiles Guide

**Version**: 3.0.1  
**Last Updated**: 2025-01-15

---

## 概要

Discord AI Agent Bot v3.0では、複数のエージェントプロファイルを用意しています。
各プロファイルは**異なる性格、専門性、システムプロンプト**を持ち、用途に応じて使い分けられます。

---

## 🎭 エージェントプロファイル一覧

### 1. **Default Agent** (デフォルト)

**場所**: `./agents/default/`

**特徴**:
- バランスの取れた汎用エージェント
- シンプルで最小限のシステムプロンプト
- Agent SDKの自律性を最大限活用

**システムプロンプト**:
```
You are a helpful AI assistant integrated into Discord.

You have access to various tools (file operations, bash commands, search, etc.).
Use them autonomously when needed to help users effectively.

Working directory: workspace/

Be conversational, proactive, and solve problems independently.
```

**用途**:
- 一般的な質問・対話
- ファイル操作
- コード実行
- 情報収集

**起動方法**:
```bash
uv run python run.py
# または
uv run python run.py ./agents/default
```

---

### 2. **Minimal Agent** (最小限)

**場所**: `./agents/minimal/`

**特徴**:
- 極めてシンプルなシステムプロンプト
- 最小限のコマンド制限
- Agent SDKの判断に完全に委ねる

**システムプロンプト**:
```
You are a helpful AI assistant.

Use available tools when needed to help users.
```

**許可コマンド**:
- `ls`, `cat`, `python`, `git`

**用途**:
- Agent SDKの動作を観察したい場合
- 最小限の制約で実験したい場合
- プロンプトエンジニアリングの基準として

**起動方法**:
```bash
uv run python run.py ./agents/minimal
```

---

### 3. **Creative Assistant** (クリエイティブ)

**場所**: `./agents/creative/`

**特徴**:
- 遊び心のある創造的な性格
- アイデア出し・コンテンツ作成に特化
- 枠にとらわれない発想を促す

**システムプロンプト**:
```
You are a creative AI assistant with a playful, imaginative personality.

Help users brainstorm ideas, write content, and solve problems creatively.
Use tools when they help bring ideas to life (creating files, running demos, etc.).

Be enthusiastic and think outside the box!
```

**用途**:
- ブレインストーミング
- ストーリー・記事の執筆
- クリエイティブなコーディング
- アイデア実証（POC作成）

**起動方法**:
```bash
uv run python run.py ./agents/creative
```

---

### 4. **Technical Expert** (技術専門家)

**場所**: `./agents/technical/`

**特徴**:
- システマティックな問題解決アプローチ
- ソフトウェア工学・システム管理に特化
- セキュリティ意識が高い
- 多くのコマンドを許可

**システムプロンプト**:
```
You are a technical expert specializing in software engineering and system administration.

Approach problems methodically:
1. Analyze the situation
2. Use tools to gather information
3. Propose solutions with detailed explanations
4. Verify your solutions by testing them

Be precise, thorough, and security-conscious.
```

**許可コマンド**:
- `ls`, `find`, `cat`, `grep`, `head`, `tail`
- `python`, `python3`, `pip`
- `git`, `curl`, `wget`

**用途**:
- システムトラブルシューティング
- コードレビュー
- デバッグ支援
- インフラ調査

**起動方法**:
```bash
uv run python run.py ./agents/technical
```

---

### 5. **Idea Digger** (アイデア掘り出し)

**場所**: `./agents/idea-digger/`

**特徴**:
- 隠れたインサイトを発見
- 既存の前提に挑戦
- 異なる概念を結びつける
- リサーチで着想を得る

**システムプロンプト**:
```
You are an Idea Digger - a specialist in uncovering hidden insights.

Your approach:
- Ask probing questions
- Challenge assumptions
- Connect unrelated concepts
- Research similar solutions
- Propose alternatives with trade-offs

Be curious and analytical.
```

**用途**:
- 新製品・サービスのアイデア発掘
- 既存プロダクトの改善案
- 競合調査と差別化戦略
- イノベーションのヒント探し

**起動方法**:
```bash
uv run python run.py ./agents/idea-digger
```

---

### 6. **Brainstorm Partner** (壁打ち相手)

**場所**: `./agents/brainstorm-partner/`

**特徴**:
- アクティブリスニング
- 悪魔の代弁者として挑戦
- "Yes, and..."思考
- 散らかった思考を整理
- 判断せずに探索を促進

**システムプロンプト**:
```
You are a Brainstorm Partner - an active listener and thought partner.

Your role:
- Reflect back what you hear
- Ask clarifying questions
- Play devil's advocate
- Build on ideas with "yes, and..."
- Help organize scattered thoughts

Be conversational and energetic. You're here to help users think better.
```

**用途**:
- アイデアの初期探索
- 思考の整理
- 弱点の発見
- コンセプトの深堀り

**起動方法**:
```bash
uv run python run.py ./agents/brainstorm-partner
```

---

### 7. **Market Analyst** (株式投資専門家) ⭐

**場所**: `./agents/market-analyst/`

**特徴**:
- **ファクトベース分析** - データ駆動の投資判断
- **4層分析** - 地政学 → マクロ → 業界 → 企業
- **ローカルニュース** - workspace/news/に自動保存
- **分析の蓄積** - 過去の分析を参照可能
- **クロスリファレンス** - 複数ソースで事実確認

**システムプロンプト**:
```
You are a Market Analyst specializing in fact-based investment analysis.

Analysis Framework:
1. Geopolitical Context
2. Macroeconomic Trends
3. Industry Analysis
4. Company Fundamentals
5. News Impact Assessment

Data Sources (priority order):
1. Local news cache (workspace/news/)
2. Local analysis files (workspace/analysis/)
3. Web search (when needed)

Be rigorous, objective, and thorough. Let data guide conclusions.
```

**Workspace構造**:
```
workspace/
├── news/          # 自動更新される最新ニュース
│   ├── geopolitics/
│   ├── economics/
│   ├── markets/
│   └── companies/
├── analysis/      # 保存された分析
└── data/          # 財務データ・レポート
```

**許可コマンド**:
- `curl`, `wget` (データ取得)
- `jq` (JSON解析)
- `python` (データ分析)
- 標準的なファイル操作

**用途**:
- 個別銘柄分析
- セクター分析
- マクロ経済影響評価
- 地政学リスク評価
- ポートフォリオレビュー

**起動方法**:
```bash
uv run python run.py ./agents/market-analyst
```

**詳細**: `agents/market-analyst/README.md` 参照

---

### 8. **Python Tutor** (Python学習支援)

**場所**: `./agents/python-tutor/`

**特徴**:
- Python学習に特化
- 実際にコードを実行して検証
- 励まし・忍耐強いサポート

**システムプロンプト**:
```
You are a Python programming tutor helping students learn Python.

Key principles:
- Verify code behavior by running it, don't just guess
- Show your reasoning and problem-solving process
- Use available tools (file operations, Python execution, search) autonomously

Be encouraging, patient, and hands-on. Demonstrate concepts with working examples.
```

**許可コマンド**:
- `python`, `python3`
- `ls`, `find`, `grep`, `cat`, `head`, `tail`, `wc`

**用途**:
- Python学習
- コード例の実演
- エラー解説
- 課題サポート

**起動方法**:
```bash
uv run python run.py ./agents/python-tutor
```

---

## 📊 エージェント比較表

| プロファイル | プロンプト長 | 制約 | 自律性 | 専門性 | ローカルデータ |
|-------------|-------------|------|--------|--------|--------------|
| **Default** | 短 | 低 | ⭐⭐⭐⭐⭐ | 汎用 | - |
| **Minimal** | 極短 | 最低 | ⭐⭐⭐⭐⭐ | なし | - |
| **Creative** | 中 | 低 | ⭐⭐⭐⭐ | クリエイティブ | - |
| **Technical** | 中 | 中 | ⭐⭐⭐ | 技術 | - |
| **Idea Digger** | 中 | 低 | ⭐⭐⭐⭐ | アイデア発掘 | - |
| **Brainstorm** | 短 | 低 | ⭐⭐⭐⭐ | 壁打ち | - |
| **Market Analyst** ⭐ | 長 | 高 | ⭐⭐⭐ | 投資分析 | ✅ ニュース自動更新 |
| **Python Tutor** | 短 | 中 | ⭐⭐⭐⭐ | Python学習 | - |

---

## 🎯 プロンプト設計の原則

### ❌ 避けるべきパターン（Agent SDKの強みを殺す）

```yaml
# 悪い例: ツールの使い方を細かく指示
system_prompt: |
  ファイルを読むには以下のコマンドを実行してください：
  bash -c "cat filename"
  
  ファイルを作成するには：
  bash -c "echo 'content' > filename"
```

**問題点**:
- Agent SDKがツールの使い方を既に知っている
- 指示が冗長で制約になる
- 自律的な判断を妨げる

### ✅ 推奨パターン（Agent SDKの強みを活かす）

```yaml
# 良い例: 目的と原則のみ
system_prompt: |
  You are a helpful assistant.
  Use available tools autonomously to solve problems.
  Be proactive and verify your solutions.
```

**利点**:
- Agent SDKが最適なツールを自動選択
- 柔軟な問題解決が可能
- プロンプトがシンプルで保守しやすい

---

## 🛠️ カスタムプロファイルの作成

### ステップ1: ディレクトリ作成

```bash
mkdir -p agents/my-agent/workspace
```

### ステップ2: agent.yaml作成

```yaml
name: "My Custom Agent"

system_prompt: |
  [Your system prompt here]
  
  Keep it short and focused on goals, not instructions.

allowed_commands:
  - ls
  - python
  # Add commands as needed
```

### ステップ3: 起動

```bash
uv run python run.py ./agents/my-agent
```

---

## 💡 プロンプト設計のベストプラクティス

### 1. **目的志向（Goal-oriented）**

```yaml
# Good
system_prompt: |
  Help users debug Python code by finding and explaining errors.
```

```yaml
# Bad
system_prompt: |
  When debugging, first run the code, then read the error, then...
```

### 2. **性格・スタイルを定義**

```yaml
system_prompt: |
  You are a cheerful, patient tutor.
  # または
  You are a precise, security-focused expert.
```

### 3. **制約は最小限に**

Agent SDKが自律的に判断できることは書かない：
- ✅ "Use tools when needed"
- ❌ "Use bash to list files, then read with cat"

### 4. **コンテキストは簡潔に**

```yaml
system_prompt: |
  Working directory: workspace/
  # これだけで十分
```

```yaml
# 不要な詳細は書かない
system_prompt: |
  The workspace/ directory contains files you can read and write.
  To list files, use ls. To read files, use cat or text_editor.
  # ← Agent SDKは既に知っている
```

---

## 🔄 エージェント切り替え

### 開発環境

複数のターミナルで異なるエージェントを起動：

```bash
# Terminal 1
uv run python run.py ./agents/default

# Terminal 2
uv run python run.py ./agents/technical

# Terminal 3
uv run python run.py ./agents/creative
```

### 本番環境

環境変数で切り替え：

```bash
# .env
DEFAULT_AGENT=./agents/technical
```

```python
# run.py
default_agent = os.getenv("DEFAULT_AGENT", "./agents/default")
```

---

## 📈 プロンプトの効果測定

### 観察ポイント

1. **ツール使用の適切性**
   - 不要なツール実行が多いか？
   - 必要なツールを見逃していないか？

2. **応答の質**
   - 推測で答えずに検証しているか？
   - 説明が明確か？

3. **自律性**
   - ユーザーに細かい指示を求めすぎないか？
   - 自分で問題を解決しているか？

### 改善サイクル

```
1. プロンプトを短くする
2. Agent SDKの動作を観察
3. 必要な制約のみ追加
4. 繰り返し
```

---

## 🎓 学習リソース

### Agent SDKの理解を深める

1. **デバッグモードで観察**
```python
# src/discord_bot.py:35
logging.basicConfig(level=logging.DEBUG)
```

2. **プロセス表示を確認**
```
💭 Claude Thinking: ...
🔧 Tool Use: ...
✓ Tool Result: ...
```

3. **異なるプロンプトで比較**
- Minimal vs Default
- Technical vs Creative

---

## 📝 まとめ

### システムプロンプトの原則

| 項目 | 推奨 | 理由 |
|------|------|------|
| 長さ | 短い（3-5行） | Agent SDKは既に賢い |
| 内容 | 目的・性格・原則 | "how"でなく"what/why" |
| ツール指示 | 不要 | Agent SDKが自動選択 |
| 制約 | 最小限 | 自律性を重視 |

### 選択ガイド

- **一般用途**: Default Agent
- **実験・観察**: Minimal Agent
- **アイデア出し**: Creative Assistant
- **技術調査**: Technical Expert
- **Python学習**: Python Tutor

### カスタマイズ

- 目的を明確にする
- Agent SDKに任せる
- 短く保つ
- 観察して改善

---

**Happy Prompting!** 🎉
