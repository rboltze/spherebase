# -*- coding: utf-8 -*-

from sphere_base.edge.surface_edge import SurfaceEdge
from examples.example_sphere.sphere_overlay.sov_conf import *

@register_node(OP_SPHERE_EDGE, SPHERE_NODE_EDITOR)
class SphereEdge(SurfaceEdge):
    op_code = OP_SPHERE_EDGE
    op_title = "EdgeNode"

    def __init__(self, parent, socket_start=None, socket_end=None):
        super().__init__(parent, socket_start, socket_end)
        # self.node_type_name = "sphere_edge"



