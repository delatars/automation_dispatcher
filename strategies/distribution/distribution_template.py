# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class DistributionStrategy(metaclass=ABCMeta):

    @abstractmethod
    def distribute_task(self, task: object):
        """
        Strategy to distribute task to clusters

        :type task: object
            Task from queue

        In this method task must be pushed to running or discarded
            - task.push_to_running()
            - task.discard()
        """


if __name__ == '__main__':
    pass
