# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class MetricsExporter(metaclass=ABCMeta):

    @abstractmethod
    def run(self):
        """
        entrypoint to start exporter.
        exporters will runs in separate threads.
        """


if __name__ == '__main__':
    pass
