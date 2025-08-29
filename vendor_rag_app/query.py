#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ベンダー情報検索＆回答生成（RAG）モジュール
Streamlitアプリから呼び出し可能な関数を提供
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
# MMRRetrieverは使わずにvectorstore.as_retriever()を使用
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import re
import tiktoken

class VendorRetriever:
    """ベンダー情報検索クラス"""
    
    def __init__(self, vectordb_path: str = "vectordb", api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            vectordb_path: ベクトルDBのパス
            api_key: OpenAI APIキー
        """
        self.vectordb_path = vectordb_path
        self.api_key = api_key
        self.vectorstore = None
        self.retriever = None
        
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """ベクトルストアの初期化"""
        try:
            # ベクトルDBの存在確認
            if not os.path.exists(self.vectordb_path):
                raise FileNotFoundError(f"ベクトルDBが見つかりません: {self.vectordb_path}")
            
            # OpenAI Embeddingsの初期化
            embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=self.api_key
            )
            
            # Chromaベクトルストアの読み込み
            self.vectorstore = Chroma(
                persist_directory=self.vectordb_path,
                embedding_function=embeddings
            )
            
            # MMR Retrieverの初期化（vectorstore.as_retrieverを使用）
            # MMRRetrieverクラスは使わず、vectorstoreのas_retrieverメソッドを使用
            
        except Exception as e:
            raise Exception(f"ベクトルストアの初期化に失敗しました: {e}")
    
    def search(self, query: str, k: int = 5, use_mmr: bool = True) -> List[Document]:
        """
        検索実行（デフォルトでMMR使用）
        
        Args:
            query: 検索クエリ
            k: 取得するドキュメント数
            use_mmr: MMR検索を使用するかどうか
            
        Returns:
            検索結果のドキュメントリスト
        """
        try:
            if not self.vectorstore:
                raise ValueError("ベクトルストアが初期化されていません")
            
            if use_mmr:
                # MMR検索を使用
                retriever = self.vectorstore.as_retriever(
                    search_type="mmr", 
                    search_kwargs={
                        "k": k,
                        "fetch_k": k * 2,  # より多くの候補を取得
                        "lambda_mult": 0.7  # 多様性の重み
                    }
                )
                results = retriever.get_relevant_documents(query)
            else:
                # 類似度検索を使用
                results = self.vectorstore.similarity_search(query, k=k)
            
            return results[:k]  # 必要な件数に制限
            
        except Exception as e:
            raise Exception(f"検索に失敗しました: {e}")
    
    def get_document_count(self) -> int:
        """ベクトルDB内のドキュメント数を取得"""
        try:
            if not self.vectorstore:
                return 0
            
            collection = self.vectorstore._collection
            return collection.count()
        except Exception:
            return 0

class VendorResponseFormatter:
    """ベンダー回答整形クラス"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        初期化
        
        Args:
            api_key: OpenAI APIキー
            model: 使用するモデル名
        """
        self.api_key = api_key
        self.model = model
        self.llm = None
        
        self._initialize_llm()
    
    def _initialize_llm(self):
        """LLMの初期化"""
        try:
            self.llm = ChatOpenAI(
                model=self.model,
                openai_api_key=self.api_key,
                temperature=0.1  # 低い温度で一貫性のある回答を生成
            )
        except Exception as e:
            raise Exception(f"LLMの初期化に失敗しました: {e}")
    
    def _extract_vendor_info(self, document: Document) -> dict:
        """
        ドキュメントからベンダー情報を抽出
        
        Args:
            document: ベンダー情報ドキュメント
            
        Returns:
            抽出されたベンダー情報の辞書
        """
        content = document.page_content
        
        # 正規表現でベンダー情報を抽出
        patterns = {
            'name': r'ベンダー \d+: (.+?) ｜',
            'vendor_id': r'ベンダーID: (.+?) ｜',
            'aliases': r'別名: (.+?) ｜',
            'interview_status': r'面談状況: (.+?) ｜',
            'category': r'カテゴリ: (.+?) ｜',
            'industry_tags': r'業界タグ: (.+?) ｜',
            'tech_stack': r'技術スタック: (.+?) ｜',
            'price_range': r'価格帯: (.+?) ｜',
            'deployment': r'デプロイ方式: (.+?) ｜',
            'strengths': r'強み: (.+?) ｜',
            'service_summary': r'サービス概要: (.+?) ｜',
            'description': r'詳細説明: (.+?) ｜',
            'url': r'URL: (.+?) ｜'
        }
        
        vendor_info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                vendor_info[key] = match.group(1).strip()
            else:
                vendor_info[key] = "情報なし"
        
        return vendor_info
    
    def _create_context_text(self, documents: List[Document]) -> str:
        """
        ドキュメントリストからコンテキストテキストを作成
        
        Args:
            documents: 検索結果のドキュメントリスト
            
        Returns:
            コンテキストテキスト
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            vendor_info = self._extract_vendor_info(doc)
            
            context_part = f"""
## ベンダー{i}
- **ベンダー名**: {vendor_info['name']}
- **ベンダーID**: {vendor_info['vendor_id']}
- **別名**: {vendor_info['aliases']}
- **面談状況**: {vendor_info['interview_status']}
- **カテゴリ**: {vendor_info['category']}
- **業界タグ**: {vendor_info['industry_tags']}
- **技術スタック**: {vendor_info['tech_stack']}
- **価格帯**: {vendor_info['price_range']}
- **デプロイ方式**: {vendor_info['deployment']}
- **強み**: {vendor_info['strengths']}
- **サービス概要**: {vendor_info['service_summary']}
- **詳細説明**: {vendor_info['description']}
- **URL**: {vendor_info['url']}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def format_response(self, question: str, documents: List[Document]) -> str:
        """
        質問とドキュメントから整形された回答を生成
        
        Args:
            question: ユーザーの質問
            documents: 検索結果のドキュメントリスト
            
        Returns:
            整形されたMarkdown形式の回答
        """
        if not documents:
            return self._create_no_results_response(question)
        
        # コンテキストテキストの作成
        context_text = self._create_context_text(documents)
        
        # プロンプトテンプレート
        system_prompt = """あなたはベンダー情報の専門アシスタントです。
提供されたベンダー情報のみを使用して、ユーザーの質問に回答してください。

重要なルール：
1. 提供されたベンダー情報からのみ回答を生成する
2. 情報にない内容は推測せず、「情報なし」と明記する
3. 各ベンダーの情報を整理して、見やすくMarkdown形式で出力する
4. 質問に関連するベンダーのみを回答に含める
5. ベンダー情報は正確に転記し、改変しない

回答形式：
```markdown
【質問】
{question}

【回答】
## ベンダー1
- **ベンダー名**: 
- **カテゴリ**: 
- **業界タグ**: 
- **サービス概要**: 
- **強み**: 
- **価格帯**: 
- **面談状況**: 

## ベンダー2
（同様に続く）
```"""

        human_prompt = f"""
質問: {question}

ベンダー情報:
{context_text}

上記のベンダー情報のみを使用して、質問に回答してください。
"""

        try:
            # LLMで回答生成
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # 回答の整形
            formatted_response = self._post_process_response(response.content)
            
            return formatted_response
            
        except Exception as e:
            return f"回答生成中にエラーが発生しました: {e}"
    
    def _create_no_results_response(self, question: str) -> str:
        """検索結果がない場合の回答"""
        return f"""【質問】
{question}

【回答】
申し訳ございませんが、ご質問に関連するベンダー情報が見つかりませんでした。

以下の点をご確認ください：
- キーワードを変更して再度お試しください
- より具体的な業界やカテゴリを指定してください
- 技術スタックやサービス内容で検索してみてください"""
    
    def _post_process_response(self, response: str) -> str:
        """
        回答の後処理
        
        Args:
            response: LLMからの回答
            
        Returns:
            後処理された回答
        """
        # 余分な改行を整理
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # マークダウンの整形
        response = response.strip()
        
        return response

def load_environment():
    """環境変数の読み込み"""
    load_dotenv()
    
    # OpenAI APIキーの確認
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # .envファイルがない場合は、API.txtから読み込み
        try:
            with open("../../API.txt", "r", encoding="utf-8") as f:
                api_key = f.read().strip()
        except FileNotFoundError:
            raise ValueError("OPENAI_API_KEYが設定されていません。.envファイルまたはAPI.txtを確認してください。")
    
    return api_key

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """テキストのトークン数を計算"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # フォールバック: 大まかな計算（1トークン ≈ 4文字）
        return len(text) // 4

def query_vendor_info(question: str, k: int = 5, use_mmr: bool = True, model: str = "gpt-3.5-turbo", vectordb_path: str = "vectordb") -> tuple[str, dict]:
    """
    ベンダー情報を検索して回答を生成する関数
    
    Args:
        question: 検索したい質問
        k: 検索するベンダー数
        use_mmr: MMR検索を使用するかどうか
        model: 使用するLLMモデル
        vectordb_path: ベクトルDBのパス
        
    Returns:
        整形されたMarkdown形式の回答
    """
    try:
        # 1. 環境変数の読み込み
        api_key = load_environment()
        
        # 2. ベクトルDBの読み込み
        retriever = VendorRetriever(
            vectordb_path=vectordb_path,
            api_key=api_key
        )
        
        # ベクトルDB内のドキュメント数を確認
        doc_count = retriever.get_document_count()
        if doc_count == 0:
            return "エラー: ベクトルDBにデータがありません。Step1を先に実行してください。", {}
        
        # 3. ベンダー情報の検索
        documents = retriever.search(
            query=question,
            k=k,
            use_mmr=use_mmr
        )
        
        if not documents:
            return "検索結果が見つかりませんでした。", {}
        
        # 4. LLMの初期化
        formatter = VendorResponseFormatter(
            api_key=api_key,
            model=model
        )
        
        # 5. 回答の生成
        response = formatter.format_response(question, documents)
        
        # 6. トークン数の計算
        # 質問のトークン数
        question_tokens = count_tokens(question, model)
        
        # 検索結果のトークン数
        context_text = ""
        for doc in documents:
            context_text += doc.page_content + "\n"
        context_tokens = count_tokens(context_text, model)
        
        # 回答のトークン数
        response_tokens = count_tokens(response, model)
        
        # 合計トークン数
        total_tokens = question_tokens + context_tokens + response_tokens
        
        # トークン数情報
        token_info = {
            "question_tokens": question_tokens,
            "context_tokens": context_tokens,
            "response_tokens": response_tokens,
            "total_tokens": total_tokens,
            "documents_retrieved": len(documents),
            "model_used": model
        }
        
        return response, token_info
        
    except Exception as e:
        return f"エラーが発生しました: {e}", {}
