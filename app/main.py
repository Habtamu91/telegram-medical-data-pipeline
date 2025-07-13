from fastapi import FastAPI, HTTPException, Depends, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.db_utils import get_db_connection, check_db_health
from app.schemas import (
    ChannelStats,
    TopProducts,
    ImageAnalysis,
    APIHealthCheck,
    ErrorResponse,
    SearchQuery,
    Pagination
)
import psycopg2.extras
from dotenv import load_dotenv
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import logging

# Configuration
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Medical Data API",
    description="API for analyzing Ethiopian medical Telegram data",
    version="1.2.0",
    docs_url="/docs",
    redoc_url=None
)

# Security
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["GET"],
    allow_headers=["X-API-Key"]
)

async def validate_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            detail="Too many requests",
            error_code="RATE_LIMIT_EXCEEDED"
        ).dict()
    )

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail=jsonable_encoder(exc.errors()),
            error_code="VALIDATION_ERROR"
        ).dict()
    )

@app.get("/health", response_model=APIHealthCheck)
async def health_check():
    db_ok, db_msg = check_db_health()
    return APIHealthCheck(
        status="healthy" if db_ok else "degraded",
        db_connected=db_ok,
        yolo_ready=os.path.exists("yolov8n.pt"),
        last_scrape_time=datetime.now(),
        active_connections=1
    )

@app.get("/products/top", response_model=TopProducts)
@limiter.limit("10/minute")
async def get_top_products(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1),
    api_key: str = Depends(validate_api_key)
):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
        SELECT 
            data->>'message' as product_name,
            COUNT(*) as count,
            MAX(DATE(data->>'date')) as last_mentioned,
            ARRAY_AGG(DISTINCT data->>'channel') as channels
        FROM raw_messages
        WHERE data->>'message' IS NOT NULL
        AND DATE(data->>'date') >= CURRENT_DATE - %s::integer
        GROUP BY product_name
        ORDER BY count DESC
        LIMIT %s
        """, (days, limit))
        
        results = cur.fetchall()
        return {"products": results}
    except Exception as e:
        logger.error(f"Error in /products/top: {str(e)}")
        raise HTTPException(500, detail=str(e))
    finally:
        conn.close()

@app.get("/images/analysis", response_model=ImageAnalysis)
@limiter.limit("5/minute")
async def get_image_analysis(
    request: Request,
    min_confidence: float = Query(0.5, ge=0.1, le=0.9),
    api_key: str = Depends(validate_api_key)
):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
        SELECT 
            object_class,
            COUNT(*) as count,
            AVG(confidence) as confidence_avg,
            MAX(detected_at) as last_detected
        FROM image_detections
        WHERE confidence >= %s
        GROUP BY object_class
        ORDER BY count DESC
        """, (min_confidence,))
        
        results = cur.fetchall()
        return {
            "top_classes": results,
            "total_detections": sum(row[1] for row in results),
            "processing_time": None
        }
    except Exception as e:
        logger.error(f"Error in /images/analysis: {str(e)}")
        raise HTTPException(500, detail=str(e))
    finally:
        conn.close()

@app.get("/")
async def root():
    return {
        "message": "Ethiopian Medical Data API",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "top_products": "/products/top",
            "image_analysis": "/images/analysis"
        }
    }