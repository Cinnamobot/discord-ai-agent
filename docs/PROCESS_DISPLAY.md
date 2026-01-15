# Agent SDK プロセス表示機能

**Version**: 3.0.1  
**追加日**: 2025-01-15

---

## 概要

Discord AI Agent Bot v3.0では、Agent SDKの実行プロセス（推論、ツール使用、結果）をターミナルにリアルタイム表示する機能を実装しています。

これにより、以下を視覚的に確認できます：

- 🤖 Claudeの思考プロセス（推論）
- 🔧 使用するツール（Read, Write, Bash等）
- 📊 ツールの入力パラメータ
- ✓ ツールの実行結果
- 📨 最終的な応答

---

## 表示例

### 1. 基本的なフロー

```
================================================================================
🤖 Agent SDK 実行開始
📝 User Message: Hello! Can you help me?
================================================================================

💭 Claude Thinking:
   Hello! I'd be happy to help you. What can I assist you with today?

📨 Final Result:
   Hello! I'd be happy to help you. What can I assist you with today?

================================================================================
✅ Agent SDK 実行完了
📤 Response Length: 68 chars
================================================================================
```

### 2. ツール使用あり（ファイル読み込み）

```
================================================================================
🤖 Agent SDK 実行開始
📝 User Message: Read the config.yaml file
================================================================================

💭 Claude Thinking:
   I'll read the config.yaml file for you.

🔧 Tool Use: Read
   └─ filePath: C:\Users\szk27\work\discord-AI-agent\config.yaml

✓ Tool Result: (2341 chars, 85 lines)
   agent:
     name: "Discord AI Agent"
     version: "3.0.0"
     model: "claude-3-5-sonnet-20241022"
   ... (80 more lines)

💭 Claude Thinking:
   Here's the content of config.yaml: [analysis of the file]

📨 Final Result:
   I've read the config.yaml file. It contains the following configuration:
   - Agent name: Discord AI Agent
   - Version: 3.0.0
   ...

================================================================================
✅ Agent SDK 実行完了
📤 Response Length: 245 chars
================================================================================
```

### 3. 複数ツール使用（Bash + Read）

```
================================================================================
🤖 Agent SDK 実行開始
📝 User Message: List Python files and show me the main one
================================================================================

💭 Claude Thinking:
   I'll first list all Python files in the directory.

🔧 Tool Use: Bash
   └─ command: ls *.py
   └─ description: List Python files

✓ Tool Result:
   run.py
   test_agent_sdk_simple.py
   prototype_agent_loader.py

💭 Claude Thinking:
   Now I'll read the main bot file.

🔧 Tool Use: Read
   └─ filePath: C:\Users\szk27\work\discord-AI-agent\run.py

✓ Tool Result: (421 chars, 23 lines)
   """Discord AI Agent Bot v3.0 起動スクリプト"""
   import sys
   from pathlib import Path
   ...

📨 Final Result:
   I found 3 Python files. The main file is run.py which...

================================================================================
✅ Agent SDK 実行完了
📤 Response Length: 312 chars
================================================================================
```

---

## カラーコード一覧

表示には以下のカラーコードを使用しています：

| 要素 | カラー | 説明 |
|------|--------|------|
| ヘッダー/区切り線 | マゼンタ | セクション区切り |
| 実行開始/完了 | シアン/グリーン（太字） | 実行状態 |
| Claude Thinking | シアン | 推論プロセス |
| Tool Use | イエロー（太字） | ツール使用開始 |
| Tool Parameters | ブルー | ツールパラメータ |
| Tool Result | グリーン | ツール実行結果 |
| Final Result | グリーン | 最終応答 |
| Error | レッド | エラーメッセージ |

---

## 実装詳細

### カラーコード定義

`src/discord_bot.py` (40-48行目):

```python
class Colors:
    """ターミナル出力用カラーコード"""
    HEADER = '\033[95m'     # マゼンタ
    BLUE = '\033[94m'       # ブルー
    CYAN = '\033[96m'       # シアン
    GREEN = '\033[92m'      # グリーン
    YELLOW = '\033[93m'     # イエロー
    RED = '\033[91m'        # レッド
    ENDC = '\033[0m'        # リセット
    BOLD = '\033[1m'        # 太字
```

### メッセージ表示関数

`src/discord_bot.py` (374-433行目):

