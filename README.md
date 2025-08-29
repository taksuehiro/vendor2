# ベンダー検索 RAG システム

AIベンダー情報を効率的に検索・分析するためのRAG（Retrieval-Augmented Generation）システムです。

## 📁 プロジェクト構成

```
ベクトルDB構築用/
├── vendor_rag_ingest/     # Step1: ベクトルDB構築
├── vendor_rag_query/      # Step2: RAG検索エンジン
├── vendor_rag_app/        # Step3: Streamlit Webアプリ
├── .gitignore            # Git除外設定
└── README.md             # このファイル
```

## 🚀 セットアップ

### 1. 環境準備

```bash
# 必要なPythonパッケージをインストール
cd vendor_rag_ingest
pip install -r requirements.txt

cd ../vendor_rag_query
pip install -r requirements.txt

cd ../vendor_rag_app
pip install -r requirements.txt
```

### 2. APIキー設定

**重要**: APIキーは絶対にGitにアップロードしないでください！

```bash
# 方法1: .envファイルを作成
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 方法2: API.txtファイルを作成
echo "your_api_key_here" > API.txt
```

### 3. ベクトルDB構築（Step1）

```bash
cd vendor_rag_ingest
python ingest.py
```

### 4. Streamlitアプリ起動（Step3）

```bash
cd vendor_rag_app
streamlit run app.py
```

## 🔧 使用方法

### Webアプリ（推奨）
1. `streamlit run app.py` でアプリを起動
2. ブラウザで `http://localhost:8501` にアクセス
3. 質問を入力して検索実行

### CLI使用
```bash
cd vendor_rag_query
python query.py "契約書管理系のベンダーは？"
```

## 📊 機能

- **MMR検索**: 関連性と多様性のバランスを取った検索
- **トークン追跡**: リアルタイムでトークン使用量を表示
- **柔軟な設定**: 検索件数、モデル選択、検索方法のカスタマイズ
- **美しいUI**: Streamlitによる直感的なインターフェース

## 🔒 セキュリティ

- APIキーは `.env` または `API.txt` で管理
- `.gitignore` で機密情報を除外
- ベクトルDBはローカルに保存

## 🛠️ 技術スタック

- **LangChain**: RAGパイプライン構築
- **Chroma**: ベクトルデータベース
- **OpenAI**: 埋め込みとLLM
- **Streamlit**: Webインターフェース
- **Python**: メイン言語

## 📝 検索例

- `契約書管理系のベンダーは？`
- `製造業向けの画像認識AIベンダーは？`
- `医療系のベンダーを教えて`
- `チャットボット系のベンダーは？`
- `セキュリティ系のベンダーは？`

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。





