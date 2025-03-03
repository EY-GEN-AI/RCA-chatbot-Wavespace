from fastapi import FastAPI, Request, Response, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from fastapi_cache import FastAPICache 
# from fastapi_cache.backends.inmemory import InMemoryBackend
# from fastapi_cache.decorator import cache
from fastapi.responses import FileResponse, JSONResponse
from backend.api.routes import auth, chat
from backend.core.config import settings
import uvicorn
from contextlib import asynccontextmanager
from backend.database.mongodb import MongoDB
#from backend.database.postgres import PostgresDB
#from backend.database.redis import RedisClient
import logging
import os
from pathlib import Path
from dotenv import load_dotenv  # Import the load_dotenv function
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from diskcache import Cache

# Load environment variables from .env file
load_dotenv()
import logging
#logging.basicConfig()    
#logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Startup: Connect to database
        logger.info("Connecting to Mongo DB")
        await MongoDB.connect_db()
        logger.info("Successfully connected to Mongo")
        logger.info("Connecting to Postgres")
        print("Connecting to Postgres")
        #await PostgresDB.connect_db()
        # print("Successfully connected to Postgres")
        # logger.info("Successfully connected to Postgres")
        yield
    finally:
        # Shutdown: Close connection
        await MongoDB.close_db()
        logger.info("Mongo Database connection closed")
        #await PostgresDB.close_db()
        logger.info("Postgres Database connection closed")


app = FastAPI(
    title="SmartChat API",
    version=settings.VERSION,
    lifespan=lifespan
)




# CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Ensure static directory exists
static_path = os.path.join(os.path.dirname(__file__), "static/dist")
os.makedirs(static_path, exist_ok=True)


#### Main Line to be uncommented to run on Different ports ######
app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets"),html=True), name="assets")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend static files and handle client-side routing"""
    # If API request, let it pass through to the API routes
    if full_path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"message": "API route not found"}
        )
        
    # For all other routes, serve the index.html
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return JSONResponse(
            status_code=404,
            content={"message": "Frontend not built. Please run 'npm run build' first. Then run npm run dev"}
        )

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=int(os.getenv("WEB_CONCURRENCY", 4)),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
