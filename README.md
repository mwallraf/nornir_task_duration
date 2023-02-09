# nornir_task_duration

`Nornir processor plugin` which calculates the duration of each task

This plugin will store the duration of each task as attribute in the Nornir result objects.

## Installation

```bash
pip install nornir_task_duration
```

## Purpose

The plugin will add new class attributes to the Nornir results:

- **total_duration**: this is the total duration to process all hosts, this is added to the AggregatedResult
- **host_duration**: this is the totoal duration to process a single host, this is added to the host's MultiResult
- **duration**: this is added to the Result of each task

## Usage

This example shows the usage of the processor and an example how to print a summary. You may want to use the duration during the task execution or in another print plugin.

```python

from nornir import InitNornir
from nornir.core.task import Result, Task, AggregatedResult, MultiResult
from nornir_task_duration.plugins.processors import TaskDuration

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

nrp = nr.with_processors([TaskDuration()])

results = nrp.run(task=some_task)

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

printer(results)


# TOTAL DURATION:12
#   * HOST:test1 - DURATION:9
#      -- task:ROOT-TASK - duration:9
#      -- task:task1 - duration:4
#      -- task:task2 - duration:3
#      -- task:task2 - duration:3
#   * HOST:test2 - DURATION:12
#      -- task:ROOT-TASK - duration:12
#      -- task:task1 - duration:4
#      -- task:task2 - duration:3
#      -- task:task2 - duration:3

```
