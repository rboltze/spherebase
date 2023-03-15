# -*- coding: utf-8 -*-

from sphere_base.sphere_overlay.sov_sphere_node_base import SphereNodeBase
from sphere_base.sphere_universe_base.suv_surface_edge import SphereSurfaceEdge
from sphere_base.sphere_overlay.sov_conf import *

@register_node(OP_SPHERE_EDGE, SPHERE_NODE_EDITOR)
class SphereEdge(SphereSurfaceEdge):
    op_code = OP_SPHERE_EDGE
    op_title = "EdgeNode"

    def __init__(self, parent, socket_start=None, socket_end=None):
        super().__init__(parent, socket_start, socket_end)
        self.node_type_name = "sphere_edge"



