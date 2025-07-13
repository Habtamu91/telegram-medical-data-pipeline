import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def get_db_connection():
    """Establish and return a new database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def check_db_health() -> Tuple[bool, str]:
    """
    Check if database is reachable
    Returns:
        Tuple: (success: bool, message: str)
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            conn.close()
        return True, "Database connection successful"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False, f"Database connection failed: {str(e)}"

def init_db():
    """Initialize database tables"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create tables
        cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_messages (
            id SERIAL PRIMARY KEY,
            data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS image_detections (
            id SERIAL PRIMARY KEY,
            message_id INTEGER REFERENCES raw_messages(id),
            object_class TEXT,
            confidence FLOAT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()