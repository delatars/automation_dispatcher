# -*- coding: utf-8 -*-
import time

from strategies.queue.queue_template import QueueStrategy
from loaders.tasks import TasksLoader
from logger import STREAM


class PriorityStrategy(QueueStrategy):
    def __init__(self):
        self.loader = TasksLoader()

    def get_first_task_by_filter(self, **kwargs):
        filtered = self.loader.waiting.filter_tasks(**kwargs)
        if not filtered:
            return False
        first_timestamp_task = type("first_task", (), {"build_timestamp": time.time()})
        for task in filtered:
            try:
                if int(task.build_timestamp) < int(first_timestamp_task.build_timestamp):
                    first_timestamp_task = task
            except AttributeError:
                STREAM.warning("Task %s: Wrong format, attribute 'build_timestamp' not found." % task.uuid)
        if not hasattr(first_timestamp_task, "uuid"):
            return False
        return first_timestamp_task

    def __iter__(self):
        return self

    def __next__(self):
        uuid = (lambda x: x.uuid if x else [])
        group_system = self.get_first_task_by_filter(group="system")
        STREAM.debug("System task: %s" % uuid(group_system))

        priority_high = self.get_first_task_by_filter(priority="high")
        STREAM.debug("High priority task: %s" % uuid(priority_high))

        priority_normal = self.get_first_task_by_filter(priority="normal")
        STREAM.debug("Normal priority task: %s" % uuid(priority_normal))

        priority_low = self.get_first_task_by_filter(priority="low")
        STREAM.debug("Low priority task: %s" % uuid(priority_low))

        group_guest = self.get_first_task_by_filter(group="guest")
        STREAM.debug("Guest task: %s" % uuid(group_guest))
        if group_system:
            return group_system
        elif priority_high:
            return priority_high
        elif priority_normal:
            return priority_normal
        elif priority_low:
            return priority_low
        elif group_guest:
            return group_guest
        else:
            return None


if __name__ == '__main__':
    pass
