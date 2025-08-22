#!/bin/bash

# EC2デプロイスクリプト
# ベンダー検索RAGアプリケーション用

echo "🚀 ベンダー検索RAGアプリケーションのデプロイを開始します..."

# システムパッケージの更新
echo "📦 システムパッケージを更新中..."
sudo yum update -y

# Python3とpipのインストール
echo "🐍 Python3とpipをインストール中..."
sudo yum install -y python3 python3-pip

# Gitのインストール
echo "📚 Gitをインストール中..."
sudo yum install -y git

# プロジェクトディレクトリの作成
echo "📁 プロジェクトディレクトリを作成中..."
mkdir -p /home/ec2-user/vendor-rag-app
cd /home/ec2-user/vendor-rag-app

# GitHubリポジトリのクローン
echo "📥 GitHubリポジトリをクローン中..."
git clone https://github.com/taksuehiro/vendor2.git .

# Python仮想環境の作成
echo "🔧 Python仮想環境を作成中..."
python3 -m venv venv
source venv/bin/activate

# 依存関係のインストール
echo "📦 依存関係をインストール中..."
cd vendor_rag_app
pip install --upgrade pip
pip install -r requirements.txt

# 環境変数ファイルの作成
echo "🔐 環境変数ファイルを作成中..."
cat > .env << 'ENVEOF'
OPENAI_API_KEY=sk-proj-zZgZjBlWYnlua91oh1nKT3BlbkFJ5qeKOfTIDe8Q6GIQzK23
ENVEOF

# Streamlit設定ファイルの作成
echo "⚙️ Streamlit設定ファイルを作成中..."
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << 'STREAMLITEOF'
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
STREAMLITEOF

# systemdサービスファイルの作成
echo "🔄 systemdサービスファイルを作成中..."
sudo tee /etc/systemd/system/vendor-rag-app.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=Vendor RAG App
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/vendor-rag-app/vendor_rag_app
Environment=PATH=/home/ec2-user/vendor-rag-app/venv/bin
ExecStart=/home/ec2-user/vendor-rag-app/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# サービスの有効化と開始
echo "🚀 サービスを開始中..."
sudo systemctl daemon-reload
sudo systemctl enable vendor-rag-app
sudo systemctl start vendor-rag-app

# ファイアウォール設定
echo "🔥 ファイアウォールを設定中..."
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload

echo "✅ デプロイが完了しました！"
echo "🌐 アプリケーションは http://YOUR_ELASTIC_IP:8501 でアクセスできます"
echo "📊 サービスステータス確認: sudo systemctl status vendor-rag-app"
echo "📝 ログ確認: sudo journalctl -u vendor-rag-app -f"
