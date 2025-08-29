#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ベンダー検索 RAG アプリ
Streamlitでベンダー情報検索＆回答生成を行うWebアプリ
"""

import streamlit as st
import time
from query import query_vendor_info

# ページ設定
st.set_page_config(
    page_title="ベンダー検索 RAG アプリ",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """メインアプリケーション"""
    
    # タイトル
    st.title("🔍 ベンダー検索 RAG アプリ")
    st.markdown("---")
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 検索オプション
        st.subheader("検索設定")
        k = st.slider("検索件数", min_value=1, max_value=10, value=5, help="検索するベンダー数")
        use_mmr = st.checkbox("MMR検索を使用", value=True, help="関連性と多様性のバランスを取った検索")
        
        # モデル選択
        st.subheader("LLM設定")
        model = st.selectbox(
            "使用モデル",
            ["gpt-3.5-turbo", "gpt-4"],
            help="使用するOpenAIモデル"
        )
        
        # ベクトルDBパス
        st.subheader("データベース設定")
        vectordb_path = st.text_input(
            "ベクトルDBパス",
            value="vectordb",
            help="ChromaベクトルDBのパス"
        )
        
        # 情報表示
        st.markdown("---")
        st.info("""
        **使用方法:**
        1. 質問を入力
        2. 検索ボタンをクリック
        3. 結果を確認
        
        **検索例:**
        - 契約書管理系のベンダーは？
        - 製造業向けの画像認識AIベンダーは？
        - 医療系のベンダーを教えて
        """)
    
    # メインコンテンツ
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 質問入力")
        
        # 質問入力
        question = st.text_area(
            "検索したい質問を入力してください",
            value="契約書レビューのAIベンダーは？",
            height=100,
            placeholder="例: 契約書管理系のベンダーは？"
        )
        
        # 検索ボタン
        if st.button("🔍 検索実行", type="primary", use_container_width=True):
            if question.strip():
                # プログレスバー
                with st.spinner("検索中..."):
                    progress_bar = st.progress(0)
                    
                    # 検索実行
                    try:
                        # プログレスバー更新
                        progress_bar.progress(25)
                        time.sleep(0.5)
                        
                        # RAG処理実行
                        progress_bar.progress(50)
                        result, token_info = query_vendor_info(
                            question=question,
                            k=k,
                            use_mmr=use_mmr,
                            model=model,
                            vectordb_path=vectordb_path
                        )
                        
                        progress_bar.progress(100)
                        time.sleep(0.5)
                        
                        # 結果表示
                        st.subheader("📊 検索結果")
                        st.markdown(result)
                        
                        # トークン数情報の表示
                        if token_info:
                            st.subheader("📊 トークン使用量")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("質問トークン", token_info.get("question_tokens", 0))
                            with col2:
                                st.metric("コンテキストトークン", token_info.get("context_tokens", 0))
                            with col3:
                                st.metric("回答トークン", token_info.get("response_tokens", 0))
                            with col4:
                                st.metric("合計トークン", token_info.get("total_tokens", 0))
                            
                            # 詳細情報
                            st.info(f"""
                            **詳細情報:**
                            - 使用モデル: {token_info.get("model_used", "N/A")}
                            - 取得ドキュメント数: {token_info.get("documents_retrieved", 0)}件
                            - 検索方法: {'MMR' if use_mmr else '類似度検索'}
                            """)
                        
                        # 成功メッセージ
                        st.success("検索が完了しました！")
                        
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
                        progress_bar.progress(0)
            else:
                st.warning("質問を入力してください。")
    
    with col2:
        st.subheader("📈 統計情報")
        
        # 統計情報の表示
        try:
            from query import VendorRetriever, load_environment
            api_key = load_environment()
            retriever = VendorRetriever(vectordb_path=vectordb_path, api_key=api_key)
            doc_count = retriever.get_document_count()
            
            st.metric("ベクトルDB内のベンダー数", doc_count)
            
            if doc_count > 0:
                st.success("✅ ベクトルDBが正常に読み込まれています")
            else:
                st.error("❌ ベクトルDBにデータがありません")
                
        except Exception as e:
            st.error(f"❌ ベクトルDBの読み込みに失敗: {e}")
        
        # 使用設定の表示
        st.subheader("🔧 現在の設定")
        st.write(f"**検索件数:** {k}")
        st.write(f"**検索方法:** {'MMR' if use_mmr else '類似度検索'}")
        st.write(f"**使用モデル:** {model}")
        st.write(f"**ベクトルDB:** {vectordb_path}")
    
    # フッター
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>ベンダー検索 RAG アプリ | Powered by LangChain + OpenAI + Chroma</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
