from supabase import create_client, Client
from app.config import settings
from typing import List, Dict, Any

class VectorStore:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )

    def store_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]], document_id: str):
        """
        Inserts document chunks and their embeddings into Supabase.
        """
        data = []
        for i, chunk in enumerate(chunks):
            data.append({
                "document_id": document_id,
                "chunk_text": chunk["text"],
                "chunk_index": chunk["metadata"]["chunk_index"],
                "embedding": embeddings[i],
                "metadata": {
                    "page_number": chunk["metadata"]["page_number"]
                }
            })
            
        try:
            self.supabase.table("document_chunks").insert(data).execute()
        except Exception as e:
            raise ValueError(f"Supabase insertion failed: {str(e)}")

    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a cosine similarity search in pgvector via an RPC call.
        Note: You must define the 'match_documents' function in Supabase SQL editor.
        """
        try:
            # We call the RPC function we will define in Supabase
            result = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.2,
                    "match_count": limit
                }
            ).execute()
            return result.data
        except Exception as e:
            raise ValueError(f"Supabase search failed: {str(e)}")

vector_store = VectorStore()
