# Discord AI Agent Bot - Agent SDK統合計画

**作成日**: 2025-01-15  
**最終更新**: 2025-01-15 (v3.0実装完了)  
**目的**: Claude Agent SDKを統合し、コードベースを大幅に簡素化  
**現在のバージョン**: v3.0 (Agent SDK統合版) ✅  
**前バージョン**: v2.0 (独自実装)

---

## 📊 現状分析

### 現在の実装状況

| コンポーネント | 実装方式 | コード量 | 状態 |
|--------------|---------|---------|------|
| エージェントループ | 独自実装 | ~250行 | ✅ 動作中 |
| ツール実行 | 独自実装 (SecureBashTool, SecureFileTools) | ~400行 | ✅ 動作中 |
| セキュリティ | 独自ミドルウェア | ~300行 | ✅ 動作中 |
| セッション管理 | 独自実装 (DiscordSessionManager) | ~270行 | ✅ 動作中 |
| Discord統合 | discord.py | ~250行 | ✅ 動作中 |
| **合計** | - | **~1,470行** | - |

### Agent SDK統合後の見積もり

| コンポーネント | 実装方式 | コード量 | 削減率 |
|--------------|---------|---------|--------|
| エージェントループ | **Agent SDK** | **~0行** | **100%削減** |
| ツール実行 | **Agent SDK** | **~0行** | **100%削減** |
| セキュリティ | **Agent SDK + 最小限の独自実装** | **~50行** | **83%削減** |
| セッション管理 | 独自実装（Discord特有） | ~270行 | 維持 |
| Discord統合 | discord.py + Agent SDK呼び出し | ~150行 | 40%削減 |
| **合計** | - | **~470行** | **68%削減** |

---

## 🎯 統合の目標

### 主要目標

1. **コード量の大幅削減** - 1,470行 → 470行 (68%削減)
2. **保守性の向上** - エージェントロジックはAnthropicが管理
3. **先進機能へのアクセス** - Web検索、MCP、サブエージェント
4. **セキュリティの強化** - エンタープライズグレードのセキュリティ
5. **スケーラビリティ** - AWS Bedrock、Google Vertex AI対応

### 副次的目標

- テストの簡素化
- ドキュメントの整理
- CI/CD構築の簡易化

---

## 📅 実装フェーズ

### **Phase 1: 検証と準備** (2-3日)

#### タスク

- [x] Agent SDKの調査完了
- [ ] Agent SDKのインストール
  ```bash
  pip install claude-agent-sdk
  ```
- [ ] Claude Code CLIのインストール
  ```bash
  curl -fsSL https://claude.ai/install.sh | bash
  ```
- [ ] 基本動作確認
  ```python
  # test_agent_sdk.py
  import asyncio
  from claude_agent_sdk import query, ClaudeAgentOptions
  
  async def test():
      async for message in query(
          prompt="List files in current directory",
          options=ClaudeAgentOptions(allowed_tools=["Bash"])
      ):
          print(message)
  
  asyncio.run(test())
  ```
- [ ] プロトタイプ作成（単独動作確認）
- [ ] エージェント設定の互換性確認

**成果物:**
- `test_agent_sdk.py` - 動作確認スクリプト
- `prototype_bot.py` - Discord統合なしのプロトタイプ
- 検証レポート

---

### **Phase 2: コア統合** (3-5日)

#### タスク 2.1: Discord Bot Layer のリファクタリング

**対象ファイル:** `src/bot.py`

**変更内容:**
```python
# Before: 独自Agentクラス使用
from src.agent_factory import Agent, AgentError

self.agent = Agent(agent_path, config)
response = await self.agent.run(enhanced_content, history)

# After: Agent SDK使用
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt=enhanced_content,
    options=ClaudeAgentOptions(
        system_prompt=self.agent_config["system_prompt"],
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        working_dir=str(self.agent_path / "workspace"),
        permission_mode="bypassPermissions"
    )
):
    if hasattr(message, "result"):
        await self.send_response(message.result)
```

**チェックリスト:**
- [ ] `src/bot.py` のリファクタリング
- [ ] エージェント設定読み込みの統合
- [ ] メッセージ処理フローの調整
- [ ] エラーハンドリングの実装

#### タスク 2.2: エージェント設定の統合

**対象ファイル:** `src/config.py`, エージェント設定読み込み

**変更内容:**
- `agent.yaml` から `system_prompt`, `allowed_commands` を読み込み
- Agent SDKの `ClaudeAgentOptions` へマッピング

**チェックリスト:**
- [ ] エージェント設定読み込みロジックの簡素化
- [ ] `allowed_commands` → `allowed_tools` へのマッピング
- [ ] `working_dir` 設定の実装

#### タスク 2.3: セッション管理の統合

**対象ファイル:** `src/session_adapter.py`, `src/bot.py`

**Agent SDKのセッション機能との統合方針:**
- Discord特有のセッション管理（`bot_message_id`, TTL）は**維持**
- Agent SDKの会話履歴機能は**オプションで使用**

