# -*- coding: utf-8 -*-

import os
import json
import re
import shutil
from typing import List, Any

import settings
from logger import STREAM


class _Task:
    """ Task object implementation """
    def __init__(self, **kwargs):
        for parameter, value in kwargs.items():
            setattr(self, parameter, value)

    def push_to_running(self):
        if self.status == "waiting":
            try:
                shutil.move(os.path.join(self.queue_directory, "waiting", self.uuid),
                            os.path.join(self.queue_directory, "running", self.uuid))
                STREAM.info("Task: %s : Moved to running" % self.uuid)
            except FileNotFoundError:
                STREAM.warning("Task: %s : Can't run! Maybe already running" % self.uuid)
        else:
            STREAM.warning("Task: %s : Already running")

    def discard(self):
        try:
            os.remove(os.path.join(self.queue_directory, self.status, self.uuid))
        except FileNotFoundError:
            STREAM.warning("Task: %s : File not found!" % self.uuid)


class _TaskProperty:

    def __init__(self, tasks):
        self.tasks = tasks

    def count_tasks(self, **kwargs):
        return len(self.filter_tasks(**kwargs))

    def filter_tasks(self, **kwargs):
        """ Method get filter, and return list of filtered tasks
            Example:
                filter_tasks(group="unix", priority="low") """
        tasks = self.tasks
        for attr, value in kwargs.items():
            tasks = list(filter(lambda task_object: getattr(task_object, attr) == value, tasks))
        return tasks


class TasksLoader:
    """
    Load tasks objects from waiting and running directories

    examples:
    >> BASE_QUEUE_PATH = "/queue"
    >> loader = TasksLoader(BASE_QUEUE_PATH)
    >> loader.waiting
        <loaders.tasks._TaskProperty object at 0x7fb0c3ff3fd0>

    >> loader.waiting.tasks
        [<loaders.tasks._Task object at 0x7fb0c1382358>, <loaders.tasks._Task object at 0x7fb0c13821d0>]

    >> loader.running.tasks
        [<loaders.tasks._Task object at 0x7fb0c1382780>]
    """
    _INSTANCE = None
    _QUEUE_TYPE = ""
    _GROUPS = settings.TASK_GROUPS
    _WAITING_TASKS = []
    _RUNNING_TASKS = []
    _WAITING_TASKS_CACHE = []
    _RUNNING_TASKS_CACHE = []

    def __new__(cls, *args, **kwargs):
        """ Singleton object

        >> loader = TasksLoader()
        >> loader
            <loaders.tasks.TasksLoader object at 0x7fb0c15fceb8>
        >> loader2 = TasksLoader()
        >> loader2
            <loaders.tasks.TasksLoader object at 0x7fb0c15fceb8>
        """
        if cls._INSTANCE is None:
            cls._INSTANCE = super(TasksLoader, cls).__new__(cls)
        return cls._INSTANCE

    def __init__(self, base_directory=settings.BASE_QUEUE_PATH):
        self._base_directory = base_directory

    def _compare_listings(self, listing, cached_listing):
        """ Compare os.listdir with cache

        arrived : rtype : list
            List with new arrived tasks
        deleted : rtype : list
            List with tasks should be deleted
        """
        arrived = list(set(listing) - set(cached_listing))
        STREAM.debug(" -> new arrived tasks: %s" % arrived)
        deleted = list(set(cached_listing) - set(listing))
        STREAM.debug(" -> deleted tasks: %s" % deleted)
        return arrived, deleted

    def _get_listing_from_cache(self):
        """ Get directory listing, previously saved in file """
        cache_list = getattr(self, "_%s_TASKS_CACHE" % self._QUEUE_TYPE.upper())
        assert isinstance(cache_list, list), "listing: expected type <list>"
        return cache_list

    def _get_path(self):
        """
        return path based on _base_directory and _QUEUE_TYPE
        :rtype: path
        """
        path = os.path.join(self._base_directory, self._QUEUE_TYPE)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def _get_task_group(self, name):
        try:
            group = re.findall(r"^(\w)-", name)[0]
        except IndexError:
            group = ""
        return self._GROUPS.get(group, "unknown")

    def _get_task_files(self, directory):
        """
        Get files from directory and return only new added files
        Using cache to reduce the number of IO reads.
        Reads only new added files to directory.
        """
        directory_listing = [fil for fil in os.listdir(directory) if not fil.startswith(".")]
        STREAM.debug(" -> listdir tasks: %s" % directory_listing)
        cached_directory_listing = self._get_listing_from_cache()
        STREAM.debug(" -> cached tasks: %s" % cached_directory_listing)
        arrived, deleted = self._compare_listings(directory_listing, cached_directory_listing)
        self._remove_deleted_tasks(deleted)
        arrived_abs_path = [os.path.join(directory, fil) for fil in arrived]
        self._save_listing_to_cache(directory_listing)
        return arrived_abs_path

    def _remove_deleted_tasks(self, deleted_list):
        """ Remove deleted tasks from tasks lists """
        get_obj_list = getattr(self, "_%s_TASKS" % self._QUEUE_TYPE.upper())
        iter_list = iter(list(get_obj_list))
        for task_obj in iter_list:
            if task_obj.uuid in deleted_list:
                get_obj_list.remove(task_obj)

    def _save_listing_to_cache(self, listing):
        """ Save directory listing to the file with json format """
        assert isinstance(listing, list), "listing: expected type <list>"
        setattr(self, "_%s_TASKS_CACHE" % self._QUEUE_TYPE.upper(), listing)

    def _load_tasks(self, directory):
        TASKS = []
        tasks_files = self._get_task_files(directory)
        for file_path in tasks_files:
            file_name = os.path.basename(file_path)
            with open(file_path) as task_file:
                parameters = task_file.read().replace("\n", "")
                parameters = parameters.split(";")
                TASKS.append(
                    _Task(
                        queue_directory=self._base_directory,
                        status=self._QUEUE_TYPE,
                        uuid=file_name,
                        group=self._get_task_group(file_name),
                        priority=parameters[0],
                        resource=parameters[1],
                        build_name=parameters[2],
                        build_number=parameters[3],
                        build_email=parameters[4],
                        build_url=parameters[5],
                        build_timestamp=parameters[6]
                    )
                )
        return TASKS

    @property
    def waiting(self):
        self._QUEUE_TYPE = "waiting"
        waiting_path = self._get_path()
        STREAM.debug("Get waiting tasks:")
        tasks = self._load_tasks(waiting_path)
        self._WAITING_TASKS += tasks
        return _TaskProperty(self._WAITING_TASKS)

    @property
    def running(self):
        self._QUEUE_TYPE = "running"
        running_path = self._get_path()
        STREAM.debug("Get running tasks:")
        tasks = self._load_tasks(running_path)
        self._RUNNING_TASKS += tasks
        return _TaskProperty(self._RUNNING_TASKS)


if __name__ == '__main__':
    loader = TasksLoader()
    STREAM.info(loader.waiting.tasks)
    STREAM.info(loader.running.tasks)
