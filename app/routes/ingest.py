from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.pdf_extractor import pdf_extractor
from app.services.chunker import text_chunker
from app.services.embedder import embedder
from app.services.vector_store import vector_store
from app.models.schemas import IngestResponse
import uuid

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingests a PDF document: Extract -> Chunk -> Embed -> Store.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # 1. Read file content
        content = await file.read()
        
        # 2. Extract text from PDF
        pages = pdf_extractor.extract_text(content)
        
        # 3. Split into chunks
        chunks = text_chunker.chunk_text(pages)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")
            
        # 4. Generate embeddings for all chunks
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedder.generate_embeddings(chunk_texts)
        
        # 5. Store in Supabase
        doc_id = f"{file.filename}-{str(uuid.uuid4())[:8]}"
        vector_store.store_chunks(chunks, embeddings, doc_id)
        
        return IngestResponse(
            document_id=doc_id,
            chunks_processed=len(chunks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