**チェックリスト:**
- [ ] Discord セッション ID と Agent SDK セッション ID のマッピング
- [ ] `resume` オプションの活用検討
- [ ] セッション期限切れ処理の統合

---

### **Phase 3: 不要コードの削除** (2-3日)

#### タスク 3.1: agent_factory.py の削除

**削除対象:**
- `src/agent_factory.py` (453行) - 全削除

**理由:**
- `Agent` クラス → Agent SDK の `query()` で代替
- `AgentManager` クラス → 不要（1エージェント/Bot方式）

#### タスク 3.2: security.py の整理

**削除対象:**
- `SecureBashTool` クラス - Agent SDK が提供
- `SecureFileTools` クラス - Agent SDK が提供

**維持対象:**
- `SecurityMiddleware` の一部 - Discord特有の検証に使用可能

**チェックリスト:**
- [ ] 不要なクラスの削除
- [ ] 残すべきセキュリティロジックの抽出
- [ ] Agent SDK のセキュリティ設定との統合

#### タスク 3.3: tool_hooks.py の削除

**削除対象:**
- `src/tool_hooks.py` - 全削除

**理由:**
- Agent SDK の Hooks システムで代替

**移行方針:**
```python
# Before: 独自フック
from src.tool_hooks import ToolExecutionHooks
hooks = ToolExecutionHooks()
hooks.set_channel(message.channel)

# After: Agent SDK Hooks
from claude_agent_sdk import HookMatcher

async def notify_discord(input_data, tool_use_id, context):
    await channel.send(f"🔧 Tool: {input_data.get('tool_name')}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher=".*", hooks=[notify_discord])]
    }
)
```

**チェックリスト:**
- [ ] Discord通知フックの Agent SDK への移行
- [ ] `tool_hooks.py` の削除

---

### **Phase 4: テストと品質保証** (3-5日)

#### タスク 4.1: 統合テストの作成

**新規作成:**
- `tests/test_agent_sdk_integration.py` - Agent SDK 統合テスト
- `tests/test_discord_bot.py` - Discord Bot のテスト

**テスト項目:**
- [ ] 基本的なメッセージ処理
- [ ] エージェント実行（ツール使用含む）
- [ ] セッション管理
- [ ] 添付ファイル処理
- [ ] エラーハンドリング
- [ ] レート制限

#### タスク 4.2: 既存テストの更新

**対象:**
- `tests/` 内の既存テスト（存在する場合）

**チェックリスト:**
- [ ] 不要なテストの削除
- [ ] Agent SDK 使用に合わせたテストの更新

#### タスク 4.3: エンドツーエンドテスト

**テストシナリオ:**
1. エージェント起動
2. Discord メッセージ送信
3. ツール実行（ファイル読み書き、コマンド実行）
4. セッション継続
5. エージェント終了

**チェックリスト:**
- [ ] E2E テストスクリプトの作成
- [ ] CI/CD パイプラインへの統合準備

---

### **Phase 5: ドキュメントとデプロイ** (2-3日)

#### タスク 5.1: ドキュメント更新

**対象ファイル:**
- `README.md` - Agent SDK 使用方法を反映
- `仕様書.md` - v3.0 として更新完了 ✅
- `TASKS.md` - Agent SDK 統合後のタスクに更新

**チェックリスト:**
- [ ] `README.md` の更新
- [ ] インストール手順の更新
- [ ] 使用例の追加

#### タスク 5.2: requirements.txt の更新

**現在:**
```txt
discord.py==2.3.2
anthropic==0.40.0
python-dotenv==1.0.0
pyyaml==6.0.1
aiohttp==3.9.1
```

**更新後:**
```txt
# Core Dependencies
discord.py>=2.6.4
claude-agent-sdk>=0.1.19
python-dotenv>=1.2.1
pyyaml>=6.0.3

# Note: claude-agent-sdk includes anthropic SDK internally
```

**チェックリスト:**
- [ ] `requirements.txt` の更新
- [ ] `pyproject.toml` の更新
- [ ] 依存関係の確認

#### タスク 5.3: デプロイメント準備

**対象:**
- `deployment/` ディレクトリ
- systemd サービスファイル
- Docker 設定（将来）

**チェックリスト:**
- [ ] systemd サービスファイルの更新
- [ ] デプロイメント手順書の作成
- [ ] 環境変数設定の確認

---

## 🔄 移行戦略

### オプション A: クリーンリライト（推奨）

**手順:**
1. 新しいブランチ作成 `feature/agent-sdk-integration`
2. `src/discord_bot.py` として新規実装
3. 並行して動作確認
4. 検証完了後、`src/bot.py` を置き換え

**メリット:**
- ✅ 既存実装を壊さない
- ✅ 段階的に移行可能
- ✅ ロールバックが容易

**デメリット:**
- ⚠️ 一時的にコードが重複

### オプション B: インプレース移行

**手順:**
1. `src/agent_factory.py` を Agent SDK 呼び出しに書き換え
2. 段階的に不要コードを削除

**メリット:**
- ✅ コードの重複なし

