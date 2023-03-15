# -*- coding: utf-8 -*-


from sphere_base.sphere_overlay.sov_sphere_node_base import SphereNodeBase
from sphere_base.sphere_universe_base.suv_graphic_node import GraphicNode
from sphere_base.sphere_overlay.sov_conf import *


class PersonGraphicNode(GraphicNode):
    def __init__(self, node):
        super().__init__(node)

    def init_assets(self):
        super().init_assets()
        self.set_icon_by_name("man_icon")
        self.set_background_color([0.07, 0.0, 0.4, 0.1])

@register_node(OP_SPHERE_NODE_PERSON, SPHERE_NODE_EDITOR)
class PersonSphereNode(SphereNodeBase):
    GraphicNode_class = PersonGraphicNode
    op_code = OP_SPHERE_NODE_PERSON
    op_title = "PersonNode"

    def __init__(self, target_sphere, orientation_offset=None):
        super().__init__(target_sphere, orientation_offset)
        self.node_type_name = "person_sphere_node"
        self.gender = None


