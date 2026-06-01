"""
simple_task.py

Provides the SimpleTask class for managing named async countdown tasks
using Python's asyncio framework. Tasks run concurrently and self-remove
from a shared registry upon completion.
"""

import asyncio


class SimpleTask:
    """
    Represents an asynchronous countdown task with a shared task registry.

    Each instance registers itself in the class-level `tasks` list upon
    creation and removes itself when it finishes. Tasks run concurrently
    via asyncio and print progress updates every second.

    Class Attributes:
        tasks (list[SimpleTask]): Shared registry of all active task instances.

    Instance Attributes:
        name (str): Human-readable label for the task.
        time (int): Number of seconds the task counts down from.
        status (int): Lifecycle state of the task.
            0 = not started, 1 = running, 2 = finished.
        index (int): Current position of this task in the shared `tasks` list.
        task (asyncio.Task | None): The underlying asyncio Task object,
            set when `run()` is called.
    """

    tasks = []

    def __init__(self, name: str, time: int) -> None:
        """
        Initialize a new SimpleTask and register it in the shared task list.

        Args:
            name: A label used in log output to identify this task.
            time: Duration in seconds for the countdown.
        """
        SimpleTask.tasks.append(self)
        self.name = name
        self.time = time
        self.status = 0
        self.index = len(self.tasks) - 1
        self.task = None

    async def _counter(self) -> None:
        """
        Internal coroutine that runs the countdown loop.

        Prints the remaining time every second, then calls `end()` to
        clean up the task registry once the countdown reaches zero.
        This coroutine is wrapped in an asyncio.Task by `run()`.
        """
        num = self.time
        print(f"Task {self.name}({self.index}) is running ...")
        while num:
            print(f"Task {self.name}({self.index}) will finish in {num} seconds...")
            await asyncio.sleep(1)
            num -= 1
        await self.end()
        print(f"Task {self.name}({self.index}) is finished ...")

    async def run(self) -> None:
        """
        Start the task if it has not been started yet.

        Creates an asyncio Task from `_counter()` and stores it in
        `self.task`. The task runs concurrently; callers should await
        the returned task (or use asyncio.gather) to wait for completion.

        Does nothing if the task is already running or finished
        (i.e. status != 0).
        """
        if self.status == 0:
            self.status = 1
            self.task = asyncio.create_task(self._counter())

    async def end(self) -> None:
        """
        Mark the task as finished and remove it from the shared registry.

        Updates `status` to 2, removes this instance from `SimpleTask.tasks`,
        and decrements the `index` of all subsequent tasks so their indices
        remain consistent with their new positions in the list.

        Does nothing if the task is not currently running (status != 1).
        """
        if self.status == 1:
            self.status = 2
            self.tasks.pop(self.index)

            # Keep indices consistent for tasks that come after this one
            for obj in self.tasks:
                if obj.index > self.index:
                    obj.index -= 1


async def event_loop() -> None:
    """
    Entry point that creates three SimpleTask instances and runs them concurrently.

    Each task is started with `run()`, which schedules it as a background
    asyncio Task. `asyncio.gather()` then waits for all of them to finish
    before the event loop exits.
    """
    task1 = SimpleTask("Task1", 3)
    task2 = SimpleTask("Task2", 5)
    task3 = SimpleTask("Task3", 2)

    await task1.run()
    await task2.run()
    await task3.run()

    # Wait for all background tasks to complete before the event loop exits
    await asyncio.gather(
        *[t.task for t in SimpleTask.tasks if t.task is not None]
    )


if __name__ == "__main__":
    asyncio.run(event_loop())
    