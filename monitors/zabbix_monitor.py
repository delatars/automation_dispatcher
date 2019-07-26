# -*- coding: utf-8 -*-
import json
from zabbix.api import ZabbixAPI

from .monitor_template import MonitorConnector
from logger import STREAM


class Zabbix(MonitorConnector):

    def __init__(self, url, user, password):
        try:
            self.server = ZabbixAPI(url=url, user=user, password=password)
        except Exception as error:
            STREAM.error("Cannot establish Zabbix session: {}".format(error))
            exit(1)

    def _get_host(self, hostname):
        host = self.server.do_request("host.get", {
            "output": "extend",
            "filter": {
                "host": hostname,
                "status": 0
            }
        })
        if host["result"]:
            return host
        else:
            STREAM.error("Cannot find specific host: {}".format(hostname))
            return None

    def _get_metric(self, host_id, metric):
        item = self.server.do_request("item.get", {
            "output": "extend",
            "hostids": host_id,
            "search": {
                "key_": metric
            },
        })
        if item["result"]:
            return item
        else:
            STREAM.error("Cannot find specific metric: {}".format(metric))
            return None

    def _get_metric_value(self, metric_id):
        value = self.server.do_request("history.get", {
            "output": "extend",
            "history": 0,
            "itemids": metric_id,
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": 1
        })
        if value["result"]:
            return value
        else:
            STREAM.error("Cannot retrieve value for item: {}".format(value))
            return None

    def get_metric(self, hostname, metric):
        host = self._get_host(hostname)
        if host is None:
            return -1
        # Внутренний ID хоста в Zabbix.
        host_id = host["result"][0]["hostid"]
        # Состояние наблюдаемого хоста в Zabbix. (1 - наблюдается, 2 - не наблюдается).
        host_status = host["result"][0]["available"]

        if host_status == "1":
            metric = self._get_metric(host_id, metric)
            if metric is None:
                return -1
            else:
                metric_id = metric["result"][0]["itemid"]
                metric_value = self._get_metric_value(metric_id)
                if metric_value is None:
                    return -1
                else:
                    return json.loads(metric_value["result"][0]["value"])
        else:
            return -1


if __name__ == '__main__':
    pass