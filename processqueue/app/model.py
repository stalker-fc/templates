from enum import Enum
from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json


class TaskStatus(Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass_json
@dataclass
class Task:
    task_id: int = 0
    status: TaskStatus = TaskStatus.CREATED
    input_data: str = ""
    output_data: Optional[str] = None
