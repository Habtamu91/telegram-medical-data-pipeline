import os
import json
import asyncio
from datetime import datetime
from telethon.sync import TelegramClient
from dotenv import load_dotenv

load_dotenv()

async def scrape_channel(client, channel_url, limit=100):
    try:
        channel = await client.get_entity(channel_url)
        posts = await client.get_messages(channel, limit=limit)
        
        today = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(f"data/raw/{today}", exist_ok=True)
        
        channel_name = channel_url.split('/')[-1]
        data = []
        
        for msg in posts:
            data.append({
                'id': msg.id,
                'date': msg.date.isoformat(),
                'message': msg.text,
                'media': bool(msg.media),
                'channel': channel_name
            })
            
            if msg.media:
                os.makedirs(f"data/images/{today}", exist_ok=True)
                await client.download_media(msg, file=f"data/images/{today}/{msg.id}.jpg")
        
        with open(f"data/raw/{today}/{channel_name}.json", 'w') as f:
            json.dump(data, f)
            
        return len(posts)
    except Exception as e:
        print(f"Error scraping {channel_url}: {str(e)}")
        return 0

async def main():
    channels = [
        "https://t.me/CheMed123",
        "https://t.me/lobelia4cosmetics",
        "https://t.me/tikvahpharma"
    ]
    
    async with TelegramClient(
        'session_name',
        int(os.getenv('API_ID')),
        os.getenv('API_HASH'),
        system_version="4.16.30",
        device_model="MedicalDataScraper",
        app_version="1.0"
    ) as client:
        for channel in channels:
            count = await scrape_channel(client, channel)
            print(f"Scraped {count} messages from {channel}")

if __name__ == '__main__':
    asyncio.run(main())