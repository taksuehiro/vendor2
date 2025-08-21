# Vendor RAG Ingest

ベンダー情報をベクトルDBに保存するためのプロジェクトです。

## 概要

Markdown形式で保存されたベンダー情報（`data/vendor_catalog.md`）を、ベンダーごとにチャンク分割し、ChromaベクトルDBに埋め込んで保存する処理を提供します。

## ファイル構成

```
vendor_rag_ingest/
├── ingest.py                # チャンク分割＋埋め込み登録
├── requirements.txt         # 依存ライブラリ
├── README.md               # このファイル
├── data/
│   └── vendor_catalog.md   # 入力元のMarkdownファイル
└── vectordb/               # ChromaベクトルDBの保存先
```

## セットアップ

### 1. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、OpenAI APIキーを設定してください：

```
OPENAI_API_KEY=your_openai_api_key_here
```

## 使用方法

### ベクトルDBの構築

```bash
python ingest.py
```

このコマンドにより以下が実行されます：

1. `data/vendor_catalog.md` を読み込み
2. `### ベンダー N:` のような見出しで各ベンダー情報を分割（1ベンダー = 1チャンク）
3. 分割後、LangChain Document として構築し、Chromaに保存（persist_directory = ./vectordb）
4. すでに vectordb/ が存在する場合は上書き（初期化）
5. `.env` の `OPENAI_API_KEY` を読み込んで埋め込みを取得

## 技術仕様

- **使用ライブラリ**: langchain, chromadb, openai, python-dotenv
- **使用モデル**: OpenAIEmbeddings（`text-embedding-ada-002`）
- **ベクトルDB**: Chroma
- **チャンク分割**: MarkdownHeaderTextSplitter

## 出力

- `vectordb/` ディレクトリにChromaベクトルDBが保存されます
- 各ベンダー情報が個別のドキュメントとして保存され、ベクトル検索が可能になります

## 注意事項

- OpenAI APIキーが必要です
- 既存のvectordbディレクトリは上書きされます
- インターネット接続が必要です（OpenAI APIの呼び出しのため）

## 次のステップ

このベクトルDB（`./vectordb`）を読み込んで、RAG（Retrieval-Augmented Generation）システムで使用できます。


