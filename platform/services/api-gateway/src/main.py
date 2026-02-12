from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import api_router

app = FastAPI(
    title="ALGORITHMIC ARTS API Gateway",
    description="API Gateway for the Partnership Intelligence Platform",
    version="0.1.0",
)

# CORS middleware - restrict to known origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://platform.algorithmic-arts.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")

@app.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "api-gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)