**デメリット:**
- ⚠️ 既存実装が壊れるリスク
- ⚠️ ロールバックが困難

**推奨**: **オプション A（クリーンリライト）**

---

## 📊 進捗トラッキング

### Phase 1: 検証と準備

- [x] Agent SDK 調査
- [ ] インストール
- [ ] 基本動作確認
- [ ] プロトタイプ作成
- [ ] 互換性確認

**進捗**: 20% (1/5 完了)

### Phase 2: コア統合

- [ ] Discord Bot Layer リファクタリング
- [ ] エージェント設定統合
- [ ] セッション管理統合

**進捗**: 0% (0/3 完了)

### Phase 3: 不要コードの削除

- [ ] agent_factory.py 削除
- [ ] security.py 整理
- [ ] tool_hooks.py 削除

**進捗**: 0% (0/3 完了)

### Phase 4: テストと品質保証

- [ ] 統合テスト作成
- [ ] 既存テスト更新
- [ ] E2E テスト

**進捗**: 0% (0/3 完了)

### Phase 5: ドキュメントとデプロイ

- [x] 仕様書更新 (v3.0)
- [ ] README.md 更新
- [ ] requirements.txt 更新
- [ ] デプロイメント準備

**進捗**: 25% (1/4 完了)

**全体進捗**: **8.3%** (2/24 タスク完了)

---

## ⚠️ リスクと対策

### リスク 1: Agent SDK の学習コスト

**影響度**: 中  
**対策**:
- 公式ドキュメント熟読
- サンプルコード実装
- プロトタイプで検証

### リスク 2: Discord 特有機能との統合問題

**影響度**: 中  
**対策**:
- セッション管理は独自実装を維持
- `bot_message_id` 追跡を継続
- 段階的に統合

### リスク 3: パフォーマンスの劣化

**影響度**: 低  
**対策**:
- ベンチマーク実施
- Agent SDK のオプション最適化
- 必要に応じてキャッシング実装

### リスク 4: Agent SDK のバグや制限

**影響度**: 低  
**対策**:
- 最新版を使用
- GitHubで issue 確認
- フォールバック実装を準備

---

## 📈 期待される効果

### コードベース

| 指標 | Before | After | 改善率 |
|-----|--------|-------|--------|
| 総コード行数 | ~1,470行 | ~470行 | **68%削減** |
| エージェント実装 | ~450行 | ~0行 | **100%削減** |
| ツール実装 | ~400行 | ~0行 | **100%削減** |
| テストコード | ~0行 | ~300行 | **+300行** |

### 機能

| 機能 | Before | After |
|-----|--------|-------|
| Web検索 | ❌ 未実装 | ✅ Agent SDK提供 |
| MCP統合 | ❌ 未実装 | ✅ Agent SDK提供 |
| サブエージェント | ❌ 未実装 | ✅ Agent SDK提供 |
| セキュリティ | 🟡 独自実装 | ✅ エンタープライズグレード |
| スケーラビリティ | 🟡 限定的 | ✅ AWS/GCP対応 |

### 保守性

- ✅ エージェントロジックのメンテナンス不要
- ✅ Anthropic公式サポート
- ✅ 自動アップデート
- ✅ バグ修正の迅速化

---

## 🎯 次のアクション

### 即座に実行

1. **Agent SDK インストール**
   ```bash
   pip install claude-agent-sdk
   curl -fsSL https://claude.ai/install.sh | bash
   ```

2. **プロトタイプ作成**
   ```bash
   # test_agent_sdk.py を作成
   python test_agent_sdk.py
   ```

3. **ブランチ作成**
   ```bash
   git checkout -b feature/agent-sdk-integration
   ```

### 今週中に完了

- [ ] Phase 1 全タスク完了
- [ ] Phase 2 の設計完了
- [ ] プロトタイプでの動作確認

### 今月中に完了

- [ ] Phase 2-3 完了（コア統合）
- [ ] Phase 4 完了（テスト）
- [ ] Phase 5 完了（ドキュメント）

---

## 📚 参考資料

### 公式ドキュメント

- [Claude Agent SDK Overview](https://docs.claude.com/en/docs/agent-sdk/overview)
- [Agent SDK Quickstart](https://docs.claude.com/en/docs/agent-sdk/quickstart)
- [Agent SDK Python API](https://docs.claude.com/en/docs/agent-sdk/python)
- [Claude Code Documentation](https://code.claude.com/docs/en/overview)

### GitHub リポジトリ

- [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- [claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos)
- [claude-code](https://github.com/anthropics/claude-code)

### 関連資料

- [Agent Skills Specification](https://github.com/anthropics/skills)
- [Model Context Protocol](https://github.com/modelcontextprotocol)

---

## 📝 変更履歴

| 日付 | バージョン | 変更内容 |
|-----|----------|---------|
| 2025-01-15 | 1.0 | 初版作成 - Agent SDK 統合計画策定 |

---

**次回更新予定**: Phase 1 完了時  
**担当**: Development Team  
**レビュー**: 週次
