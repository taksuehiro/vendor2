# Vendor RAG Query

ベンダー情報検索＆回答生成（RAG）システムです。

## 概要

Step1で作成したベクトルDB（`vectordb/`）を使用して、ユーザーの質問に対し関連するベンダー情報を検索し、テンプレートに沿って回答を生成するCLIスクリプトです。

## ファイル構成

```
vendor_rag_query/
├── query.py                  # メインスクリプト（質問に対してRAGで回答）
├── requirements.txt          # 依存ライブラリ
├── README.md                # このファイル
├── utils/
│   ├── retriever.py         # ベクトルDBからチャンクを検索
│   └── formatter.py         # 回答テンプレートでLLMを使って整形
└── vectordb/                # Step1で作成済みのDBを再利用
```

## 前提条件

- Step1で作成されたChromaのベクトルDBが `./vectordb` に存在すること
- OpenAI APIキーが設定されていること（`.env` または `../API.txt`）

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

または、`../API.txt`にAPIキーを記載してください。

## 使用方法

### 基本的な使用方法

```bash
python query.py "契約書管理系のベンダーは？"
```

### オプション付きの使用方法

```bash
# 取得件数を指定
python query.py "製造業向けの画像認識AIベンダーは？" --k 3

# 類似度検索を使用（MMRを無効）
python query.py "医療系のベンダーを教えて" --no-mmr

# モデルを指定
python query.py "チャットボット系のベンダーは？" --model gpt-4

# ベクトルDBのパスを指定
python query.py "セキュリティ系のベンダーは？" --vectordb ../vendor_rag_ingest/vectordb
```

## コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `question` | 検索したい質問（必須） | - |
| `--k` | 検索するベンダー数 | 5 |
| `--no-mmr` | MMR検索を無効にして類似度検索を使用 | False |
| `--model` | 使用するLLMモデル | gpt-3.5-turbo |
| `--vectordb` | ベクトルDBのパス | vectordb |

## 出力形式

回答は以下のMarkdown形式で出力されます：

```markdown
【質問】
契約書管理系のベンダーは？

【回答】
## ベンダー1
- **ベンダー名**: Hubble
- **カテゴリ**: 契約書管理
- **業界タグ**: 法務,全業種
- **サービス概要**: 契約書管理クラウド＋AIレビュー支援
- **強み**: AIで契約台帳を自動化・期限通知
- **価格帯**: 低
- **面談状況**: 面談済

## ベンダー2
（同様に続く）
```

## 技術仕様

- **使用ライブラリ**: langchain, openai, chromadb, python-dotenv
- **使用モデル**: OpenAI Chat Model（gpt-3.5-turbo または gpt-4）
- **検索方法**: MMR（Maximum Marginal Relevance）または類似度検索
- **ベクトルDB**: Chroma

## 検索方法

### MMR検索（デフォルト）
- 関連性と多様性のバランスを取った検索
- 類似したベンダーが重複することを防ぐ
- `fetch_k=10, k=5, lambda_mult=0.7` の設定

### 類似度検索
- 純粋な類似度による検索
- `--no-mmr` オプションで使用

## 注意事項

- Step1でベクトルDBを構築してから使用してください
- OpenAI APIキーが必要です
- インターネット接続が必要です（OpenAI APIの呼び出しのため）
- LLMは提供されたベンダー情報のみを使用して回答を生成します

## エラーハンドリング

- ベクトルDBが見つからない場合：Step1の実行を促すメッセージを表示
- APIキーが設定されていない場合：設定方法を案内
- 検索結果が見つからない場合：適切なメッセージを表示

## 使用例

```bash
# 契約書管理系のベンダーを検索
python query.py "契約書管理系のベンダーは？"

# 製造業向けの画像認識AIベンダーを検索（3件）
python query.py "製造業向けの画像認識AIベンダーは？" --k 3

# 医療系のベンダーを検索（類似度検索）
python query.py "医療系のベンダーを教えて" --no-mmr

# GPT-4を使用してチャットボット系のベンダーを検索
python query.py "チャットボット系のベンダーは？" --model gpt-4
```







