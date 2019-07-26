# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class MonitorConnector(metaclass=ABCMeta):

    @abstractmethod
    def get_metric(self, hostname, metric):
        """
        Get metric value from monitoring system.

        :type hostname: string
            The name of the host for which the value will be returned
        :type   metric: string
            The name of the metric for which the value will be returned

        :return: value
        """
        return -1


if __name__ == '__main__':
    pass
