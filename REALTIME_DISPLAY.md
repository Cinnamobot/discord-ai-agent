# リアルタイム表示のトラブルシューティング

## 問題: 出力がBotの起動後にまとめて表示される

### 原因

Pythonの標準出力がバッファリングされているため、`print()`の内容が即座に表示されません。

### 解決策

以下の3つの方法があります。

---

## 方法1: 環境変数を設定（推奨）

### Windows (PowerShell)

```powershell
$env:PYTHONUNBUFFERED = "1"
uv run python run.py
```

### Windows (cmd)

```cmd
set PYTHONUNBUFFERED=1
uv run python run.py
```

### Linux/Mac

```bash
export PYTHONUNBUFFERED=1
uv run python run.py
```

または、1行で実行：

```bash
PYTHONUNBUFFERED=1 uv run python run.py
```

---

## 方法2: Pythonオプションを使用

```bash
uv run python -u run.py
```

`-u` オプションは `PYTHONUNBUFFERED=1` と同じ効果があります。

---

## 方法3: uvコマンドのオプション（v3.0.1で実装済み）

v3.0.1では以下の対策を実装済みです：

### `run.py`

```python
import os
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout.reconfigure(line_buffering=True)
```

### `src/discord_bot.py`

```python
# 標準出力のバッファリングを無効化
sys.stdout.reconfigure(line_buffering=True)
```

### 全ての`print()`に`flush=True`を追加

```python
print(f"🔧 Tool Use: {message.tool_name}", flush=True)
```

これにより、通常の起動でもリアルタイム表示されるはずです：

```bash
uv run python run.py
```

---

## 確認方法

### テストスクリプトで確認

```bash
uv run python test_process_display.py
```

正常に動作している場合、以下のように**メッセージごとに**表示されます：

```
💭 Claude Thinking:
   I'll create a file...

🔧 Tool Use: Write
   └─ filePath: test.txt
   └─ content: Hello from Agent SDK

✓ Tool Result:
   File written successfully

📨 Final Result:
   I've created the file test.txt
```

もしバッファリングされている場合、全ての出力が最後にまとめて表示されます。

---

## さらなる対策

### PowerShellプロファイルに追加（Windows）

永続的に環境変数を設定：

```powershell
# PowerShellプロファイルを開く
notepad $PROFILE

# 以下を追加
$env:PYTHONUNBUFFERED = "1"
```

### .bashrcに追加（Linux/Mac）

```bash
echo 'export PYTHONUNBUFFERED=1' >> ~/.bashrc
source ~/.bashrc
```

### VS Code設定

VS Code統合ターミナルを使用している場合：

`.vscode/settings.json` に追加：

```json
{
  "terminal.integrated.env.windows": {
    "PYTHONUNBUFFERED": "1"
  },
  "terminal.integrated.env.linux": {
    "PYTHONUNBUFFERED": "1"
  },
  "terminal.integrated.env.osx": {
    "PYTHONUNBUFFERED": "1"
  }
}
```

---

## トラブルシューティング

### それでも表示されない場合

#### 1. Pythonのバージョンを確認

```bash
python --version
```

Python 3.7以上を推奨。

#### 2. 別のターミナルを試す

- Windows Terminal
- PowerShell 7+
- Git Bash
- VS Code統合ターミナル

#### 3. バッファサイズを確認

Windowsの場合、コンソールバッファサイズを増やす：

1. ターミナルのプロパティを開く
2. 「レイアウト」タブ
3. 「画面バッファーのサイズ」を増やす

#### 4. 直接Pythonを実行

```bash
python -u src/discord_bot.py ./agents/default
```

---

## デバッグ用コード

以下をスクリプトの先頭に追加して、バッファリングの状態を確認：

```python
import sys
print(f"stdout isatty: {sys.stdout.isatty()}")
print(f"stdout line_buffering: {getattr(sys.stdout, 'line_buffering', 'N/A')}")
print(f"PYTHONUNBUFFERED: {os.environ.get('PYTHONUNBUFFERED', 'not set')}")
sys.stdout.flush()
```

期待される出力：

```
stdout isatty: True
stdout line_buffering: True
PYTHONUNBUFFERED: 1
```

---

## まとめ

最も簡単な方法：

```bash
# Windows (PowerShell)
$env:PYTHONUNBUFFERED = "1"; uv run python run.py

# Linux/Mac
PYTHONUNBUFFERED=1 uv run python run.py
```

または

```bash
uv run python -u run.py
```

これでAgent SDKの実行プロセスがリアルタイムで表示されます！🎉
