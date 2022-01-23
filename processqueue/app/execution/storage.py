import abc
from dataclasses import dataclass
from pathlib import Path

from app.exceptions import NoSuchTaskException
from app.exceptions import NoTaskOutputDataException
from app.logger import get_logger

logger = get_logger(__name__)

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


class FileExecutorTaskDataStorage(IExecutorTaskDataStorage):
    def __init__(self, root_data_folder: Path):
        if root_data_folder.is_file():
            logger.error(f"{root_data_folder} is file, not directory")
            raise ValueError(f"Path `{root_data_folder} must be a directory, not a file.")

        root_data_folder.mkdir(exist_ok=True, parents=True)
        self._root_data_folder = root_data_folder

    def get_input_data(self, task_id: int) -> str:
        path_to_file = self._get_path_to_file(task_id, is_input_data=True)
        try:
            output_data = self._load_data(path_to_file)
            return output_data
        except Exception:
            logger.exception(f'Unable to load input data for task id=`{task_id}`.')
            raise NoSuchTaskException(task_id)

    def set_input_data(self, task_id: int, input_data: str) -> None:
        path_to_file = self._get_path_to_file(task_id, is_input_data=True)
        logger.info(f"Save task id={task_id} to {path_to_file}")
        try:
            self._save_data(path_to_file, input_data)
        except Exception:
            logger.exception(f'Unable to save input data for task id=`{task_id}`.')

    def get_output_data(self, task_id: int) -> str:
        path_to_file = self._get_path_to_file(task_id, is_input_data=False)
        try:
            output_data = self._load_data(path_to_file)
            return output_data
        except Exception:
            logger.exception(f'Unable to save output data for task id=`{task_id}`.')
            raise NoTaskOutputDataException(task_id)

    def set_output_data(self, task_id: int, output_data: str) -> None:
        path_to_file = self._get_path_to_file(task_id, is_input_data=False)
        logger.info(f"Save task id={task_id} to {path_to_file}")
        try:
            self._save_data(path_to_file, output_data)
        except Exception:
            logger.exception(f'Unable to save output data for task id=`{task_id}`.')

    def _get_data_folder(self, task_id: int) -> Path:
        return self._root_data_folder / str(task_id)

    def _get_path_to_file(self, task_id: int, is_input_data: bool) -> Path:
        if is_input_data:
            filename = "input.txt"
        else:
            filename = "output.txt"

        data_folder = self._get_data_folder(task_id)
        return data_folder / filename

    def _save_data(self, path_to_file: Path, data: str) -> None:
        path_to_file.parent.mkdir(exist_ok=True, parents=True)
        with open(str(path_to_file), 'w') as file:
            file.write(data)

    def _load_data(self, path_to_file: Path) -> str:
        with open(str(path_to_file), 'r') as file:
            data = file.read()
        return data


@dataclass
class ExecutorTaskDataStorageConfig:
    pass


def build_executor_task_data_storage(config: ExecutorTaskDataStorageConfig) -> IExecutorTaskDataStorage:
    root_data_folder = Path(__file__)
    return FileExecutorTaskDataStorage(root_data_folder)
