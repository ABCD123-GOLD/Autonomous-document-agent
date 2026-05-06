from fastapi import APIRouter, HTTPException
from app.services.embedder import embedder
from app.services.vector_store import vector_store
from app.services.llm import llm_service
from app.models.schemas import AskRequest, AskResponse, Citation

router = APIRouter(prefix="/ask", tags=["query"])

@router.post("/", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Answers a question based on ingested documents.
    """
    try:
        # 1. Embed the question
        question_embedding = embedder.generate_embedding(request.question)
        
        # 2. Search for similar chunks in Supabase
        relevant_chunks = vector_store.search_similar(
            question_embedding, 
            limit=request.limit
        )
        
        if not relevant_chunks:
            return AskResponse(
                answer="I couldn't find any relevant information in your documents to answer this question.",
                citations=[]
            )
            
        # 3. Generate answer using Gemini Flash
        answer = llm_service.generate_answer(request.question, relevant_chunks)
        
        # 4. Format citations
        citations = [
            Citation(
                page_number=str(chunk.get("metadata", {}).get("page_number", "Unknown")),
                text=chunk["chunk_text"][:200] + "..." # Snippet for reference
            )
            for chunk in relevant_chunks
        ]
        
        return AskResponse(
            answer=answer,
            citations=citations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
