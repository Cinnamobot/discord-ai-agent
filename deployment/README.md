# デプロイ手順

## systemdサービスのインストール

### 1. サービスファイルをコピー

```bash
sudo cp deployment/discord-ai-bot@.service /etc/systemd/system/
```

### 2. サービスを有効化して起動

```bash
# サービスのリロード
sudo systemctl daemon-reload

# サービスを有効化（自動起動設定）
sudo systemctl enable discord-ai-bot@default

# サービスを起動
sudo systemctl start discord-ai-bot@default

# ステータス確認
sudo systemctl status discord-ai-bot@default
```

### 3. ログの確認

```bash
# ログを表示
sudo journalctl -u discord-ai-bot@default -f

# 最近のログ
sudo journalctl -u discord-ai-bot@default -n 100
```

### 4. サービスの操作

```bash
# 停止
sudo systemctl stop discord-ai-bot@default

# 再起動
sudo systemctl restart discord-ai-bot@default

# 設定ファイルを再読み込み
sudo systemctl daemon-reload
sudo systemctl restart discord-ai-bot@default
```

## 複数エージェントの運用

複数のエージェントを別々のサービスとして起動する場合:

```bash
# 各エージェントのサービスを有効化・起動
sudo systemctl enable discord-ai-bot@python-tutor
sudo systemctl start discord-ai-bot@python-tutor

sudo systemctl enable discord-ai-bot@code-reviewer
sudo systemctl start discord-ai-bot@code-reviewer

# 全エージェントのステータスを確認
sudo systemctl status discord-ai-bot@*
```

## トラブルシューティング

### サービスが起動しない場合

1. ログを確認:
   ```bash
   sudo journalctl -u discord-ai-bot@default -n 50 --no-pager
   ```

2. 設定ファイルを確認:
   - `.env`ファイルが正しく設定されているか
   - `agents/`ディレクトリにエージェント設定があるか

3. パーミッションを確認:
   ```bash
   ls -la /opt/discord-ai-bot/
   ```

### ポートの競合

Discord Botは特定のポートを使用しませんが、他のサービスと競合する場合は：
```bash
sudo netstat -tulpn | grep python
```
