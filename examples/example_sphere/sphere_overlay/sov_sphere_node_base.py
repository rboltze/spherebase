# -*- coding: utf-8 -*-

from sphere_base.node.node import Node
from sphere_base.node.graphic_node import GraphicNode
from examples.example_sphere.sphere_overlay.sov_conf import *


class GraphicSphereNode(GraphicNode):
    """ probably needed to add project specific imaging"""
    def __init__(self, node):
        super().__init__(node)


class SphereNodeBase(Node):
    GraphicNode_class = GraphicSphereNode
    op_code = OP_SPHERE_NODE_BASE

    def __init__(self, target_sphere, orientation_offset=None, yaw_degrees=0, pitch_degrees=0,):
        # self.texture_id = None
        super().__init__(target_sphere, orientation_offset, yaw_degrees, pitch_degrees, "sphere_node")
        self.node_type_name = "sphere_node_base"

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def update_content(self, value, sphere_id):
        """ Each texture (icon, image) has a unique short name. The dictionary node sphere_icons
        contains a translation between a listbox text in the editor content nodes with the image short name
        """
        if self.id != sphere_id:
            return

        if value in DICTIONARY_SPHERE_NODE_ICONS:
            icon_name = DICTIONARY_SPHERE_NODE_ICONS[value]

            # sets all state images (_selected, hovered)
            self.img_id = self.gr_node.set_icon_by_name(icon_name)
