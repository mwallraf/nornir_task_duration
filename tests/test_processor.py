from nornir import InitNornir
from nornir_task_duration.plugins.processors import TaskDuration

from nornir.core.task import Result, Task, AggregatedResult, MultiResult

import time


def dummy_task(task):
    return "hi!!!"


nr = InitNornir(
    inventory={
        "plugin": "YAMLInventory",
        "options": {
            "host_file": "tests/inventory/hosts.yaml",
            "group_file": "tests/inventory/groups.yaml",
            "defaults_file": "tests/inventory/defaults.yaml",
        },
    }
)


def taskParent(task: Task, msg: str) -> Result:
    task.run(task=task1, msg="run my first task")
    task.run(task=task2, msg="run my second task")

    if task.host.name == "test1":
        time.sleep(2)
    else:
        time.sleep(5)

    return Result(host=task.host, result=f"PARENT: {msg}")


def task1(task: Task, msg: str) -> Result:
    time.sleep(1)
    task.run(task=task2, msg="child of first task")

    return Result(host=task.host, result=f"- TASK1: {msg}")


def task2(task: Task, msg: str) -> Result:
    time.sleep(3)
    return Result(host=task.host, result=f"- TASK2: {msg}")


def printer(res):
    if type(res) is AggregatedResult:
        print(f"TOTAL DURATION:{res.total_duration}")
        for r in res:
            print(f" * HOST:{r} - DURATION:{res[r].host_duration}")
            printer(res[r])
    if type(res) is MultiResult:
        for r in res:
            printer(r)
    if type(res) is Result:
        print(f"  -- task:{res.name} - duration:{res.duration}")


def test_processor():
    """
    TOTAL DURATION:12
     * HOST:test1 - DURATION:9
     -- task:ROOT-TASK - duration:9
     -- task:task1 - duration:4
     -- task:task2 - duration:3
     -- task:task2 - duration:3
     * HOST:test2 - DURATION:12
     -- task:ROOT-TASK - duration:12
     -- task:task1 - duration:4
     -- task:task2 - duration:3
     -- task:task2 - duration:3
    """

    nrp = nr.with_processors([TaskDuration()])

    results = nrp.run(name="ROOT-TASK", task=taskParent, msg="run parent task")

    # printer(results)

    # AggregatedResult will have: total_duration
    assert results.total_duration == 12
    # The root task will have: host_duration
    assert results["test1"].host_duration == 9
    assert results["test2"].host_duration == 12
    # Individual tasks will have: duration
    assert results["test1"][0].duration == 9
    assert results["test2"][1].duration == 4
