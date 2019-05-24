#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from time import sleep
from threading import Thread

import settings
from logger import STREAM, LoggerOptions
from exporters.exporter_template import MetricsExporter
from strategies.distribution.distribution_template import DistributionStrategy
from strategies.queue.queue_template import QueueStrategy


class TaskDistributionAdapter:

    def __init__(self, strategy):
        self.strategy = strategy

    def distribute_task(self, task):
        return self.strategy.distribute_task(task)


class TaskQueueAdapter:

    def __init__(self, strategy):
        assert hasattr(strategy, '__iter__'), "Strategy must be an iterator object."
        self.strategy = strategy

    def __iter__(self):
        return self.strategy

    def __next__(self):
        try:
            return next(self.strategy)
        except StopIteration:
            return None


class Dispatcher:

    def __init__(self):
        LoggerOptions.set_component("Dispatcher")
        STREAM.info("******************************")
        STREAM.info("Initialization...")
        STREAM.info("******************************")
        self.check_and_print_settings()
        self._start_exporters()
        self.queue = TaskQueueAdapter(settings.QUEUE_STRATEGY)
        self.distribution = TaskDistributionAdapter(settings.DISTRIBUTE_STRATEGY)

    def check_and_print_settings(self):
        # check vars
        assert isinstance(settings.LOGLEVEL, int), "settings.LOGLEVEL: expected int(10-50)"
        assert isinstance(settings.TASK_GROUPS, dict), "settings.TASK_GROUPS: expected dict"
        assert isinstance(settings.QUEUE_IDLE_INTERVAL, int), "settings.QUEUE_IDLE_INTERVAL: expected int"
        assert isinstance(settings.CLUSTER_NODE_GROUPS, dict), "settings.CLUSTER_NODE_GROUPS: expected dict"
        assert (True if os.path.exists(settings.BASE_QUEUE_PATH) and os.path.isdir(settings.BASE_QUEUE_PATH) else False),\
            "settings.BASE_QUEUE_PATH: expected directory_path"
        # Check objects
        assert (True if QueueStrategy in settings.QUEUE_STRATEGY.__class__.__bases__ else False),\
            "settings.QUEUE_STRATEGY: object must be inherited from class QueueStrategy"
        assert (True if DistributionStrategy in settings.DISTRIBUTE_STRATEGY.__class__.__bases__ else False),\
            "settings.DISTRIBUTE_STRATEGY: object must be inherited from class DistributionStrategy"
        assert isinstance(settings.EXPORTERS, list), "settings.EXPORTERS: expected list of objects"
        for exporter in settings.EXPORTERS:
            assert (True if MetricsExporter in exporter.__class__.__bases__ else False),\
                "settings.EXPORTERS: Exporters objects must be inherited from class MetricsExporter"
        # print settings
        STREAM.info("Using settings:")
        STREAM.info(" -> LOGLEVEL = %s" % settings.LOGLEVEL)
        STREAM.info(" -> BASE_QUEUE_PATH = %s" % settings.BASE_QUEUE_PATH)
        STREAM.info(" -> QUEUE_IDLE_INTERVAL = %s" % settings.QUEUE_IDLE_INTERVAL)
        STREAM.info(" -> TASK_GROUPS = %s" % [task for task in settings.TASK_GROUPS.values()])
        STREAM.info(" -> QUEUE_STRATEGY = %s" % settings.QUEUE_STRATEGY.__class__.__name__)
        STREAM.info(" -> DISTRIBUTE_STRATEGY = %s" % settings.DISTRIBUTE_STRATEGY.__class__.__name__)
        STREAM.info(" ")
        STREAM.info("Serviced clusters:")
        for cluster, nodes in settings.CLUSTER_NODE_GROUPS.items():
            STREAM.info(" -> %s: nodes(%s)" % (cluster, len(nodes)))

    def _start_exporters(self):
        STREAM.info("Loading metric exporters...")
        if not settings.EXPORTERS:
            return
        for exporter in settings.EXPORTERS:
            try:
                getattr(exporter, "run")
            except AttributeError:
                pass
            else:
                t = Thread(target=exporter.run)
                t.daemon = True
                t.start()
            STREAM.info(" -> loaded: %s" % exporter.__class__.__name__)
        sleep(5)

    def run(self):
        STREAM.info("")
        STREAM.info("******************************")
        STREAM.info("Automation Dispatcher started.")
        STREAM.info("******************************")
        while True:
            LoggerOptions.set_component("Queue")
            task = next(self.queue)
            if task is None:
                STREAM.info("Get task from queue: Queue is empty.")
                STREAM.info("Standby before next queue check: %s sec(s)" % settings.QUEUE_IDLE_INTERVAL)
                sleep(settings.QUEUE_IDLE_INTERVAL)
            else:
                STREAM.info("Get task from queue: %s" % task.uuid)
                LoggerOptions.set_component("Distribution")
                self.distribution.distribute_task(task)


if __name__ == "__main__":
    dispatcher = Dispatcher()
    try:
        dispatcher.run()
    except KeyboardInterrupt:
        STREAM.info("Automation Dispatcher stopped.")
        exit(0)
