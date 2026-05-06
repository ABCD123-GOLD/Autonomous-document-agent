from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.config import settings
from app.routes import ingest, ask, health
import structlog

# Initialize structured logging
logger = structlog.get_logger()

app = FastAPI(
    title="Production RAG API",
    description="Ask any document. Get cited answers.",
    version="1.0.0"
)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if settings.ENVIRONMENT == "development":
        return "dev_key"
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return api_key

# Include Routers
app.include_router(health.router)
app.include_router(ingest.router, dependencies=[Depends(get_api_key)])
app.include_router(ask.router, dependencies=[Depends(get_api_key)])

@app.get("/")
async def root():
    return {"message": "Welcome to the Production RAG API. Visit /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
