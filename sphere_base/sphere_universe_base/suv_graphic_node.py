# -*- coding: utf-8 -*-

"""
Module Graphic Node. The graphics node is used in all nodes and sockets.

"""

from sphere_base.sphere_universe_base.suv_graphic_disc import EditorGraphicDisc


class GraphicNode(EditorGraphicDisc):
    def __init__(self, node):
        """
        Constructor of the ``Editor Graphic Node`` class. Contains graphic elements.

        :param node: reference to any inherited class of :class:`~sphere_iot.uv_node.SphereNode`.
        :type node:  :class:`~sphere_iot.uv_node.SphereNode`

        :Instance Variables:

            - **node** - :class:`~sphere_iot.uv_node.SphereNode`.
            - **scale** - ``Vector3`` for scaling the node.
            - **circle_scale** - ``Vector3`` for scaling the outside circle.
            - **default_img_id** - id of the default image
            - **selected_img** - id of the image when the item is _selected.
            - **hover_img_id** - id of the image when the item is hovered with the mouse pointer.
            - **default_background_color** - ``Vector4``
            - **selected_background_color** - ``Vector4``
            - **hover_background_color** - ``Vector4``
            - **current_background_color** - ``Vector4``

        """
        self.node = node
        super().__init__(self.node)

        # this is used to determine how close an edge can get to the disc
        self.node_disc_radius = 0.08

    def init_assets(self):
        """
        initializing the graphic assets. Can be partially or fully overridden.

        """
        self.scale = [3.0, 3.0, 3.0]
        self.circle_scale = [0.41, 0.44, 0.41]

        img_id = self.node.config.get_img_id("icon_question_mark")
        self.default_img_id = img_id
        self.selected_img = img_id
        self.hover_img_id = img_id
        self.main_image_color = [1.0, 1.0, 1.0, 1.0]  # black image

        self.default_background_color = [0.0, 0.07, 0.4, 0.1]
        self.selected_background_color = [0.0, 0.07, 0.4, 0.1]  # [0.89, 0.15, 0.21, 0.1]
        self.hover_background_color = [0.0, 0.07, 0.4, 0.1]

        self.default_border_color = [0.0, 0.0, 1.0, 0.3]
        self.selected_border_color = [0.9, 0.0, 0.0, 0.4]
        self.hover_border_color = [0.9, 0.0, 0.0, 0.4]

        self.default_border_width = 1
        self.selected_border_width = 2
        self.hover_border_width = 3

        self.current_img_id = self.default_img_id
        self.current_background_color = self.default_background_color
        self.current_border_color = self.default_border_color
        self.current_border_width = self.default_border_width

        self.last_img_id = self.default_img_id





