#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回答テンプレートでLLMを使って整形するモジュール
"""

import re
from typing import List, Optional
from langchain.schema import Document
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

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
            print(f"LLMを初期化しました: {self.model}")
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
