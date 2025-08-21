#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ベンダー情報のベクトルDB構築スクリプト
Markdown形式のベンダー情報をチャンク分割し、ChromaベクトルDBに保存する
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

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
            print("API.txtからAPIキーを読み込みました")
        except FileNotFoundError:
            raise ValueError("OPENAI_API_KEYが設定されていません。.envファイルまたはAPI.txtを確認してください。")
    
    return api_key

def read_markdown_file(file_path: str) -> str:
    """Markdownファイルの読み込み"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    except Exception as e:
        raise Exception(f"ファイル読み込みエラー: {e}")

def split_vendor_data(text: str) -> list[Document]:
    """ベンダー情報をMarkdownヘッダーで分割"""
    try:
        # 正規表現でベンダーセクションを分割
        import re
        vendor_sections = re.split(r'(?=### ベンダー \d+:)', text.strip())
        
        # 空のセクションを除外
        vendor_sections = [section.strip() for section in vendor_sections if section.strip()]
        
        # Documentオブジェクトに変換
        documents = []
        for i, section in enumerate(vendor_sections):
            if section.startswith('### ベンダー'):
                doc = Document(
                    page_content=section,
                    metadata={"vendor_index": i + 1}
                )
                documents.append(doc)
        
        print(f"分割されたベンダー数: {len(documents)}")
        return documents
    except Exception as e:
        raise Exception(f"テキスト分割エラー: {e}")

def initialize_vectorstore(persist_directory: str):
    """ベクトルストアの初期化（既存データの削除）"""
    if os.path.exists(persist_directory):
        print(f"既存のベクトルDBを削除中: {persist_directory}")
        shutil.rmtree(persist_directory)
    
    os.makedirs(persist_directory, exist_ok=True)
    print(f"ベクトルDBディレクトリを作成: {persist_directory}")

def create_vectorstore(documents: list[Document], persist_directory: str, embeddings):
    """ベクトルストアの作成と保存"""
    try:
        print("ベクトルDBにドキュメントを保存中...")
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        
        # 永続化
        vectorstore.persist()
        print(f"ベクトルDBの保存が完了しました: {persist_directory}")
        
        # 保存されたドキュメント数の確認
        collection = vectorstore._collection
        count = collection.count()
        print(f"保存されたドキュメント数: {count}")
        
        return vectorstore
        
    except Exception as e:
        raise Exception(f"ベクトルDB作成エラー: {e}")

def main():
    """メイン処理"""
    print("=== ベンダー情報ベクトルDB構築開始 ===")
    
    # 設定
    DATA_FILE = "../../ベンダー調査.md"
    VECTORDB_DIR = "vectordb"
    
    try:
        # 1. 環境変数の読み込み
        print("1. 環境変数の読み込み...")
        api_key = load_environment()
        
        # 2. Markdownファイルの読み込み
        print("2. Markdownファイルの読み込み...")
        text = read_markdown_file(DATA_FILE)
        print(f"読み込み完了: {len(text)} 文字")
        
        # 3. ベンダー情報の分割
        print("3. ベンダー情報の分割...")
        documents = split_vendor_data(text)
        
        # 4. ベクトルストアの初期化
        print("4. ベクトルストアの初期化...")
        initialize_vectorstore(VECTORDB_DIR)
        
        # 5. OpenAI Embeddingsの初期化
        print("5. OpenAI Embeddingsの初期化...")
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=api_key
        )
        
        # 6. ベクトルストアの作成と保存
        print("6. ベクトルストアの作成と保存...")
        vectorstore = create_vectorstore(documents, VECTORDB_DIR, embeddings)
        
        print("=== ベクトルDB構築完了 ===")
        print(f"保存先: {os.path.abspath(VECTORDB_DIR)}")
        
        # 7. 動作確認（サンプル検索）
        print("\n=== 動作確認 ===")
        test_query = "契約書管理"
        print(f"テスト検索クエリ: '{test_query}'")
        
        results = vectorstore.similarity_search(test_query, k=3)
        for i, doc in enumerate(results, 1):
            print(f"\n結果 {i}:")
            print(f"内容: {doc.page_content[:200]}...")
            if hasattr(doc, 'metadata') and doc.metadata:
                print(f"メタデータ: {doc.metadata}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
