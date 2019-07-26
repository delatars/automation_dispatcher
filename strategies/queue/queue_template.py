# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class QueueStrategy(metaclass=ABCMeta):

    @abstractmethod
    def __iter__(self) -> object:
        """
        :rtype: object
        """

    @abstractmethod
    def __next__(self) -> object:
        """
        :rtype: object
          Must return task object from loaders.tasks or None if no tasks
        """
        return None


if __name__ == '__main__':
    pass
