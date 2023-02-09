import logging
from datetime import datetime
from typing import Any

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Result, Task

logger = logging.getLogger(__name__)


class TaskDuration:
    def __init__(self) -> None:
        """Initializes the processor"""
        self.durations: dict[str, Any] = {
            "task": {"starttime": None, "endtime": {}},
            "instances": {},
            "hosts": {},
        }

    def task_started(self, task: Task) -> None:
        """This method is called right before starting the task"""

        self.durations["task"]["starttime"] = datetime.now()

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        """This method is called when all the hosts have completed executing their respective task"""

        self.durations["task"]["endtime"] = datetime.now()

        duration = (
            self.durations["task"]["endtime"] - self.durations["task"]["starttime"]
        ).seconds

        if result and type(result) is AggregatedResult:
            setattr(result, "total_duration", duration)

    def task_instance_started(self, task: Task, host: Host) -> None:
        """This method is called before a host starts executing its instance of the task"""

        self.durations["hosts"].setdefault(
            host.name, {"starttime": datetime.now(), "endtime": None}
        )

        self.durations["instances"].setdefault(host.name, {})
        self.durations["instances"][host.name][task.name] = {
            "starttime": datetime.now(),
            "endtime": None,
        }

    def task_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """This method is called when a host completes its instance of a task"""

        self.durations["instances"][host.name][task.name]["endtime"] = datetime.now()

        self.durations["hosts"][host.name]["endtime"] = datetime.now()

        duration = (
            self.durations["instances"][host.name][task.name]["endtime"]
            - self.durations["instances"][host.name][task.name]["starttime"]
        ).seconds

        host_duration = (
            self.durations["hosts"][host.name]["endtime"]
            - self.durations["hosts"][host.name]["starttime"]
        ).seconds

        # set - override the host duration
        if type(result) is MultiResult:
            setattr(result, "host_duration", host_duration)

        if (
            type(result) is MultiResult
            and len(result) > 0
            and type(result[0]) is Result
        ):
            setattr(result[0], "duration", duration)

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        """This method is called before a host starts executing a subtask"""

        self.durations["instances"][host.name].setdefault(task.parent_task.name, {})
        self.durations["instances"][host.name][task.parent_task.name].setdefault(
            task.name, {"starttime": datetime.now(), "endtime": None}
        )

    def subtask_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """This method is called when a host completes executing a subtask"""

        self.durations["instances"][host.name][task.parent_task.name][task.name][
            "endtime"
        ] = datetime.now()

        duration = (
            self.durations["instances"][host.name][task.parent_task.name][task.name][
                "endtime"
            ]
            - self.durations["instances"][host.name][task.parent_task.name][task.name][
                "starttime"
            ]
        ).seconds

        # set the subtask duration
        if (
            type(result) is MultiResult
            and len(result) > 0
            and type(result[0]) is Result
        ):
            setattr(result[0], "duration", duration)
