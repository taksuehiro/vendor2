#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ベクトルDBからチャンクを検索するモジュール
"""

import os
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.retrievers import MMRRetriever

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
            
            # MMR Retrieverの初期化
            self.retriever = MMRRetriever(
                vectorstore=self.vectorstore,
                fetch_k=10,  # より多くの候補を取得
                k=5,         # 最終的に5件を返す
                lambda_mult=0.7  # 多様性の重み
            )
            
            print(f"ベクトルDBを読み込みました: {self.vectordb_path}")
            
        except Exception as e:
            raise Exception(f"ベクトルストアの初期化に失敗しました: {e}")
    
    def search_similarity(self, query: str, k: int = 5) -> List[Document]:
        """
        類似度検索
        
        Args:
            query: 検索クエリ
            k: 取得するドキュメント数
            
        Returns:
            検索結果のドキュメントリスト
        """
        try:
            if not self.vectorstore:
                raise ValueError("ベクトルストアが初期化されていません")
            
            results = self.vectorstore.similarity_search(query, k=k)
            print(f"類似度検索で {len(results)} 件のベンダー情報を取得しました")
            return results
            
        except Exception as e:
            raise Exception(f"類似度検索に失敗しました: {e}")
    
    def search_mmr(self, query: str, k: int = 5) -> List[Document]:
        """
        MMR（Maximum Marginal Relevance）検索
        
        Args:
            query: 検索クエリ
            k: 取得するドキュメント数
            
        Returns:
            検索結果のドキュメントリスト
        """
        try:
            if not self.retriever:
                raise ValueError("MMR Retrieverが初期化されていません")
            
            results = self.retriever.get_relevant_documents(query)
            print(f"MMR検索で {len(results)} 件のベンダー情報を取得しました")
            return results
            
        except Exception as e:
            raise Exception(f"MMR検索に失敗しました: {e}")
    
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
        if use_mmr:
            return self.search_mmr(query, k)
        else:
            return self.search_similarity(query, k)
    
    def get_document_count(self) -> int:
        """ベクトルDB内のドキュメント数を取得"""
        try:
            if not self.vectorstore:
                return 0
            
            collection = self.vectorstore._collection
            return collection.count()
        except Exception:
            return 0
