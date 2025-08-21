#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ベンダー情報検索＆回答生成（RAG）メインスクリプト
CLIで質問を受け取り、ベクトルDBから関連ベンダーを検索して回答を生成
"""

import sys
import argparse
import os
from dotenv import load_dotenv
from utils.retriever import VendorRetriever
from utils.formatter import VendorResponseFormatter

def load_environment():
    """環境変数の読み込み"""
    load_dotenv()
    
    # OpenAI APIキーの確認
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # .envファイルがない場合は、API.txtから読み込み
        try:
            with open("../API.txt", "r", encoding="utf-8") as f:
                api_key = f.read().strip()
            print("API.txtからAPIキーを読み込みました")
        except FileNotFoundError:
            raise ValueError("OPENAI_API_KEYが設定されていません。.envファイルまたはAPI.txtを確認してください。")
    
    return api_key

def setup_argument_parser():
    """コマンドライン引数の設定"""
    parser = argparse.ArgumentParser(
        description="ベンダー情報検索＆回答生成（RAG）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python query.py "契約書管理系のベンダーは？"
  python query.py "製造業向けの画像認識AIベンダーは？" --k 3
  python query.py "医療系のベンダーを教えて" --no-mmr
        """
    )
    
    parser.add_argument(
        "question",
        type=str,
        help="検索したい質問"
    )
    
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="検索するベンダー数（デフォルト: 5）"
    )
    
    parser.add_argument(
        "--no-mmr",
        action="store_true",
        help="MMR検索を無効にして類似度検索を使用"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        choices=["gpt-3.5-turbo", "gpt-4"],
        help="使用するLLMモデル（デフォルト: gpt-3.5-turbo）"
    )
    
    parser.add_argument(
        "--vectordb",
        type=str,
        default="vectordb",
        help="ベクトルDBのパス（デフォルト: vectordb）"
    )
    
    return parser

def main():
    """メイン処理"""
    # 引数解析
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        print("=== ベンダー情報検索＆回答生成開始 ===")
        
        # 1. 環境変数の読み込み
        print("1. 環境変数の読み込み...")
        api_key = load_environment()
        
        # 2. ベクトルDBの読み込み
        print("2. ベクトルDBの読み込み...")
        retriever = VendorRetriever(
            vectordb_path=args.vectordb,
            api_key=api_key
        )
        
        # ベクトルDB内のドキュメント数を確認
        doc_count = retriever.get_document_count()
        print(f"ベクトルDB内のベンダー数: {doc_count}")
        
        if doc_count == 0:
            print("エラー: ベクトルDBにデータがありません。Step1を先に実行してください。")
            return 1
        
        # 3. ベンダー情報の検索
        print("3. ベンダー情報の検索...")
        print(f"質問: {args.question}")
        print(f"検索方法: {'MMR' if not args.no_mmr else '類似度検索'}")
        print(f"取得件数: {args.k}")
        
        documents = retriever.search(
            query=args.question,
            k=args.k,
            use_mmr=not args.no_mmr
        )
        
        if not documents:
            print("検索結果が見つかりませんでした。")
            return 1
        
        # 4. LLMの初期化
        print("4. LLMの初期化...")
        formatter = VendorResponseFormatter(
            api_key=api_key,
            model=args.model
        )
        
        # 5. 回答の生成
        print("5. 回答の生成...")
        response = formatter.format_response(args.question, documents)
        
        # 6. 結果の出力
        print("\n" + "="*50)
        print(response)
        print("="*50)
        
        print("\n=== 処理完了 ===")
        return 0
        
    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        return 1
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    exit(main())


