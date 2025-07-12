import os
import json
from ultralytics import YOLO
from src.db_utils import get_db_connection
from dotenv import load_dotenv

load_dotenv()

def load_raw_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    processed_files = set()
    cur.execute("SELECT DISTINCT data->>'channel' as channel FROM raw_messages")
    existing_channels = {row[0] for row in cur.fetchall()}
    
    for root, _, files in os.walk('data/raw'):
        for file in files:
            if file.endswith('.json'):
                channel_name = file.split('.')[0]
                if channel_name in existing_channels:
                    continue
                    
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    for record in data:
                        cur.execute(
                            "INSERT INTO raw_messages (data) VALUES (%s) RETURNING id",
                            (json.dumps(record),)
                        )
                        message_id = cur.fetchone()[0]
                        
                        # Check if image exists for this message
                        img_path = f"data/images/{root.split('/')[-1]}/{record['id']}.jpg"
                        if os.path.exists(img_path):
                            process_image(img_path, message_id, cur)
    
    conn.commit()
    conn.close()
    print("Data loading completed")

def process_image(image_path, message_id, cursor):
    model = YOLO(os.getenv('YOLO_MODEL', 'yolov8n.pt'))
    results = model(image_path)
    
    for result in results:
        for box in result.boxes:
            cursor.execute(
                """INSERT INTO image_detections 
                (message_id, object_class, confidence)
                VALUES (%s, %s, %s)""",
                (message_id, 
                 result.names[box.cls[0].item()],
                 box.conf[0].item())
            )

if __name__ == '__main__':
    load_raw_data()