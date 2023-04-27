# -*- coding: utf-8 -*-

"""
Module Graphic Socket. The graphics socket initializes the graphic assets for the sockets

"""

from sphere_base.node.graphic_disc import GraphicDisc


class GraphicSocket(GraphicDisc):
    def __init__(self, node):
        """
        Constructor of the ``Graphic Socket`` class. Contains graphic elements.

        :param node: reference to any inherited class of :class:`~sphere_iot.uv_node.Node`.
        :type node:  :class:`~sphere_iot.uv_node.Node`

        :Instance Variables:

            - **node** - :class:`~sphere_iot.uv_node.Node`.
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

        super().__init__(node)

    def init_assets(self):
        """
        initializing the graphic assets. Can be partially or fully overridden.

        """
        self.scale = [.7, .7, .7]
        self.circle_scale = [0.05, 0.05, 0.05]
        self.default_img_id = 4
        self.selected_img_id = 2
        self.hover_img_id = 2
        self.main_image_color = [1.0, 1.0, 1.0, 1.0]  # black image

        self.default_background_color = [0.0, 0.0, 0.0, 1.0]
        self.selected_background_color = [0.9, 0.0, 0.0, 0.9]  # [0.89, 0.15, 0.21, 0.1]
        self.hover_background_color = [0.9, 0.0, 0.0, 0.9]

        self.default_border_color = [0.0, 0.07, 0.4, 0.0]
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
