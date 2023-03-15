# -*- coding: utf-8 -*-


from sphere_base.sphere_universe_base.suv_node import SphereNode
from sphere_base.sphere_universe_base.suv_graphic_node import GraphicNode
from sphere_base.sphere_overlay.sov_conf import *


class GraphicSphereNode(GraphicNode):
    """ probably needed to add project specific imaging"""
    def __init__(self, node):
        super().__init__(node)


class SphereNodeBase(SphereNode):
    GraphicNode_class = GraphicSphereNode
    op_code = OP_SPHERE_NODE_BASE

    def __init__(self, target_sphere, orientation_offset=None):
        super().__init__(target_sphere, orientation_offset, "node")
        self.node_type_name = "sphere_node_base"

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        self.gr_node.set_icon_by_id(self.texture_id)
        return res

    def update_content(self, value, sphere_id):
        """ Each texture (icon, image) has a unique short name. The dictionary node icons
        contains a translation between a listbox text in the editor content nodes with the image short name
        """

        if self.id != sphere_id:
            return

        if value in DICTIONARY_SPHERE_NODE_ICONS:
            icon_name = DICTIONARY_SPHERE_NODE_ICONS[value]

            # sets all state images (_selected, hovered)
            self.texture_id = self.gr_node.set_icon_by_name(icon_name)