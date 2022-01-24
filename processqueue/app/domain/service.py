from dataclasses import dataclass


@dataclass
class RunTaskMessage:
    task_id: int


@dataclass
class CancelTaskMessage:
    task_id: int
