# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class DistributionStrategy(metaclass=ABCMeta):

    @abstractmethod
    def distribute_task(self, task: object):
        """
        :type task: object
          task from queue
        """


if __name__ == '__main__':
    pass
