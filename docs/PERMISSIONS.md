# Agent SDK 実行許可設定ガイド

## 概要

Bot v3.0 では、Agent SDK の `permission_mode` でツール実行の許可方式を制御できます。

現在の設定: **`bypassPermissions`** (全自動許可)

## 許可モード一覧

### 1. bypassPermissions (全自動許可) ⚡

**現在の設定**

```python
ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    # ...
)
```

**特徴:**
- ✅ すべてのツール実行を自動許可
- ✅ 最も高速
- ⚠️ セキュリティリスクあり
- ⚠️ ユーザーへの確認なし

**適用場面:**
- 開発・テスト環境
- 信頼できるユーザーのみのプライベートサーバー
- ワークスペースが隔離されている環境

---

### 2. acceptEdits (編集のみ自動) 🛡️

**推奨: 本番環境**

```python
ClaudeAgentOptions(
    permission_mode="acceptEdits",
    # ...
)
```

**特徴:**
- ✅ ファイル読み書き（Read, Write, Edit）は自動許可
- ⚠️ コマンド実行（Bash）は確認が必要
- ⚡ バランスが良い

**適用場面:**
- 本番環境（一般ユーザー）
- セキュリティと利便性のバランス重視

**注意:** Discord Botでは確認UIの実装が必要

---

### 3. default / plan (全て確認) 🔒

```python
ClaudeAgentOptions(
    permission_mode="default",  # または "plan"
    # ...
)
```

**特徴:**
- 🔒 すべての操作で確認を要求
- ✅ 最も安全
- ⚠️ 対話的な確認UIが必要
- ⚠️ Discord Botでは実装が複雑

**適用場面:**
- 極めて慎重な運用が必要な環境
- 監査が必要な環境

---

### 4. カスタムフック (独自ロジック) 🎯

**最も柔軟**

```python
async def custom_permission_check(
    tool_name: str,
    tool_input: dict,
    context
) -> PermissionResult:
    """
    カスタム許可ロジック
    
    例: 特定のコマンドのみ許可
    """
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        
        # 許可するコマンド
        if command.startswith(("ls", "cat", "grep")):
            return {"allowed": True}
        
        # 危険なコマンド
        if "rm" in command or "dd" in command:
            return {
                "allowed": False,
                "reason": "危険なコマンドは実行できません"
            }
        
        # その他は確認が必要
        return {"allowed": False, "reason": "このコマンドは許可されていません"}
    
    # ファイル操作は許可
    if tool_name in ["Read", "Write", "Edit"]:
        return {"allowed": True}
    
    return {"allowed": True}

# 使用
ClaudeAgentOptions(
    can_use_tool=custom_permission_check,
    # ...
)
```

**特徴:**
- ✅ 完全にカスタマイズ可能
- ✅ 複雑なロジックを実装可能
- ⚠️ 実装が必要

**適用場面:**
- 特定のコマンドのみ許可したい
- ユーザーごとに権限を変えたい
- Discord Reactionsで承認/却下を実装したい

---

## 実装例: Discord Botでの段階的許可

### パターン1: ユーザーロールで許可を変更

```python
async def handle_new_conversation(self, message: discord.Message):
    # ユーザーのロールを確認
    is_admin = any(role.name == "Admin" for role in message.author.roles)
    is_trusted = any(role.name == "Trusted" for role in message.author.roles)
    
    # 権限に応じてモードを変更
    if is_admin:
        permission_mode = "bypassPermissions"
    elif is_trusted:
        permission_mode = "acceptEdits"
    else:
        permission_mode = "default"
    
    # Agent SDK実行
    result = await self.run_agent_sdk(
        content,
        permission_mode=permission_mode
    )
```

### パターン2: Discord Reactionsで承認

