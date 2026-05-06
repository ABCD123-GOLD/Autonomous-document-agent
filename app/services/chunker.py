import tiktoken
from typing import List, Dict

class TextChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Using cl100k_base which is standard for OpenAI models
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, pages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Splits text from pages into chunks of approximately chunk_size tokens 
        with an overlap.
        """
        chunks = []
        
        for page in pages:
            text = page["text"]
            page_num = page["page_number"]
            
            tokens = self.tokenizer.encode(text)
            
            for i in range(0, len(tokens), self.chunk_size - self.overlap):
                chunk_tokens = tokens[i : i + self.chunk_size]
                chunk_text = self.tokenizer.decode(chunk_tokens)
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "page_number": page_num,
                        "chunk_index": len(chunks)
                    }
                })
                
                # If we've reached the end of the tokens, stop
                if i + self.chunk_size >= len(tokens):
                    break
                    
        return chunks

text_chunker = TextChunker()
