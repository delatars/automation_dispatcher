# -*- coding: utf-8 -*-

import re

import settings
from logger import STREAM



class _Node:
    """ Node object implementation """
    def __init__(self, **kwargs):
        for parameter, value in kwargs.items():
            setattr(self, parameter, value)

    @property
    def cpu(self):
        """ Node cpu load """
        return settings.MONITORING_SYSTEM.get_metric(self.name, "cpu")

    @property
    def memory(self):
        """ Node memory free """
        return settings.MONITORING_SYSTEM.get_metric(self.name, "memory")

    @property
    def iowait(self):
        """ Node iowait load """
        return settings.MONITORING_SYSTEM.get_metric(self.name, "iowait")


class _ClusterProperty:
    """ Cluster object implementation """
    nodes = []

    def __init__(self, nodes):
        self.nodes = nodes

    def count_nodes(self, **kwargs):
        return len(self.filter_nodes(**kwargs))

    def filter_nodes(self, **kwargs):
        """
        Method get filter, and return list of filtered nodes
        Support gt, gte, lt, lte modificators

        Examples:
        >> CLUSTER_NODE_GROUPS = {"openstack": [node1], openshift: [node1, node2]}
        >> loader = ClustersLoader(CLUSTER_NODE_GROUPS)
        >> loader.openshift.filter_nodes(name="node1.test")
            [<__main__._Node object at 0x7efe53071f60>]

        >> loader.openshift.filter_nodes(cpu_gt=5)
        [<__main__._Node object at 0x7f051b505ef0>, <__main__._Node object at 0x7f051b505f28>]

        >> loader.openshift.filter_nodes(memory_lt=20)
        [<__main__._Node object at 0x7efe53071f60>]
        """
        nodes = self.nodes
        for attr, value in kwargs.items():
            if re.match(r".+_(gt|gte|lt|lte)$", attr):
                attr, operation = attr.split("_")
                if operation == "gt":
                    nodes = list(filter(lambda node_obj: getattr(node_obj, attr) > value, nodes))
                elif operation == "gte":
                    nodes = list(filter(lambda node_obj: getattr(node_obj, attr) >= value, nodes))
                elif operation == "lt":
                    nodes = list(filter(lambda node_obj: getattr(node_obj, attr) < value, nodes))
                elif operation == "lte":
                    nodes = list(filter(lambda node_obj: getattr(node_obj, attr) <= value, nodes))
            else:
                nodes = list(filter(lambda t: getattr(t, attr) == value, nodes))
        return nodes

    @property
    def cpu(self):
        """ Cluster avg cpu load """
        cpu = 0
        for node in self.nodes:
            cpu += node.cpu
        avg = cpu / len(self.nodes)
        return avg

    @property
    def memory(self):
        """ Cluster avg memory free """
        memory = 0
        for node in self.nodes:
            memory += node.memory
        avg = memory / len(self.nodes)
        return avg

    @property
    def iowait(self):
        """ Cluster avg iowait load """
        iowait = 0
        for node in self.nodes:
            iowait += node.iowait
        avg = iowait / len(self.nodes)
        return avg


class ClustersLoader:
    """
    Load clusters objects and generates properties
    Properties will be filled dynamicaly based on settings.CLUSTER_NODE_GROUPS

    examples:
    >> CLUSTER_NODE_GROUPS = {"openstack": [node1], openshift: [node1, node2]}
    >> loader = ClustersLoader(CLUSTER_NODE_GROUPS)
    >> loader.openstack
        <__main__._ClusterProperty object at 0x7fee65d4df28>

    >> loader.openstack.nodes
        [<__main__._Node object at 0x7efe53071f60>]

    >> loader.openshift.nodes
        [<__main__._Node object at 0x7f051b505ef0>, <__main__._Node object at 0x7f051b505f28>]

    """

    def __init__(self, clusters_nodes=settings.CLUSTER_NODE_GROUPS):
        for cluster, nodes in clusters_nodes.items():
            prop = self._make_property(nodes)
            setattr(self, cluster, prop)

    def _load_nodes(self, nodes):
        NODES = []
        for node in nodes:
            NODES.append(
                _Node(
                    name=node
                )
            )
        return NODES

    def _make_property(self, nodes):
        nodes = self._load_nodes(nodes)
        return _ClusterProperty(nodes)


if __name__ == '__main__':
    loader = ClustersLoader()

