# -*- coding: utf-8 -*-

from nodeeditor.node_edge import Edge
from nodeeditor.node_edge_validators import *  # Do not remove this


EDGE_TYPE_DIRECT = 1        #:
EDGE_TYPE_BEZIER = 2        #:
EDGE_TYPE_SQUARE = 3        #:
EDGE_TYPE_DEFAULT = EDGE_TYPE_SQUARE


class SplitEdge(Edge):
    def __init__(self, scene:'Scene', start_socket:'Socket'=None, end_socket:'Socket'=None, edge_type=EDGE_TYPE_DEFAULT):

        super().__init__(scene, start_socket, end_socket, edge_type)
        self.edge_type = EDGE_TYPE_SQUARE


