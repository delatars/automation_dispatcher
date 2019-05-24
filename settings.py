# -*- coding: utf-8 -*-
import os
import logging


# Dispatcher
LOGLEVEL = logging.INFO
QUEUE_IDLE_INTERVAL = 10
TASK_GROUPS = {
        "g": "guest",
        "s": "system"
    }
BASE_QUEUE_PATH = os.getcwd()
CLUSTER_NODE_GROUPS = {
    "master": ["node1.test"],
    "openstack": ["node2.test", "node3.test"],
    "openshift": ["node4.test", "node5.test", "node6.test"]
    }

# Zabbix
ZABBIX_SERVER = "http://localhost/zabbix"
ZABBIX_USERNAME = "Admin"
ZABBIX_PASSWORD = "zabbix"


# Objects
from strategies.queue.straight_priority_strategy import PriorityStrategy
from strategies.distribution.simple_distribution import SimpleStrategy
from exporters.prometheus import PrometheusMetrics

# List of metrics exporters objects
EXPORTERS = [PrometheusMetrics(update_interval=10)]

QUEUE_STRATEGY = PriorityStrategy()     # Object of task queue strategy
DISTRIBUTE_STRATEGY = SimpleStrategy()  # Object of task distribute strategy
