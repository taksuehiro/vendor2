# AWS EC2 デプロイ設定

このディレクトリには、ベンダー検索RAGアプリケーションをAWS EC2にデプロイするための設定ファイルと手順書が含まれています。

## 📁 ファイル構成

### デプロイ関連ファイル
- `deploy.sh` - EC2インスタンスでの自動デプロイスクリプト
- `cloudformation-template.yaml` - CloudFormationテンプレート（自動化用）
- `aws-setup.md` - 詳細なAWS設定ガイド
- `aws-console-steps.md` - AWSコンソールでの手動設定手順

### 既存ファイル
- `vendor_rag_app/` - Streamlitアプリケーション
- `vendor_rag_ingest/` - データ取り込みスクリプト
- `vendor_rag_query/` - クエリ処理スクリプト
- `API.txt` - OpenAI APIキー

## 🚀 デプロイ方法

### 方法1: CloudFormation（推奨）
1. AWSコンソールでCloudFormationスタックを作成
2. `cloudformation-template.yaml`をアップロード
3. パラメータを設定（キーペア名など）
4. スタックを作成

### 方法2: 手動設定
1. `aws-console-steps.md`の手順に従ってEC2インスタンスを作成
2. Elastic IPを設定
3. セキュリティグループを設定
4. `deploy.sh`を実行

### 方法3: 自動化スクリプト
```bash
# EC2インスタンスに接続後
curl -O https://raw.githubusercontent.com/taksuehiro/vendor2/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

## 🔧 必要な設定

### セキュリティグループ
- **SSH (22)**: あなたのIPからのアクセスのみ
- **HTTP (80)**: すべてのIP
- **HTTPS (443)**: すべてのIP
- **Custom TCP (8501)**: Streamlitアプリ用

### Elastic IP
- 固定IPアドレスを割り当て
- EC2インスタンスに関連付け

### インスタンス仕様
- **タイプ**: t3.medium（推奨）
- **OS**: Amazon Linux 2023
- **ストレージ**: 20GB (gp3)
- **メモリ**: 4GB

## 📊 アプリケーション構成

### メインアプリケーション
- **フレームワーク**: Streamlit
- **ポート**: 8501
- **言語**: Python 3.8+

### 依存関係
```
streamlit==1.28.1
langchain>=0.1.0
langchain-community>=0.0.38
langchain-openai>=0.3.0
openai>=1.3.7
chromadb>=0.4.22
python-dotenv>=1.0.0
```

### 環境変数
```
OPENAI_API_KEY=sk-proj-zZgZjBlWYnlua91oh1nKT3BlbkFJ5qeKOfTIDe8Q6GIQzK23
```

## 🌐 アクセス方法

デプロイ完了後、以下のURLでアプリケーションにアクセスできます：

```
http://YOUR_ELASTIC_IP:8501
```

## 🔍 監視とメンテナンス

### サービス管理
```bash
# サービスステータス確認
sudo systemctl status vendor-rag-app

# サービス再起動
sudo systemctl restart vendor-rag-app

# ログ確認
sudo journalctl -u vendor-rag-app -f
```

### システム監視
```bash
# メモリ使用量
free -h

# ディスク使用量
df -h

# プロセス確認
ps aux | grep streamlit
```

## 🛠️ トラブルシューティング

### よくある問題

1. **アプリケーションが起動しない**
   - ログを確認: `sudo journalctl -u vendor-rag-app -f`
   - 依存関係を再インストール: `pip install -r requirements.txt`

2. **ポート8501にアクセスできない**
   - セキュリティグループの設定を確認
   - ファイアウォールの設定を確認: `sudo firewall-cmd --list-all`

3. **メモリ不足**
   - インスタンスタイプをアップグレード（t3.large以上）
   - 不要なプロセスを停止

### ログファイル
- システムログ: `/var/log/messages`
- アプリケーションログ: `sudo journalctl -u vendor-rag-app`
- Streamlitログ: `~/.streamlit/logs/`

## 💰 コスト最適化

### 推奨設定
- **開発環境**: t3.micro（月額約$8）
- **本番環境**: t3.medium（月額約$30）

### コスト削減方法
1. **スケジュール停止**: 夜間や週末に停止
2. **リザーブドインスタンス**: 長期利用で割引
3. **Spot インスタンス**: 開発環境で使用

## 🔒 セキュリティ

### 推奨設定
1. **SSHアクセス制限**: 特定のIPからのみアクセス許可
2. **セキュリティグループ**: 必要最小限のポートのみ開放
3. **定期的なアップデート**: `sudo yum update -y --security`
4. **SSL証明書**: Let's EncryptでHTTPS化

### セキュリティチェックリスト
- [ ] SSHキーペアの安全な保管
- [ ] セキュリティグループの適切な設定
- [ ] 定期的なセキュリティアップデート
- [ ] ログの監視設定
- [ ] バックアップの設定

## 📞 サポート

問題が発生した場合は、以下の手順で対処してください：

1. ログファイルを確認
2. トラブルシューティングガイドを参照
3. 必要に応じてインスタンスを再起動
4. 設定ファイルの見直し

## 📝 更新履歴

- **2024-01-XX**: 初回作成
- デプロイスクリプトの追加
- CloudFormationテンプレートの追加
- 詳細な設定ガイドの追加


