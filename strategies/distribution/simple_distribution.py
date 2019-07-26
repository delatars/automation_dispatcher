# -*- coding: utf-8 -*-
import os
from time import sleep

import settings
from strategies.distribution.distribution_template import DistributionStrategy
from loaders.clusters import ClustersLoader
from logger import STREAM


class SimpleStrategy(DistributionStrategy):
    # Thresholds, upon which the new tasks will be put on a "pause".
    CLUSTERS_WORKLOAD_THRESHOLDS = {
        "master":
            {
                "cpu": 30,
                "memory": 30,
                "iowait": 7,
            },
        "openshift":
            {
                "cpu": 30,
                "memory": 30,
                "iowait": 5,
            },
        "openstack":
            {
                "cpu": 30,
                "memory": 30,
                "iowait": 5,
            }

    }
    UPDATE_INTERVAL = 120
    REDISTRIBUTE_INTERVAL = UPDATE_INTERVAL//4
    QUEUE_CONTROL_FILE = settings.QUEUE_CONTROL_FILE

    def __init__(self):
        self.loader = ClustersLoader()

    def distribute_task(self, task):
        STREAM.info("Distribute task: %s" % task.uuid)
        while True:
            STREAM.info("Check manual mode")
            if not self.get_manual_queue_control_status():
                if task.group == "system":
                    STREAM.info("Task: %s : system task" % task.uuid)
                    self.run_task(task)
                else:
                    STREAM.info("Standby before retry to distribute task: %s sec(s)" % self.REDISTRIBUTE_INTERVAL)
                    sleep(self.REDISTRIBUTE_INTERVAL)
                    continue

            STREAM.info("Check cluster's status")
            if task.resource == "vm":
                STREAM.info("Task: %s : Requires resources: %s" % (task.uuid, task.resource))
                if self.get_cluster_status("master") and\
                        self.get_cluster_status("openstack"):
                    self.run_task(task)
                    return
                else:
                    STREAM.info("Standby before retry to distribute task: %s sec(s)" % self.REDISTRIBUTE_INTERVAL)
                    sleep(self.REDISTRIBUTE_INTERVAL)
                    continue
            elif task.resource == "con":
                STREAM.info("Task: %s : Requires resources: %s" % (task.uuid, task.resource))
                if self.get_cluster_status("master") and\
                        self.get_cluster_status("openshift"):
                    self.run_task(task)
                    return
                else:
                    STREAM.info("Standby before retry to distribute task: %s sec(s)" % self.REDISTRIBUTE_INTERVAL)
                    sleep(self.REDISTRIBUTE_INTERVAL)
                    continue
            else:
                STREAM.info("Task: %s : Requires resources: %s" % (task.uuid, task.resource))
                if self.get_cluster_status("master") and\
                        self.get_cluster_status("openstack") and\
                        self.get_cluster_status("openshift"):
                    self.run_task(task)
                    return
                else:
                    STREAM.info("Standby before retry to distribute task: %s sec(s)" % self.REDISTRIBUTE_INTERVAL)
                    sleep(self.REDISTRIBUTE_INTERVAL)
                    continue

    def get_manual_queue_control_status(self):
        STREAM.debug("Check manual queue control flag: %s" % self.QUEUE_CONTROL_FILE)
        if os.path.isfile(self.QUEUE_CONTROL_FILE):
            with open(self.QUEUE_CONTROL_FILE, "r") as f:
                queue_control_status = f.read().rstrip()
        else:
            queue_control_status = "start"
        if queue_control_status == "start":
            STREAM.info("-> Manual control: distribution is: ON")
            return True
        else:
            STREAM.warning("-> Manual control: distribution is: OFF")
            STREAM.warning("-> Only system tasks wiil be distributed.")
            return False

    def get_cluster_status(self, cluster):
        STREAM.debug("Check cluster status: %s" % cluster)
        try:
            cluster_metrics = getattr(self.loader, cluster)
        except AttributeError:
            STREAM.error("Cluster Error: cluster %s not in group: CLUSTER_NODE_GROUPS" % cluster)
            return
        cpu = cluster_metrics.cpu
        memory = cluster_metrics.memory
        iowait = cluster_metrics.iowait
        STREAM.debug("Cluster: %s -> CPU:%s -> MEMORY:%s -> IOWAIT:%s" % (cluster, cpu,  memory, iowait))
        if cpu > self.CLUSTERS_WORKLOAD_THRESHOLDS[cluster]["cpu"] or \
                memory < self.CLUSTERS_WORKLOAD_THRESHOLDS[cluster]["memory"] or \
                iowait > self.CLUSTERS_WORKLOAD_THRESHOLDS[cluster]["iowait"]:
            STREAM.warning("Cluster: %s -> CPU:%s -> MEMORY:%s -> IOWAIT:%s" % (cluster, cpu,  memory, iowait))
            STREAM.warning("Cluster: %s: Thresholds exceed, not ready to get tasks" % cluster)
            return False
        else:
            STREAM.info("-> Cluster %s: Ready to get tasks" % cluster)
            return True

    def run_task(self, task):
        task.push_to_running()
        STREAM.info("Standby before distribute next task: %s sec(s)" % self.UPDATE_INTERVAL)
        sleep(self.UPDATE_INTERVAL)


if __name__ == '__main__':
    pass
