import asyncio

from app.logger import get_logger

logger = get_logger(__name__)


def build_task_queue() -> asyncio.Queue:
    return asyncio.Queue()