```python
def _log_agent_message(self, message) -> None:
    """Agent SDKのメッセージをターミナルに表示（カラー出力）"""
    
    # TextMessage - Claude の思考・推論
    if hasattr(message, "text") and hasattr(message, "type"):
        if message.type == "text":
            print(f"{Colors.CYAN}💭 Claude Thinking:{Colors.ENDC}")
            print(f"   {message.text[:200]}...")
    
    # ToolUseMessage - ツール使用開始
    if hasattr(message, "tool_name"):
        print(f"{Colors.YELLOW}🔧 Tool Use:{Colors.ENDC} {message.tool_name}")
        # パラメータ表示...
    
    # ToolResultMessage - ツール実行結果
    if hasattr(message, "tool_result"):
        print(f"{Colors.GREEN}✓ Tool Result:{Colors.ENDC}")
        # 結果表示...
    
    # ResultMessage - 最終応答
    if hasattr(message, "result"):
        print(f"{Colors.GREEN}📨 Final Result:{Colors.ENDC}")
        # 応答表示...
```

### メインループ

`src/discord_bot.py` (335-372行目):

```python
async def run_agent_sdk(self, user_message: str, sdk_session_id: Optional[str] = None):
    """Agent SDK を使用してエージェントを実行"""
    
    # 実行開始ヘッダー
    print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}🤖 Agent SDK 実行開始{Colors.ENDC}")
    print(f"{Colors.BLUE}📝 User Message:{Colors.ENDC} {user_message[:100]}...")
    print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")
    
    # Agent SDK実行
    async for message in query(...):
        self._log_agent_message(message)  # リアルタイム表示
    
    # 実行完了ヘッダー
    print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ Agent SDK 実行完了{Colors.ENDC}")
    print(f"{Colors.BLUE}📤 Response Length:{Colors.ENDC} {len(result_text)} chars")
    print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")
```

---

## 表示される情報

### 1. TextMessage (思考・推論)

**条件**: `message.type == "text"`

**表示内容**:
- Claudeの思考プロセス
- 次の行動の説明
- 推論の途中経過

**例**:
```
💭 Claude Thinking:
   I'll read the config.yaml file to check the current configuration.
```

### 2. ToolUseMessage (ツール使用)

**条件**: `hasattr(message, "tool_name")`

**表示内容**:
- ツール名（Read, Write, Edit, Bash, Glob, Grep）
- 入力パラメータ（filePath, command等）
- パラメータ値（長い場合は省略）

**例**:
```
🔧 Tool Use: Bash
   └─ command: ls -la
   └─ description: List all files with details
```

### 3. ToolResultMessage (実行結果)

**条件**: `hasattr(message, "tool_result")`

**表示内容**:
- ツールの実行結果
- 長い場合は先頭5行のみ + 行数表示
- 短い場合は全文表示

**例**:
```
✓ Tool Result: (2341 chars, 85 lines)
   total 24
   drwxr-xr-x 1 user user  4096 Jan 15 10:30 .
   drwxr-xr-x 1 user user  4096 Jan 15 10:29 ..
   -rw-r--r-- 1 user user  1234 Jan 15 10:30 config.yaml
   -rw-r--r-- 1 user user  5678 Jan 15 10:30 run.py
   ... (80 more lines)
```

### 4. ResultMessage (最終応答)

**条件**: `hasattr(message, "result")`

**表示内容**:
- Claudeの最終的な応答
- ユーザーに返されるメッセージ
- 200文字以上は省略表示

**例**:
```
📨 Final Result:
   I've read the config.yaml file. It contains the following configuration:
   - Agent name: Discord AI Agent
   - Version: 3.0.0
   - Model: claude-3-5-sonnet-20241022
   ...
```

### 5. ErrorMessage (エラー)

**条件**: `hasattr(message, "error")`

**表示内容**:
- エラーメッセージ
- エラーの詳細

**例**:
```
❌ Error: FileNotFoundError: config.yaml not found
```

---

## テスト方法

### 1. 単独テスト（Discord不使用）

```bash
uv run python test_process_display.py
```

このスクリプトは3つのテストケースを実行します：

1. 簡単な質問（ツール不使用）
2. ファイル操作（Read/Write）
3. Bashコマンド実行

### 2. Discord Botでのテスト

```bash
uv run python run.py
```

Discord上で以下のようなメッセージを送信：

```
@ai-agent Read the config.yaml file and tell me what agent is configured
```

ターミナルにプロセスが表示されます。

---

## カスタマイズ

### 表示の詳細度を変更

**より詳細に（デバッグモード）:**

```python
# src/discord_bot.py:35
logging.basicConfig(
    level=logging.DEBUG,  # DEBUGに変更
    # ...
)
```

**より簡潔に（本番モード）:**

```python
# src/discord_bot.py:35
logging.basicConfig(
    level=logging.WARNING,  # WARNINGに変更
    # ...
)
```

### 色を変更

```python
# src/discord_bot.py:40-48
class Colors:
    HEADER = '\033[96m'     # シアンに変更
    BLUE = '\033[95m'       # マゼンタに変更
    # ... 自由にカスタマイズ
```

### 表示フォーマットを変更

