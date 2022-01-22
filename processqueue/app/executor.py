import os
import time
import traceback
from dataclasses import dataclass

from app.common import Result
from app.logger import get_logger
from app.storage import build_executor_task_data_storage, ExecutorTaskDataStorageConfig

logger = get_logger(__name__)

@dataclass
class ExecutionConfig:
    executor_task_data_storage_config: ExecutorTaskDataStorageConfig


def execute_task(config: ExecutionConfig, task_id: int) -> Result:
    try:
        logger.info(f"Executing task_id={task_id} in pid={os.getpid()}")

        executor_task_data_storage = build_executor_task_data_storage(
            config.executor_task_data_storage_config
        )
        input_data = executor_task_data_storage.get_input_data(task_id)

        time.sleep(2.)

        output_data = f"{input_data} - successfully executed"

        executor_task_data_storage.set_output_data(task_id, output_data)

        return Result.SUCCESS
    except Exception:
        logger.exception(f'Unable to handle task_id={task_id}. Traceback: {traceback.format_exc()}.')
        return Result.FAILURE