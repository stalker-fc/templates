import abc
from dataclasses import dataclass
from typing import Dict

__all__ = [
    "build_executor_task_data_storage",
    "IExecutorTaskDataStorage",
    "ExecutorTaskDataStorageConfig"
]

class IExecutorTaskDataStorage(abc.ABC):
    @abc.abstractmethod
    def get_input_data(self, task_id: int) -> str:
        pass

    @abc.abstractmethod
    def set_input_data(self, task_id: int, input_data: str) -> None:
        pass

    @abc.abstractmethod
    def get_output_data(self, task_id: int) -> str:
        pass

    @abc.abstractmethod
    def set_output_data(self, task_id: int, output_data: str) -> None:
        pass


class DummyExecutorTaskDataStorage(IExecutorTaskDataStorage):
    def __init__(self):
        self._task_id_to_input_data: Dict[int, str] = {}
        self._task_id_to_output_data: Dict[int, str] = {}

    def get_input_data(self, task_id: int) -> str:
        return self._task_id_to_input_data[task_id]

    def set_input_data(self, task_id: int, input_data: str) -> None:
        self._task_id_to_input_data[task_id] = input_data

    def get_output_data(self, task_id: int) -> str:
        return self._task_id_to_output_data[task_id]

    def set_output_data(self, task_id: int, output_data: str) -> None:
        self._task_id_to_output_data[task_id] = output_data


@dataclass
class ExecutorTaskDataStorageConfig:
    pass


def build_executor_task_data_storage(config: ExecutorTaskDataStorageConfig) -> IExecutorTaskDataStorage:
    return DummyExecutorTaskDataStorage()