```python
# _log_agent_message() 内で自由に変更可能
def _log_agent_message(self, message):
    if hasattr(message, "tool_name"):
        # 例: 時刻を追加
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] 🔧 Tool Use: {message.tool_name}")
```

---

## デバッグモード

### メッセージタイプの詳細を確認

Agent SDKから受信したメッセージの型と属性を確認するには：

```python
# src/discord_bot.py:35
logging.basicConfig(
    level=logging.DEBUG,  # DEBUGに変更
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
```

**出力例:**
```
DEBUG - Message type: TextMessage, attrs: ['text', 'type', 'role']
DEBUG - Message type: ToolUseMessage, attrs: ['tool_name', 'tool_input', 'id']
DEBUG - Message type: ToolResultMessage, attrs: ['tool_result', 'tool_use_id']
DEBUG - Message type: ResultMessage, attrs: ['result', 'session_id']
```

これにより、予期しないメッセージや属性の問題をデバッグできます。

---

## トラブルシューティング

### "❌ Error: None" が表示される

**原因**: Agent SDKがerror属性を持つが値がNoneのメッセージを返している

**解決**: v3.0.1で修正済み。エラー値がNoneの場合は表示しません。

```python
# 修正後のコード
if hasattr(message, "error") and message.error is not None:
    print(f"❌ Error: {message.error}")
```

### 出力がリアルタイムで表示されない（重要！）

**原因**: Pythonの標準出力がバッファリングされている

**解決策**:

#### 方法1: 環境変数を設定（推奨）

```bash
# Windows (PowerShell)
$env:PYTHONUNBUFFERED = "1"
uv run python run.py

# Linux/Mac
PYTHONUNBUFFERED=1 uv run python run.py
```

#### 方法2: Pythonオプションを使用

```bash
uv run python -u run.py
```

#### 詳細

`REALTIME_DISPLAY.md` を参照してください。

---

### カラーが表示されない

**原因**: Windowsターミナルがカラーコードに対応していない

**解決策**:
1. Windows Terminal を使用
2. VS Code の統合ターミナルを使用
3. PowerShell 7+ を使用

```powershell
# PowerShellでカラー有効化
$PSStyle.OutputRendering = "ANSI"
```

### 表示が文字化けする

**原因**: 文字コードの問題

**解決策**:
```bash
# 環境変数を設定
set PYTHONIOENCODING=utf-8
```

### ログが多すぎる

**原因**: DEBUGレベルのログが有効

**解決策**:
```python
# src/discord_bot.py:35
logging.basicConfig(level=logging.INFO)  # または WARNING
```

### Agent SDKのメッセージが表示されない

**原因**: Agent SDKのバージョンが古い

**解決策**:
```bash
uv sync --reinstall
# または
pip install --upgrade claude-agent-sdk
```

---

## パフォーマンスへの影響

### 表示機能の影響

| 項目 | 影響度 | 詳細 |
|------|--------|------|
| 実行速度 | 無視できる程度 | print()は非常に高速 |
| メモリ使用量 | 無視できる程度 | 文字列のみ |
| ディスク I/O | なし | ターミナル出力のみ |

### ログレベルによる影響

| レベル | 表示量 | パフォーマンス | 推奨用途 |
|--------|--------|--------------|---------|
| DEBUG | 最大 | やや低下 | 開発・デバッグ |
| INFO | 中程度 | 影響小 | **推奨（デフォルト）** |
| WARNING | 最小 | 影響なし | 本番環境（安定時） |

---

## 今後の改善案

### 1. ファイルへのログ出力

```python
# 実装例
import logging
logging.basicConfig(
    filename="agent_process.log",
    level=logging.DEBUG,
)
```

### 2. Discord へのストリーミング表示

ツール使用をリアルタイムでDiscordにも表示：

```python
# 実装例
async with message.channel.typing():
    status_msg = await message.channel.send("🔧 Tool: Read...")
    # ...
    await status_msg.edit(content="✓ Tool complete")
```

### 3. Web UIでの可視化

WebSocketでブラウザにリアルタイム表示：

```python
# 将来的な実装
import websockets
await ws.send(json.dumps({
    "type": "tool_use",
    "tool": "Read",
    "params": {...}
}))
```

---

## まとめ

Discord AI Agent Bot v3.0のプロセス表示機能により、以下が可能になりました：

✅ Claudeの思考プロセスの可視化  
✅ ツール使用のリアルタイム監視  
✅ デバッグ効率の向上  
✅ ユーザー体験の向上（開発者向け）  
✅ 透明性の向上（監査用途）

この機能は開発・デバッグ時に特に有用で、Agent SDKの動作を理解するのに役立ちます。

---

**参考資料**:
- `src/discord_bot.py` - メイン実装
- `test_process_display.py` - テストスクリプト
- Agent SDK公式ドキュメント
