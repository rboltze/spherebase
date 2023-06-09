# -*- coding: utf-8 -*-

"""
Module Graphic Disc. The graphics disc class is used in all nodes and sockets.

"""


class GraphicDisc:
    def __init__(self, node):
        """
        Constructor of the ``Editor Graphic Disc`` class. Contains graphic elements.

        :param node: reference to  :class:`~sphere_iot.uv_node.Node`.
        :type node:  :class:`~sphere_iot.uv_node.Node`

        :Instance Variables:

            - **node** - :class:`~sphere_iot.uv_node.Node`.
            - **current_img_id** - id of the current active image.
            - **last_img_id** - id of the last active image.
            - **default_img_id** - id of the default image
            - **selected_img_id** - id of the image when the item is _selected.
            - **hover_img_id** - id of the image when the item is hovered with the mouse pointer.
            - **default_background_color** - ``list``
            - **selected_background_color** - ``list``
            - **hover_background_color** - ``list``
            - **current_background_color** - ``list``

        """

        self.node = node
        self._hover = False
        self._selected = False
        self.current_img_id = None
        self.last_img_id = None
        self.default_img_id, self.selected_img_id, self.hover_img_id = None, None, None
        self.current_img_id, self.last_img_id = None, None

        self.scale, self.circle_scale, self.default_img_id, self.selected_img_id = None, None, None, None
        self.hover_img_id, self.main_image_color, self.default_background_color = None, None, None
        self.default_img_name, self.selected_img_name = 'icon_question_mark', 'icon_question_mark'
        self.hover_img_name = 'icon_question_mark'

        self.selected_background_color, self.hover_background_color, self.default_border_color = None, None, None
        self.selected_border_color, self.hover_border_color, self.default_border_width = None, None, None
        self.selected_border_width, self.hover_border_width = None, None

        self.current_img_id = self.default_img_id
        self.current_background_color = self.default_background_color
        self.current_border_color = self.default_border_color
        self.current_border_width = self.default_border_width

        self.last_img_id = self.default_img_id
        self.init_assets()

    def _init_unified_icons(self, img_name, img_id: int) -> int:
        """
        This function sets all sphere_icons the same, independent of its state, therefore
        there is no difference between hovered, _selected and default.

        .. Warning::

            In some cases all sphere_icons should be the same and independent of the state of the item.
            This is not always desired

        """
        self.default_img_name, self.hover_img_name, self.selected_img_name = img_name, img_name, img_name
        self.default_img_id, self.selected_img_id, self.hover_img_id = img_id, img_id, img_id
        self.current_img_id, self.last_img_id = img_id, img_id
        return img_id

    def _init_unified_background_colors(self, background_color: list):
        """
        This function sets all background colours the same, independent of its state, therefore
        there is no difference between hovered, _selected and default.

        .. Warning::

            In some cases all sphere_icons should be the same and independent of the state of the item.
            This is not always desired

        """

        self.default_background_color = background_color
        self.selected_background_color = background_color
        self.hover_background_color = background_color
        self.current_background_color = background_color

    def set_icon_by_name(self, img_name: str) -> int:
        """
        Receives an image name, sets all sphere_icons to that image and returns its id.

        :param img_name: The name of image
        :type img_name: ``str``
        :returns: ``int`` img_id

        """

        img_id = self.node.config.get_img_id(img_name)
        return self._init_unified_icons(img_name, img_id)

    def set_icon_by_id(self, img_id: int) -> int:
        """
        Receives an image id and sets all sphere_icons to that image and returns the same id.

        :param img_id: The id of the image
        :type img_id: ``int``
        :returns: ``int`` img_id

        """

        return self._init_unified_icons(img_id)

    def set_background_color(self, background_color: list):
        """
        :param background_color: Color to use as the background
        :type background_color: ``Vector4``
        :return:
        """
        self._init_unified_background_colors(background_color)

    def init_assets(self):
        """
        Needs to be overridden

        """
        return NotImplemented

        # self.scale = [.5, .5, .5]
        # self.circle_scale = [0.05, 0.05, 0.05]
        # self.default_img_id = self.node.config.get_img_id(self.default_img_name)
        # self.selected_img_id = self.node.config.get_img_id(self.selected_img_id)
        # self.hover_img_id = self.node.config.get_img_id(self.hover_img_name)
        # self.main_image_color = [1.0, 1.0, 1.0, 1.0]  # black image
        #
        # self.default_background_color = [0.0, 0.0, 0.0, 1.0]
        # self.selected_background_color = [0.9, 0.0, 0.0, 0.9]  # [0.89, 0.15, 0.21, 0.1]
        # self.hover_background_color = [0.9, 0.0, 0.0, 0.9]
        #
        # self.default_border_color = [0.0, 0.07, 0.4, 0.0]
        # self.selected_border_color = [0.9, 0.0, 0.0, 0.4]
        # self.hover_border_color = [0.9, 0.0, 0.0, 0.4]
        #
        # self.default_border_width = 1
        # self.selected_border_width = 2
        # self.hover_border_width = 3
        #
        # self.current_img_id = self.default_img_id
        # self.current_background_color = self.default_background_color
        # self.current_border_color = self.default_border_color
        # self.current_border_width = self.default_border_width
        #
        # self.last_img_id = self.default_img_id

    def on_selected_event(self, event: bool) -> int:
        """
        Changing of images and colors when item is _selected.

        :return: ``int`` image_id

        """
        self._selected = event
        if event:
            self.current_img_id = self.selected_img_id
            self.current_background_color = self.selected_background_color
            self.current_border_color = self.selected_border_color
            self.current_border_width = self.selected_border_width
        else:
            self.current_img_id = self.default_img_id
            self.current_background_color = self.default_background_color
            self.current_border_color = self.default_border_color
            self.current_border_width = self.default_border_width
        return self.current_img_id

    def on_hover_event(self, event: bool = False) -> int:
        """
        Changing of images and colors when item is hovered.

        :return: ``int`` image_id

        """

        if self._hover and event:
            # already hovering, don't change anything
            pass

        elif self._hover and not event:
            if self._selected:
                # ending hovering above a _selected node
                self.current_img_id = self.selected_img_id
                self.current_background_color = self.selected_background_color
                self.current_border_color = self.selected_border_color
                self.current_border_width = self.selected_border_width
            else:
                # ending hovering above an unselected node
                self.current_img_id = self.default_img_id
                self.current_background_color = self.default_background_color
                self.current_border_color = self.default_border_color
                self.current_border_width = self.default_border_width
            self._hover = False

        elif event:
            self._hover = True
            self.current_img_id = self.hover_img_id
            self.current_background_color = self.hover_background_color
            self.current_border_color = self.hover_border_color
            self.current_border_width = self.hover_border_width

        return self.current_img_id

    def is_hover(self):
        return self._hover
