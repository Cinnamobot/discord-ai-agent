# 権限設定の変更

**更新日**: 2025-01-15  
**理由**: WebSearch等のツールで毎回許可を求められるのを回避

---

## 変更内容

### permission_mode

```python
# Before
permission_mode="acceptEdits"  # ファイル操作のみ自動承認

# After
permission_mode="bypassPermissions"  # 全ツール自動承認
```

### allowed_tools

```python
# Before
allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]

# After
allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch"]
```

---

## 理由

### 問題
- WebSearchを使用する度に許可を求められる
- 対話が中断されてユーザー体験が悪い
- Discord Botでは承認UIが実装されていない

### 解決
- `bypassPermissions`で全ツールを自動承認
- `WebSearch`をallowed_toolsに追加
- スムーズな対話フローを実現

---

## セキュリティへの影響

### リスク評価

| 設定 | リスクレベル | 対策 |
|------|------------|------|
| bypassPermissions | 中 | ワークスペース隔離 ✅ |
| WebSearch自動承認 | 低 | 読み取り専用 ✅ |
| Bash自動承認 | 中 | allowed_commands制限 ✅ |

### 実装済みの対策

1. **ワークスペース隔離**
   - 各エージェントは独自のworkspace/内で動作
   - システムディレクトリへのアクセス不可

2. **コマンド制限**
   - agent.yamlの`allowed_commands`で制限
   - 危険なコマンド（rm -rf等）は許可しない

3. **レート制限**
   - 10リクエスト/分、100リクエスト/時
   - DoS攻撃を防止

4. **セッションTTL**
   - 30分で自動期限切れ
   - 不正利用のリスク低減

5. **ファイルサイズ制限**
   - 1MB上限
   - リソース枯渇を防止

---

## 使用可能なツール

### 自動承認されるツール

| ツール | 用途 | リスク |
|-------|------|--------|
| **Read** | ファイル読み込み | 低 |
| **Write** | ファイル書き込み | 低 |
| **Edit** | ファイル編集 | 低 |
| **Bash** | コマンド実行 | 中 |
| **Glob** | ファイル検索 | 低 |
| **Grep** | コンテンツ検索 | 低 |
| **WebSearch** 🆕 | Web検索 | 低 |

---

## 推奨設定（環境別）

### 開発環境（現在の設定）

```python
permission_mode="bypassPermissions"
allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch"]
```

**理由**: 開発効率を優先

### 本番環境（慎重な場合）

```python
permission_mode="acceptEdits"
allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "WebSearch"]
# Bashは除外
```

**理由**: セキュリティを優先

### エンタープライズ環境（最も慎重）

```python
permission_mode="default"  # 全て確認
allowed_tools=["Read", "Glob", "Grep", "WebSearch"]
# 書き込み操作は確認必須
```

**理由**: 監査・コンプライアンス要件

---

## WebSearchの動作

### 自動で行われること

```
ユーザー: @ai-agent 最新のPythonのニュースを調べて

↓

🔧 Tool Use: WebSearch
   └─ query: latest Python news 2025

✓ Tool Result: (3 articles found)
   [自動的に検索実行]

📨 Final Result:
   最新のPythonニュースをまとめます...
```

### 許可不要

- ✅ 検索クエリの実行
- ✅ 結果の取得
- ✅ 内容の分析

---

## 変更の影響

### ユーザー体験

**Before**:
```
ユーザー: @ai-agent 最新のニュースを調べて
Bot: WebSearchを実行しますか？ [承認待ち]
[ここで止まる]
```

**After**:
```
ユーザー: @ai-agent 最新のニュースを調べて

🔧 Tool Use: WebSearch
✓ Tool Result: [結果取得]

Bot: 最新のニュースをまとめました...
[スムーズに完了]
```

### パフォーマンス

- ⚡ 応答速度向上（承認待ち時間なし）
- 🔄 スムーズな対話フロー
- 📊 より多くのツール活用

---

## ロールバック方法

元の設定に戻す場合:

```python
# src/discord_bot.py line 391-392
permission_mode="acceptEdits"
allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
# WebSearchを削除
```

---

## まとめ

### 変更点

- ✅ `bypassPermissions`で全ツール自動承認
- ✅ `WebSearch`を許可リストに追加
- ✅ より快適なユーザー体験

### セキュリティ

- ✅ ワークスペース隔離で保護
- ✅ レート制限で悪用防止
- ✅ WebSearchは読み取り専用で安全

### 推奨

開発・個人使用では現在の設定（bypassPermissions）で問題ありません。
本番環境や複数ユーザーの場合は、環境に応じて調整してください。

---

**これでWebSearchもBashもスムーズに動作します！**🚀
