# AWSコンソールでの手動設定手順

## 1. EC2インスタンスの作成

### ステップ1: インスタンスの起動
1. AWSコンソールにログイン
2. EC2サービスに移動
3. 「インスタンスを起動」をクリック

### ステップ2: 名前とタグ
- **名前**: `vendor-rag-instance`
- **タグ**:
  - Key: `Environment`, Value: `Production`
  - Key: `Application`, Value: `VendorRAG`

### ステップ3: アプリケーションとOSイメージ
- **Amazon Linux 2023** を選択
- **アーキテクチャ**: x86

### ステップ4: インスタンスタイプ
- **インスタンスタイプ**: `t3.medium`
- **vCPU**: 2
- **メモリ**: 4 GiB

### ステップ5: キーペア
- **キーペア**: 既存のキーペアを選択、または新規作成
- 新規作成の場合、`.pem`ファイルをダウンロードして安全な場所に保存

### ステップ6: ネットワーク設定
- **VPC**: デフォルトVPC
- **サブネット**: デフォルトサブネット
- **パブリックIP**: 有効
- **ファイアウォール（セキュリティグループ）**: 新しいセキュリティグループを作成

### ステップ7: セキュリティグループの設定
**セキュリティグループ名**: `vendor-rag-sg`
**説明**: ベンダー検索RAGアプリケーション用

**インバウンドルール**:
| タイプ | プロトコル | ポート範囲 | ソース | 説明 |
|--------|------------|------------|--------|------|
| SSH | TCP | 22 | あなたのIP | SSH接続用 |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTPアクセス用 |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPSアクセス用 |
| Custom TCP | TCP | 8501 | 0.0.0.0/0 | Streamlitアプリ用 |

**アウトバウンドルール**:
| タイプ | プロトコル | ポート範囲 | ソース | 説明 |
|--------|------------|------------|--------|------|
| All traffic | All | All | 0.0.0.0/0 | すべてのアウトバウンド通信 |

### ステップ8: ストレージ設定
- **ルートボリューム**: 20 GB (gp3)
- **暗号化**: 有効

### ステップ9: インスタンスの起動
- 「インスタンスを起動」をクリック
- インスタンスIDをメモ

## 2. Elastic IPの設定

### ステップ1: Elastic IPの割り当て
1. EC2コンソールで「Elastic IP」を選択
2. 「Elastic IPアドレスの割り当て」をクリック
3. 設定:
   - **ネットワーク境界グループ**: デフォルト
   - **パブリックIPv4アドレスプール**: AmazonのIPv4アドレスプール
4. 「割り当て」をクリック

### ステップ2: EC2インスタンスへの関連付け
1. 作成したElastic IPを選択
2. 「アクション」→「Elastic IPアドレスの関連付け」
3. **インスタンス**: 作成したEC2インスタンスを選択
4. 「関連付け」をクリック

## 3. セキュリティグループの詳細設定

### ステップ1: セキュリティグループの確認
1. EC2コンソールで「セキュリティグループ」を選択
2. `vendor-rag-sg`を選択

### ステップ2: インバウンドルールの追加
1. 「インバウンドルール」タブを選択
2. 「インバウンドルールを編集」をクリック
3. 以下のルールを追加:

**SSHルール**:
- タイプ: SSH
- プロトコル: TCP
- ポート範囲: 22
- ソース: あなたのIPアドレス（推奨）または 0.0.0.0/0

**HTTPルール**:
- タイプ: HTTP
- プロトコル: TCP
- ポート範囲: 80
- ソース: 0.0.0.0/0

**HTTPSルール**:
- タイプ: HTTPS
- プロトコル: TCP
- ポート範囲: 443
- ソース: 0.0.0.0/0

**Custom TCPルール**:
- タイプ: Custom TCP
- プロトコル: TCP
- ポート範囲: 8501
- ソース: 0.0.0.0/0
- 説明: Streamlitアプリケーション

4. 「ルールを保存」をクリック

## 4. インスタンスへの接続とデプロイ

### ステップ1: SSH接続
```bash
ssh -i your-key.pem ec2-user@YOUR_ELASTIC_IP
```

### ステップ2: デプロイスクリプトの実行
```bash
# スクリプトをダウンロード（GitHubから直接実行する場合）
curl -O https://raw.githubusercontent.com/taksuehiro/vendor2/main/deploy.sh

# 実行権限を付与
chmod +x deploy.sh

# デプロイスクリプトを実行
./deploy.sh
```

### ステップ3: デプロイの確認
```bash
# サービスステータスの確認
sudo systemctl status vendor-rag-app

# ログの確認
sudo journalctl -u vendor-rag-app -f

# ポートの確認
sudo netstat -tlnp | grep 8501
```

## 5. アプリケーションのテスト

### ステップ1: ブラウザでのアクセス
```
http://YOUR_ELASTIC_IP:8501
```

### ステップ2: アプリケーションの動作確認
1. ベンダー検索RAGアプリが表示されることを確認
2. サンプルクエリで検索テストを実行
3. 結果が正常に表示されることを確認

## 6. 追加設定（オプション）

### 6.1 ドメイン名の設定
1. Route 53コンソールに移動
2. ホストゾーンを作成
3. Aレコードを作成してElastic IPを指すように設定

### 6.2 SSL証明書の設定
```bash
# Certbotのインストール
sudo yum install -y certbot python3-certbot-nginx

# 証明書の取得
sudo certbot --nginx -d your-domain.com
```

### 6.3 Nginxの設定
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

## 7. 監視とメンテナンス

### 7.1 CloudWatchの設定
1. CloudWatchコンソールに移動
2. ロググループを作成: `/ec2/vendor-rag-app`
3. メトリクスアラームを設定

### 7.2 バックアップ設定
1. EC2コンソールでインスタンスを選択
2. 「アクション」→「イメージとテンプレート」→「イメージを作成」
3. 定期的なスナップショットの作成をスケジュール

### 7.3 セキュリティアップデート
```bash
# 定期的なセキュリティアップデート
sudo yum update -y --security
```

## 8. トラブルシューティング

### 8.1 よくある問題

**アプリケーションが起動しない**:
```bash
# ログを確認
sudo journalctl -u vendor-rag-app -f

# 手動で起動テスト
cd /home/ec2-user/vendor-rag-app/vendor_rag_app
source ../venv/bin/activate
streamlit run app.py
```

**ポート8501にアクセスできない**:
```bash
# ファイアウォールの確認
sudo firewall-cmd --list-all

# セキュリティグループの確認
# AWSコンソールでセキュリティグループの設定を確認
```

**メモリ不足**:
```bash
# メモリ使用量の確認
free -h

# プロセス確認
ps aux | grep streamlit
```

### 8.2 ログの確認方法
```bash
# システムログ
sudo journalctl -u vendor-rag-app -f

# Streamlitログ
tail -f /home/ec2-user/.streamlit/logs/streamlit.log

# システムログ
sudo tail -f /var/log/messages
```

## 9. コスト最適化

### 9.1 インスタンスタイプの最適化
- 使用量に応じてインスタンスタイプを調整
- CloudWatchメトリクスで使用状況を監視

### 9.2 スケジュール停止
- 開発環境では夜間停止を検討
- AWS Lambda + EventBridgeで自動停止/起動

### 9.3 リザーブドインスタンス
- 長期利用の場合はリザーブドインスタンスを検討
- 1年または3年のコミットメントで割引


