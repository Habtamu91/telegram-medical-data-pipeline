from dagster import job, op, repository, schedule
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@op
def init_db():
    from src.db_utils import init_db
    init_db()
    logger.info("Database initialized")

@op
def scrape_telegram():
    from src.telegram_client import main
    import asyncio
    asyncio.run(main())
    logger.info("Telegram scraping completed")

@op
def process_data():
    from src.data_pipeline import load_raw_data
    load_raw_data()
    logger.info("Data processing completed")

@job
def telegram_pipeline():
    process_data(scrape_telegram(init_db()))

@schedule(
    cron_schedule="0 0 * * *",
    job=telegram_pipeline,
    execution_timezone="UTC"
)
def daily_schedule(context):
    scheduled_date = context.scheduled_execution_time.strftime("%Y-%m-%d")
    return {
        "ops": {
            "scrape_telegram": {
                "config": {
                    "scheduled_date": scheduled_date
                }
            }
        }
    }

@repository
def repo():
    return [telegram_pipeline, daily_schedule]