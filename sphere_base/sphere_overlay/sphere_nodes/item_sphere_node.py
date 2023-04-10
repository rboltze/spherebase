# -*- coding: utf-8 -*-


from sphere_base.sphere_overlay.sov_sphere_node_base import SphereNodeBase
from sphere_base.node.graphic_node import GraphicNode
from sphere_base.sphere_overlay.sov_conf import *

# GENDER = ["Male", "Female", "LGBT"]


class ItemGraphicNode(GraphicNode):
    def __init__(self, node):
        super().__init__(node)
        self.node_disc_radius = 0.06

    def init_assets(self):
        super().init_assets()
        self.set_icon_by_name("icon_item")
        self.set_background_color([0.17, 0.07, 0.4, 0.05])
        self.scale = [2.0, 2.0, 2.0]
        self.circle_scale = [0.27, 0.30, 0.27]



@register_node(OP_SPHERE_NODE_ITEM, SPHERE_NODE_EDITOR)
class ItemSphereNode(SphereNodeBase):
    GraphicNode_class = ItemGraphicNode
    op_code = OP_SPHERE_NODE_ITEM
    op_title = "ItemNode"

    def __init__(self, target_sphere, orientation_offset=None, yaw_degrees=0, pitch_degrees=0):
        super().__init__(target_sphere, orientation_offset, yaw_degrees, pitch_degrees)
        self.node_type_name = "item_sphere_node"
