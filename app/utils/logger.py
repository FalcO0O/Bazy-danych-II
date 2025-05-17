import logging
from datetime import datetime, timezone
from database import logs_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_operation(operation_type: str, collection_name: str, meta: dict = None):
    meta = meta or {}
    log_doc = {
        "operation_type": operation_type,
        "timestamp": datetime.now(timezone.utc),
        "meta": meta,
        "collection": collection_name
    }
    try:
        await logs_collection.insert_one(log_doc)
    except Exception as e:
        logger.error(f"Failed to write log to DB: {e}")

def log_info(message: str):
    logger.info(message)

def log_error(message: str):
    logger.error(message)
