# -*- coding: utf-8 -*-
import os
from time import sleep
from prometheus_client import start_http_server, Gauge

import settings
from loaders.tasks import TasksLoader
from loaders.clusters import ClustersLoader
from logger import STREAM, LoggerOptions
from exporters.exporter_template import MetricsExporter
from strategies.distribution.simple_distribution import SimpleStrategy


class PrometheusMetrics(MetricsExporter):

    _INSTANCE = None
    QUEUE_CONTROL_FILE = os.path.join(settings.BASE_QUEUE_PATH, "queue_control.flag")

    def __init__(self, update_interval):
        self.update_interval = update_interval
        self.init_common_metrics()
        self.init_guest_group_metrics()
        self.init_system_group_metrics()
        self.init_unknown_group_metrics()
        self.init_zabbix_metrics()
        self.init_clusters_metrics()

    def init_common_metrics(self):
        # waiting        
        self.common_waiting_guest = Gauge('common_waiting_guest',
                                          'Amount of tasks with "guest" priority in the "waiting" queue')
        self.common_waiting_system = Gauge('common_waiting_system',
                                           'Amount of tasks with "system" priority in the "waiting" queue')
        self.common_waiting_openstack = Gauge('common_waiting_openstack',
                                              'Amount of tasks related to Openstack in the "waiting" queue')
        self.common_waiting_openshift = Gauge('common_waiting_openshift',
                                              'Amount of tasks related to Openshift in the "waiting" queue')
        # running
        self.common_running_count = Gauge('common_running_count', 'Amount of tasks in the "running" queue')
        self.common_running_high = Gauge('common_running_high',
                                         'Amount of tasks with "high" priority in the "running" queue')
        self.common_running_normal = Gauge('common_running_normal',
                                           'Amount of tasks with "normal" priority in the "running" queue')
        self.common_running_low = Gauge('common_running_low',
                                        'Amount of tasks with "low" priority in the "running" queue')
        self.common_running_guest = Gauge('common_running_guest',
                                          'Amount of tasks with "guest" priority in the "running" queue')
        self.common_running_system = Gauge('common_running_system',
                                           'Amount of tasks with "system" priority in the "running" queue')
        self.common_running_openstack = Gauge('common_running_openstack',
                                              'Amount of tasks related to Openstack in the "running" queue')
        self.common_running_openshift = Gauge('common_running_openshift',
                                              'Amount of tasks related to Openshift in the in the "waiting" queue')

    def init_guest_group_metrics(self):
        # waiting
        self.guest_waiting_count = Gauge('guest_waiting_count',
                                         'Amount of Guest group tasks in the "waiting" queue')
        self.guest_waiting_openstack = Gauge('guest_waiting_openstack',
                                             'Amount of Guest group tasks related to Openstack in the "waiting" queue')
        self.guest_waiting_openshift = Gauge('guest_waiting_openshift',
                                             'Amount of Guest group tasks related to Openshift in the "waiting" queue')
        # running
        self.guest_running_count = Gauge('guest_running_count',
                                         'Amount of Guest group tasks in the "running" queue')
        self.guest_running_openstack = Gauge('guest_running_openstack',
                                             'Amount of Guest group tasks related to Openstack in the "running" queue')
        self.guest_running_openshift = Gauge('guest_running_openshift',
                                             'Amount of Guest group tasks related to Openshift in the "running" queue')

    def init_system_group_metrics(self):
        # waiting
        self.system_waiting_count = Gauge('system_waiting_count',
                                          'Amount of System group tasks in the "waiting" queue')
        self.system_waiting_openstack = Gauge('system_waiting_openstack',
                                              'Amount of System group tasks related to Openstack in the "waiting" queue')
        self.system_waiting_openshift = Gauge('system_waiting_openshift',
                                              'Amount of System group tasks related to Openshift in the "waiting" queue')
        # running
        self.system_running_count = Gauge('system_running_count',
                                          'Amount of System group tasks in the "running" queue')
        self.system_running_openstack = Gauge('system_running_openstack',
                                              'Amount of System group tasks related to Openstack in the "running" queue')
        self.system_running_openshift = Gauge('system_running_openshift',
                                              'Amount of System group tasks related to Openshift in the "running" queue')

    def init_unknown_group_metrics(self):
        # waiting
        self.unknown_waiting_count = Gauge('unknown_waiting_count',
                                           'Amount of Unknown group tasks in the "waiting" queue')
        self.unknown_waiting_high = Gauge('unknown_waiting_high',
                                          'Amount of Unknown group tasks with "high" priority in the "waiting" queue')
        self.unknown_waiting_normal = Gauge('unknown_waiting_normal',
                                            'Amount of Unknown group tasks with "normal" priority in the "waiting" queue')
        self.unknown_waiting_low = Gauge('unknown_waiting_low',
                                         'Amount of unknown group tasks with "low" priority in the "waiting" queue')
        self.unknown_waiting_openstack = Gauge('unknown_waiting_openstack',
                                               'Amount of Unknown group tasks related to Openstack in the "waiting" queue')
        self.unknown_waiting_openshift = Gauge('unknown_waiting_openshift',
                                               'Amount of Unknown group tasks related to Openshift in the "waiting" queue')
        # running
        self.unknown_running_count = Gauge('unknown_running_count',
                                           'Amount of Unknown group tasks in the "running" queue')
        self.unknown_running_high = Gauge('unknown_running_high',
                                          'Amount of Unknown group tasks with "high" priority in the "running" queue')
        self.unknown_running_normal = Gauge('unknown_running_normal',
                                            'Amount of Unknown group tasks with "normal" priority in the "running" queue')
        self.unknown_running_low = Gauge('unknown_running_low',
                                         'Amount of unknown group tasks with "low" priority in the "running" queue')
        self.unknown_running_openstack = Gauge('unknown_running_openstack',
                                               'Amount of Unknown group tasks related to Openstack in the "running" queue')
        self.unknown_running_openshift = Gauge('unknown_running_openshift',
                                               'Amount of Unknown group tasks related to Openshift in the "running" queue')

    def init_zabbix_metrics(self):
        self.zabbix_openstack_cpu_usage = Gauge('zabbix_openstack_cpu_usage', 'Openstack CPU usage from Zabbix')
        self.zabbix_openstack_memory_free = Gauge('zabbix_openstack_memory_free', 'Openstack RAM free from Zabbix')
        self.zabbix_openstack_iowait_usage = Gauge('zabbix_openstack_iowait_usage', 'Openstack IO usage from Zabbix')

        self.zabbix_openshift_cpu_usage = Gauge('zabbix_openshift_cpu_usage', 'Openshift CPU usage from Zabbix')
        self.zabbix_openshift_memory_free = Gauge('zabbix_openshift_memory_free', 'Openshift RAM free from Zabbix')
        self.zabbix_openshift_iowait_usage = Gauge('zabbix_openshift_iowait_usage', 'Openshift IO usage from Zabbix')


    def init_clusters_metrics(self):
        self.common_queue_control = Gauge('common_queue_control',
                                          'State of the queue control. "0" - unpaused, "1" - paused')
        self.common_master_status = Gauge('common_master_status',
                                          'Status of the Master cluster. "0" - accepts tasks, '
                                          '"1" - doesn\'t accept tasks')
        self.common_openstack_status = Gauge('common_openstack_status',
                                             'Status of the Openstack cluster. "0" - accepts tasks, '
                                             '"1" - doesn\'t accept tasks')
        self.common_openshift_status = Gauge('common_openshift_status',
                                             'Status of the Openshift cluster. "0" - accepts tasks, '
                                             '"1" - doesn\'t accept tasks')

    def get_cluster_status(self, cluster, thresholds):
        if cluster.cpu > thresholds["cpu"] or \
                cluster.memory < thresholds["memory"] or \
                cluster.iowait > thresholds["iowait"]:
            return False
        else:
            return True

    def run(self):
        # Включаем HTTP сервер, с которого Prometheus будет забирать метрики.
        port = 8000
        start_http_server(port)
        LoggerOptions.set_component("prometheus")
        STREAM.debug("Started Prometheus http server on port: %s" % port)
        LoggerOptions.switchback_component()

        tasks = TasksLoader()
        cluster = ClustersLoader()
        while True:
            LoggerOptions.set_component("prometheus")

            # Получаем статистику очереди "waiting" и "running".
            waiting = tasks.waiting
            running = tasks.running
            # Получаем статистику кластеров "openshift" и "openstack".
            openshift = cluster.openshift
            openstack = cluster.openstack
            master = cluster.master

            LoggerOptions.switchback_component()

            # --------------------------------------------------------------------------------------------------
            # Обновляем метрики Prometheus очереди "waiting".

            self.common_waiting_guest.set(waiting.count_tasks(group="guest"))
            self.common_waiting_system.set(waiting.count_tasks(group="system"))
            vm_res = waiting.count_tasks(resource="vm")
            con_res = waiting.count_tasks(resource="con")
            all_res = waiting.count_tasks(resource="all")
            vm_res += all_res
            con_res += all_res
            self.common_waiting_openstack.set(vm_res)
            self.common_waiting_openshift.set(con_res)

            self.guest_waiting_count.set(waiting.count_tasks(group="guest"))
            vm_res = waiting.count_tasks(group="guest", resource="vm")
            con_res = waiting.count_tasks(group="guest", resource="con")
            all_res = waiting.count_tasks(group="guest", resource="all")
            vm_res += all_res
            con_res += all_res
            self.guest_waiting_openstack.set(vm_res)
            self.guest_waiting_openshift.set(con_res)

            self.system_waiting_count.set(waiting.count_tasks(group="system"))
            vm_res = waiting.count_tasks(group="system", resource="vm")
            con_res = waiting.count_tasks(group="system", resource="con")
            all_res = waiting.count_tasks(group="system", resource="all")
            vm_res += all_res
            con_res += all_res
            self.system_waiting_openstack.set(vm_res)
            self.system_waiting_openshift.set(con_res)

            self.unknown_waiting_count.set(waiting.count_tasks(group="unknown"))
            self.unknown_waiting_high.set(waiting.count_tasks(group="unknown", priority="high"))
            self.unknown_waiting_normal.set(waiting.count_tasks(group="unknown", priority="normal"))
            self.unknown_waiting_low.set(waiting.count_tasks(group="unknown", priority="low"))
            vm_res = waiting.count_tasks(group="unknown", resource="vm")
            con_res = waiting.count_tasks(group="unknown", resource="con")
            all_res = waiting.count_tasks(group="unknown", resource="all")
            vm_res += all_res
            con_res += all_res
            self.unknown_waiting_openstack.set(vm_res)
            self.unknown_waiting_openshift.set(con_res)

            # --------------------------------------------------------------------------------------------------
            # Обновляем метрики Prometheus очереди "running".

            self.common_running_count.set(running.count_tasks())
            self.common_running_high.set(running.count_tasks(priority="high"))
            self.common_running_normal.set(running.count_tasks(priority="normal"))
            self.common_running_low.set(running.count_tasks(priority="low"))
            self.common_running_guest.set(running.count_tasks(group="guest"))
            self.common_running_system.set(running.count_tasks(group="system"))
            vm_res = running.count_tasks(resource="vm")
            con_res = running.count_tasks(resource="con")
            all_res = running.count_tasks(resource="all")
            vm_res += all_res
            con_res += all_res
            self.common_running_openstack.set(vm_res)
            self.common_running_openshift.set(con_res)

            self.guest_running_count.set(running.count_tasks(group="guest"))
            vm_res = running.count_tasks(group="guest", resource="vm")
            con_res = running.count_tasks(group="guest", resource="con")
            all_res = running.count_tasks(group="guest", resource="all")
            vm_res += all_res
            con_res += all_res
            self.guest_running_openstack.set(vm_res)
            self.guest_running_openshift.set(con_res)

            self.system_running_count.set(running.count_tasks(group="system"))
            vm_res = running.count_tasks(group="system", resource="vm")
            con_res = running.count_tasks(group="system", resource="con")
            all_res = running.count_tasks(group="system", resource="all")
            vm_res += all_res
            con_res += all_res
            self.system_running_openstack.set(vm_res)
            self.system_running_openshift.set(con_res)

            self.unknown_running_count.set(running.count_tasks(group="unknown"))
            self.unknown_running_high.set(running.count_tasks(group="unknown", priority="high"))
            self.unknown_running_normal.set(running.count_tasks(group="unknown", priority="normal"))
            self.unknown_running_low.set(running.count_tasks(group="unknown", priority="low"))
            vm_res = running.count_tasks(group="unknown", resource="vm")
            con_res = running.count_tasks(group="unknown", resource="con")
            all_res = running.count_tasks(group="unknown", resource="all")
            vm_res += all_res
            con_res += all_res
            self.unknown_running_openstack.set(vm_res)
            self.unknown_running_openshift.set(con_res)

            # --------------------------------------------------------------------------------------------------
            # Обновляем метрики Prometheus загрузки кластеров.
            openstack_thresholds = SimpleStrategy.CLUSTERS_WORKLOAD_THRESHOLDS["openstack"]
            openshift_thresholds = SimpleStrategy.CLUSTERS_WORKLOAD_THRESHOLDS["openshift"]
            master_thresholds = SimpleStrategy.CLUSTERS_WORKLOAD_THRESHOLDS["master"]
            if self.get_cluster_status(openstack, openstack_thresholds):
                self.common_openstack_status.set(0)
            else:
                self.common_openstack_status.set(1)
            if self.get_cluster_status(openshift, openshift_thresholds):
                self.common_openshift_status.set(0)
            else:
                self.common_openshift_status.set(1)
            if self.get_cluster_status(master, master_thresholds):
                self.common_master_status.set(0)
            else:
                self.common_master_status.set(1)

            self.zabbix_openstack_cpu_usage.set(openstack.cpu)
            self.zabbix_openstack_memory_free.set(openstack.memory)
            self.zabbix_openstack_iowait_usage.set(openstack.iowait)

            self.zabbix_openshift_cpu_usage.set(openshift.cpu)
            self.zabbix_openshift_memory_free.set(openshift.memory)
            self.zabbix_openshift_iowait_usage.set(openshift.iowait)

            # --------------------------------------------------------------------------------------------------
            # Обновляем метрики ручного управления очередью.
            if os.path.isfile(self.QUEUE_CONTROL_FILE):
                with open(self.QUEUE_CONTROL_FILE, "r") as f:
                    queue_control_status = f.read().rstrip()
            else:
                queue_control_status = "start"
            if queue_control_status == "start":
                self.common_queue_control.set(0)
            else:
                self.common_queue_control.set(1)

            sleep(self.update_interval)


if __name__ == '__main__':
    pass
