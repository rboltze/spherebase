# -*- coding: utf-8 -*-

from examples.example_sphere.sphere_overlay.sov_sphere_node_base import SphereNodeBase
from sphere_base.node.graphic_node import GraphicNode
from examples.example_sphere.sphere_overlay.sov_conf import *


class PersonGraphicNode(GraphicNode):
    def __init__(self, node):
        super().__init__(node)
        self.node_disc_radius = 0.08

    def init_assets(self):
        super().init_assets()
        self.set_icon_by_name("icon_man")
        self.set_background_color([0.07, 0.0, 0.4, 0.1])


@register_node(OP_SPHERE_NODE_PERSON, SPHERE_NODE_EDITOR)
class PersonSphereNode(SphereNodeBase):
    GraphicNode_class = PersonGraphicNode
    op_code = OP_SPHERE_NODE_PERSON
    op_title = "PersonNode"

    def __init__(self, target_sphere, orientation_offset=None, yaw_degrees=0, pitch_degrees=0):

        super().__init__(target_sphere, orientation_offset, yaw_degrees, pitch_degrees)
        self.node_type_name = "person_sphere_node"
        self.img_name = "icon_man"
        self.gender = None
