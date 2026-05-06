import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from app.config import settings
from app.services.pdf_extractor import pdf_extractor
from app.services.chunker import text_chunker
from app.services.embedder import embedder
from app.services.vector_store import vector_store
from app.services.llm import llm_service
import uuid

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles PDF uploads: Downloads, Ingests, and confirms.
    """
    file = await update.message.document.get_file()
    if not update.message.document.file_name.endswith(".pdf"):
        await update.message.reply_text("Please upload a PDF file.")
        return

    await update.message.reply_text("📥 Processing your document... please wait.")
    
    try:
        # 1. Download file
        content = await file.download_as_bytearray()
        
        # 2. Ingest logic (mimicking the /ingest route)
        pages = pdf_extractor.extract_text(bytes(content))
        chunks = text_chunker.chunk_text(pages)
        
        if not chunks:
            await update.message.reply_text("❌ No readable text found in this PDF.")
            return
            
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embedder.generate_embeddings(chunk_texts)
        
        doc_id = f"{update.message.document.file_name}-{str(uuid.uuid4())[:8]}"
        vector_store.store_chunks(chunks, embeddings, doc_id)
        
        await update.message.reply_text(f"✅ Success! I've learned from '{update.message.document.file_name}'. You can now ask me questions about it.")
        
    except Exception as e:
        logging.error(f"Telegram Ingest Error: {str(e)}")
        await update.message.reply_text(f"⚠️ Sorry, I failed to process that document: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles text questions: Embeds question, retrieves chunks, and answers using Gemini.
    """
    question = update.message.text
    await update.message.reply_text("🔍 Thinking...")
    
    try:
        # 1. Ask logic (mimicking the /ask route)
        question_embedding = embedder.generate_embedding(question)
        relevant_chunks = vector_store.search_similar(question_embedding, limit=5)
        
        if not relevant_chunks:
            await update.message.reply_text("❓ I couldn't find any information about that in my documents.")
            return
            
        answer = llm_service.generate_answer(question, relevant_chunks)
        
        # Add a "Sources" footer for transparency
        source_footer = "\n\n📖 **OFFICIAL SOURCES:**"
        unique_docs = set()
        for i, chunk in enumerate(relevant_chunks):
            doc_name = chunk.get("document_id", "Unknown Document").split("-")[0] # Get filename before the UUID
            page = chunk.get("metadata", {}).get("page_number", "Unknown")
            source_footer += f"\n• Fragment {i+1} — *{doc_name}* (Page {page})"
            
        await update.message.reply_text(
            f"{answer}{source_footer}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Telegram Ask Error: {str(e)}")
        await update.message.reply_text(f"⚠️ Sorry, something went wrong while processing your question: {str(e)}")

if __name__ == '__main__':
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not found in environment.")
        exit(1)
        
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Handle documents (PDFs)
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    
    # Handle text messages (Questions)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Telegram Bot is running...")
    application.run_polling()
