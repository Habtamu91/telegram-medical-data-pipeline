from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.db_utils import get_db_connection
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Medical Data API",
              description="API for analyzing medical Telegram data",
              version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/top-products")
async def top_products(limit: int = 10):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
        SELECT data->>'message' as text, COUNT(*) as count
        FROM raw_messages
        WHERE data->>'message' IS NOT NULL
        GROUP BY text
        ORDER BY count DESC
        LIMIT %s
        """, (limit,))
        
        return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/channel/{channel_name}")
async def get_channel_data(channel_name: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("""
        SELECT 
            DATE(data->>'date') as date,
            COUNT(*) as message_count,
            SUM(CASE WHEN data->>'media' = 'true' THEN 1 ELSE 0 END) as media_count
        FROM raw_messages
        WHERE data->>'channel' = %s
        GROUP BY date
        ORDER BY date
        """, (channel_name,))
        
        return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Data API. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, 
               host=os.getenv('APP_HOST', '0.0.0.0'), 
               port=int(os.getenv('APP_PORT', 8000)))