```python
async def custom_discord_permission(
    tool_name: str,
    tool_input: dict,
    context
):
    """Discord Reactionsで承認を取得"""
    
    # 危険な操作のみ確認
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        
        # 確認が必要なコマンド
        if any(dangerous in command for dangerous in ["rm", "dd", "curl"]):
            # Discord メッセージで確認
            confirm_msg = await channel.send(
                f"⚠️ 以下のコマンドを実行しますか？\n"
                f"```bash\n{command}\n```\n"
                f"✅ = 許可 / ❌ = 拒否"
            )
            await confirm_msg.add_reaction("✅")
            await confirm_msg.add_reaction("❌")
            
            # ユーザーの反応を待つ
            def check(reaction, user):
                return (
                    user == original_user and
                    str(reaction.emoji) in ["✅", "❌"] and
                    reaction.message.id == confirm_msg.id
                )
            
            try:
                reaction, user = await bot.wait_for(
                    'reaction_add',
                    timeout=60.0,
                    check=check
                )
                
                if str(reaction.emoji) == "✅":
                    return {"allowed": True}
                else:
                    return {
                        "allowed": False,
                        "reason": "ユーザーが拒否しました"
                    }
            except asyncio.TimeoutError:
                return {
                    "allowed": False,
                    "reason": "タイムアウトしました"
                }
    
    # その他は自動許可
    return {"allowed": True}
```

---

## 現在の Bot v3.0 での設定変更方法

### src/discord_bot.py (289行目付近)

```python
async def run_agent_sdk(self, user_message: str) -> str:
    async for message in query(
        prompt=user_message,
        options=ClaudeAgentOptions(
            system_prompt=self.agent_config.system_prompt,
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
            cwd=str(self.agent_config.workspace),
            cli_path=str(self.claude_cli_path),
            
            # ここを変更 ↓
            permission_mode="bypassPermissions",  # ← 現在
            # permission_mode="acceptEdits",     # ← 推奨
            
            max_turns=15,
            env=self.env_vars,
        )
    ):
```

### config.yaml での設定（将来的な拡張）

```yaml
security:
  # 許可モード: bypassPermissions, acceptEdits, default
  permission_mode: acceptEdits
  
  # 許可するツール
  allowed_tools:
    - Read
    - Write
    - Edit
    - Bash
    - Glob
    - Grep
  
  # Bashコマンドのホワイトリスト
  bash_whitelist:
    - ls
    - cat
    - grep
    - find
    - python
    - git
```

---

## セキュリティのベストプラクティス

### 1. 環境ごとに設定を変える

- **開発**: `bypassPermissions`
- **ステージング**: `acceptEdits`
- **本番**: `acceptEdits` + カスタムフック

### 2. ワークスペースを隔離

```python
# エージェントごとに独立したワークスペース
workspace = agent_path / "workspace"

# さらにユーザーごとに分離
user_workspace = workspace / str(user_id)
```

### 3. 危険なコマンドをブロック

agent.yaml で allowed_commands を設定:

```yaml
allowed_commands:
  - ls
  - cat
  - grep
  - python
  # rm, dd などは含めない
```

### 4. ファイルサイズ制限

```python
# 1MB制限
max_file_size = 1024 * 1024
```

### 5. レート制限

```python
# 既に実装済み
RateLimiter(per_minute=10, per_hour=100)
```

---

## まとめ

| 設定 | セキュリティ | 利便性 | 推奨用途 |
|-----|------------|--------|---------|
| bypassPermissions | ⚠️ 低 | ⚡ 高 | 開発・テスト |
| acceptEdits | 🛡️ 中 | ⚡ 中 | **本番推奨** |
| default/plan | 🔒 高 | ⚠️ 低 | 厳格な環境 |
| カスタムフック | 🎯 カスタム | 🎯 カスタム | 柔軟性重視 |

**現在の設定**: bypassPermissions (全自動許可)  
**推奨変更**: acceptEdits (ファイル操作のみ自動)

設定を変更する場合は、`src/discord_bot.py` の 289行目を編集してください。
