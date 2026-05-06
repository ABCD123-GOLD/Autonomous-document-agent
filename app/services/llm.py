from openai import OpenAI
from app.config import settings
from app.prompts import RAG_SYSTEM_PROMPT
from typing import List, Dict, Any

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini" # Fast and efficient for RAG

    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Constructs the prompt with context and calls OpenAI to get the answer.
        """
        context_str = ""
        for i, chunk in enumerate(context_chunks):
            page_num = chunk.get("metadata", {}).get("page_number", "Unknown")
            context_str += f"--- Fragment {i+1} (Page {page_num}) ---\n{chunk['chunk_text']}\n\n"

        prompt = RAG_SYSTEM_PROMPT.format(
            context=context_str,
            question=question
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional AI Assistant for the Production RAG API."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1 # Low temperature for factual consistency
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"OpenAI generation failed: {str(e)}")

llm_service = LLMService()
