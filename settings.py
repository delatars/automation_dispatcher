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
QUEUE_CONTROL_FILE = os.path.join(BASE_QUEUE_PATH, "queue_control.flag")
CLUSTER_NODE_GROUPS = {
    "master": ["node1.test"],
    "openstack": ["node2.test", "node3.test"],
    "openshift": ["node4.test", "node5.test", "node6.test"]
    }


# Objects
from strategies.queue.straight_priority_strategy import PriorityStrategy
from strategies.distribution.simple_distribution import SimpleStrategy
from monitors.zabbix_monitor import Zabbix
from exporters.prometheus import PrometheusMetrics

# List of metrics exporters objects
EXPORTERS = [PrometheusMetrics(update_interval=10)]
MONITORING_SYSTEM = Zabbix(url="http://testlab-master1.i.drweb.ru/zabbix", user="zabstat", password="zFV3bgeC72hx5Ae7")

QUEUE_STRATEGY = PriorityStrategy()     # Object of task queue strategy
DISTRIBUTE_STRATEGY = SimpleStrategy()  # Object of task distribute strategy
