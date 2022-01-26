from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TaskInfo:
    task_id: int
    status: str


@dataclass_json
@dataclass
class TaskInputData:
    input_data: str


@dataclass_json
@dataclass
class TaskOutputData:
    task_id: int
    output_data: str


