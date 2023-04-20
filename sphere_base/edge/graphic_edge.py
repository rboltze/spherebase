# -*- coding: utf-8 -*-

"""
Module Graphic Edge. The graphics edge is used with edges.

"""

from pyrr import quaternion
from sphere_base.calc import Calc
import math


class GraphicEdge:
    """
    Base class for Graphics Edge
    """

    calc_class = Calc

    def __init__(self, parent=None):
        """
        Constructor of the ``Graphic Edge`` class .

        :param parent: reference to  :class:`~sphere_iot.uv_edge.SphereSurfaceEdge` or
        :class:`~sphere_iot.uv_edge_drag.EdgeDrag`.
        :type parent:  :class:`~sphere_iot.uv_edge.SphereSurfaceEdge` or :class:`~sphere_iot.uv_edge_drag.EdgeDrag`.

        :Instance Variables:

            - **edge** - :class:`~sphere_iot.uv_edge.SphereSurfaceEdge` or :class:`~sphere_iot.uv_edge_drag.EdgeDrag`.
            - **sphere_base** - reference of :class:`~sphere_iot.uv_sphere.Sphere`
            - **calc** - instance of :class:`~sphere_iot.uv_calc.UvCalc`

        """
        self.edge = parent
        self.sphere = parent.sphere
        self.calc = self.__class__.calc_class()

        self._selected = False
        self._current_color = None

        self.unit_length = 0.05
        self.color = [0, 0, 0, .5]
        self._hover = False
        self._init_assets()

    def _init_assets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self.default_color = [0, 0, 0, .5]  # black
        self.selected_color = [0.9, 0.0, 0.0, 0.4]
        self.hover_color = [191, 255, 0, 1]

    def count_vertices(self, start_xyz, end_xyz, radius: float, unit_length: float):
        """
        Returns the number of vertices on the edge.

        :param start_xyz: start position
        :type start_xyz: ``Vector3``
        :param end_xyz: end position
        :type end_xyz: ``Vector3``
        :param radius: radius of the sphere_base
        :type radius: ``float``
        :param unit_length: length of each unit
        :type unit_length: ``float``
        :returns: ``int`` number of edge elements

        """
        # shortest distance over the surface of the globe between start socket and edge-end
        length = self.calc.get_distance_on_sphere(end_xyz, start_xyz, radius)
        return int(math.ceil(length / unit_length))

    def get_position(self, pos_orientation_offset, radius=None):
        """
        Returns xyz vector based on degree offset (position orientation offset)

        :param pos_orientation_offset: degree offset from the zero-position of the ``Sphere``.
        :param pos_orientation_offset: ``Quaternion``
        :param radius:
        :returns: ``Vector3`` xyz-position

        """
        cumulative_orientation = self.get_cumulative_rotation(pos_orientation_offset)

        # get the position of the edge vertex on the sphere_base, calculated from the cumulative rotation
        xyz = self.calc.move_to_position(cumulative_orientation, self.sphere)
        return xyz

    def get_cumulative_rotation(self, pos_orientation_offset):
        """
        Returns the cumulative rotation of the pos_orientation_offset with the sphere rotation.

        :param pos_orientation_offset: degree offset from the zero-position of the ``Sphere``.
        :type pos_orientation_offset: ``Quaternion``
        :returns: ``Quaternion`` cumulative offset
        """
        # rotation of the sphere with rotation offset of the pointer rotation
        return quaternion.cross(pos_orientation_offset, quaternion.inverse(self.sphere.orientation))

    def on_selected_event(self, event):
        """
        Changing the color of the edge when selected.

        :returns: ``Vector4`` color

        """
        self._selected = event
        if event:
            self._current_color = self.selected_color
        else:
            self._current_color = self.default_color
        return self._current_color

    def on_hover_event(self, event=False):
        """
        Changing the color of the edge when hovered.

        :returns: ``Vector4`` color

        """
        if self._hover and event:
            return self._current_color

        elif self._hover and not event:
            if self._selected:
                self._current_color = self.selected_color
            else:
                self._current_color = self.default_color
            self._hover = False

        elif event:
            self._hover = True
            self._current_color = self.hover_color

        return self._current_color
