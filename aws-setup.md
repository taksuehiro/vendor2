# AWS EC2 デプロイ設定ガイド

## 1. EC2インスタンスの作成

### 1.1 インスタンスタイプの選択
- **推奨**: t3.medium または t3.large
- **理由**: Streamlit + RAG処理には適度なメモリとCPUが必要

### 1.2 AMIの選択
- **Amazon Linux 2023** を選択
- 最新の安定版を使用

### 1.3 ストレージ設定
- **ルートボリューム**: 20GB (gp3)
- **追加ボリューム**: 必要に応じて50GB追加

## 2. セキュリティグループの設定

### 2.1 インバウンドルール
| タイプ | プロトコル | ポート範囲 | ソース | 説明 |
|--------|------------|------------|--------|------|
| SSH | TCP | 22 | あなたのIP | SSH接続用 |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTPアクセス用 |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPSアクセス用 |
| Custom TCP | TCP | 8501 | 0.0.0.0/0 | Streamlitアプリ用 |

### 2.2 アウトバウンドルール
| タイプ | プロトコル | ポート範囲 | ソース | 説明 |
|--------|------------|------------|--------|------|
| All traffic | All | All | 0.0.0.0/0 | すべてのアウトバウンド通信 |

## 3. Elastic IPの設定

### 3.1 Elastic IPの割り当て
1. AWSコンソールで「Elastic IP」を選択
2. 「Elastic IPアドレスの割り当て」をクリック
3. 以下の設定で作成：
   - **ネットワーク境界グループ**: デフォルト
   - **パブリックIPv4アドレスプール**: AmazonのIPv4アドレスプール

### 3.2 EC2インスタンスへの関連付け
1. 作成したElastic IPを選択
2. 「アクション」→「Elastic IPアドレスの関連付け」
3. インスタンスを選択して関連付け

## 4. キーペアの設定
- 既存のキーペアを使用するか、新しいキーペアを作成
- `.pem`ファイルを安全な場所に保存

## 5. デプロイ手順

### 5.1 EC2インスタンスへの接続
```bash
ssh -i your-key.pem ec2-user@YOUR_ELASTIC_IP
```

### 5.2 デプロイスクリプトの実行
```bash
# スクリプトに実行権限を付与
chmod +x deploy.sh

# デプロイスクリプトを実行
./deploy.sh
```

## 6. アプリケーションの確認

### 6.1 サービスステータスの確認
```bash
sudo systemctl status vendor-rag-app
```

### 6.2 ログの確認
```bash
sudo journalctl -u vendor-rag-app -f
```

### 6.3 アプリケーションへのアクセス
ブラウザで以下にアクセス：
```
http://YOUR_ELASTIC_IP:8501
```

## 7. 追加設定

### 7.1 ドメイン名の設定（オプション）
Route 53を使用してドメイン名を設定する場合：
1. Route 53でホストゾーンを作成
2. Aレコードを作成してElastic IPを指すように設定

### 7.2 SSL証明書の設定（推奨）
Let's Encryptを使用してSSL証明書を取得：
```bash
# Certbotのインストール
sudo yum install -y certbot python3-certbot-nginx

# 証明書の取得
sudo certbot --nginx -d your-domain.com
```

### 7.3 Nginxの設定（オプション）
リバースプロキシとしてNginxを設定：
```bash
# Nginxのインストール
sudo yum install -y nginx

# 設定ファイルの作成
sudo tee /etc/nginx/conf.d/vendor-rag-app.conf > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Nginxの開始
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 8. 監視とメンテナンス

### 8.1 CloudWatchの設定
- EC2インスタンスのメトリクス監視
- ログの監視設定

### 8.2 バックアップ設定
- 定期的なスナップショットの作成
- データベースのバックアップ

### 8.3 セキュリティアップデート
```bash
# 定期的なセキュリティアップデート
sudo yum update -y --security
```

## 9. トラブルシューティング

### 9.1 よくある問題と解決方法

#### アプリケーションが起動しない
```bash
# ログを確認
sudo journalctl -u vendor-rag-app -f

# 手動で起動テスト
cd /home/ec2-user/vendor-rag-app/vendor_rag_app
source ../venv/bin/activate
streamlit run app.py
```

#### ポート8501にアクセスできない
```bash
# ファイアウォールの確認
sudo firewall-cmd --list-all

# セキュリティグループの確認
# AWSコンソールでセキュリティグループの設定を確認
```

#### メモリ不足
```bash
# メモリ使用量の確認
free -h

# プロセス確認
ps aux | grep streamlit
```

## 10. コスト最適化

### 10.1 インスタンスタイプの最適化
- 使用量に応じてインスタンスタイプを調整
- 開発環境ではt3.micro、本番環境ではt3.medium以上

### 10.2 スケジュール停止
- 開発環境では夜間停止を検討
- AWS Lambda + EventBridgeで自動停止/起動

### 10.3 リザーブドインスタンス
- 長期利用の場合はリザーブドインスタンスを検討


