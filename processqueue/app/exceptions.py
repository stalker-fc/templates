class NoSuchTaskException(Exception):
    def __init__(self, task_id: int):
        self.message = f"There is no task with such id = `{task_id}`."


class NoTaskOutputDataException(Exception):
    def __init__(self, task_id: int):
        self.message = f"There is no output data for task with such id = `{task_id}`."
