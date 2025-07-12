import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create tables if they don't exist
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
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully")