# -*- coding: utf-8 -*-

"""
Module rubber band. The rubber band module contains the rubber band class. It is responsible
for drawing a square selection box. Selecting all the items within the box.
"""

from sphere_base.sphere_universe.graphic_item import GraphicItem

RAY_SEED = 13  # 10 creates 10 x 10 = 100 rays, x creates x**2 rays


class RubberBand(GraphicItem):
    """
    This class represents a rubber band box used for selecting objects on a sphere_base.
    """

    def __init__(self, universe):
        """
        Constructor of the ``Map`` class

        :param universe: reference to the :class:`~sphere_iot.uv_universe.Map`.
        :type universe: :class:`~sphere_iot.uv_universe.Map`.

        :Instance Attributes:

            - **inner_square** - Instance of :class:`~sphere_iot.uv_sphere.Sphere`.
            - **outer_border** - Instance of :class:`~sphere_iot.uv_config.UvConfig`.
            - **shader** - Instance of :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`.

        :Instance Variables:

            - **xyz** - last stored x-position (``float``) of the mouse pointer.
            - **scale** - last stored y-position (``float``) of the mouse pointer.
            - **texture_id** - current x-position (``float``) of the mouse pointer.
            - **mouse_y** - current y-position (``float``) of the mouse pointer.
            - **mouse_offset** - ``float`` used when dragging the sphere_base over its axis.

        .. warning::

            module uses a ´´RAY_SEED´´ constant to determine how many rays are located within the rubber band box.
            10 creates 10 x 10 = 100 rays, x creates x**2 rays.

            More rays mean gives higher density of rays and gives a higher rate of success in selecting edges.
            However, more rays also takes up more resources and may slow down processing.

        """
        super().__init__(self, 'rubber_band_box')
        self.uv = universe

        self.inner_square = self.uv.models.get_model('rubber_band')
        self.outer_border = self.uv.models.get_model('square')  # the border of the rubber band

        self.xyz = None
        self.scale = None
        self.texture_id = 0

        self._dragging = False

        self.orientation = [0., 0., 0., 1.]
        self.color = [0.0, 0.5, 0.7, 0.05]
        self.border_color = [0.0, 0.5, 0.7, 0.5]
        self.mouse_start_point = [0.0, 0.0]
        self.mouse_end_point = [0.0, 0.0]

    def _start_dragging(self, mouse_x, mouse_y):
        self.scale = [0.0, 0.0, 0.0]
        self.mouse_start_point = [mouse_x, mouse_y]
        self.mouse_end_point = self.mouse_start_point
        self._dragging = True

    @property
    def dragging(self) -> bool:
        """
        Setting and getting the 'dragging' flag

        :getter: Returns current state
        :setter: Sets _dragging value
        :type: ``bool``
        """
        return self._dragging

    @dragging.setter
    def dragging(self, value: bool):
        if not self._dragging and value:
            self._dragging = value

    def drag(self, start: bool, mouse_x: float, mouse_y: float):
        """
        Size dragging the rubber band box. Start equals ``True`` when starting a new ``rubber band box``
        and the starting edge position is the current mouse position (mouse_x, mouse_y).

        ``Start`` is ``False`` means we are already dragging a ``rubber band box`` and we just keep dragging the
        mouse position indicates the position of the opposite corner of the box.

        This means that the start attribute determines the meaning of (mouse_x, mouse_y)

        :param start: ``True`` when starting a new box. The mouse position is then the starting edge position.
        :type start: ``bool``
        :param mouse_x: x-position of the mouse
        :type mouse_x: float
        :param mouse_y: y-position of the mouse
        :type mouse_y: float

        """

        if start:
            # mouse position is the position of the start edge of the rubber band box
            self._start_dragging(mouse_x, mouse_y)
        else:
            # current mouse position is the end point
            self.mouse_end_point = [mouse_x, mouse_y]
            self.set_pos()

    def set_pos(self):
        """
        finding the center position of the rubber band box based on the size of the box and the
        starting point. The shader uses ``xyz`` as the center of the square and ``scale`` as the scaling factor

        """
        self.xyz, self.scale = self.get_position_and_scale()

    def get_position_and_scale(self) -> (list, list):
        """
        The size of the rubber band box is determined by the distance between the mouse pointer starting
        position and its current mouse position in a two dimensional plane.

        We calculate the scale factor for the box model which has size 1.

        """
        s, e = self.mouse_start_point, self.mouse_end_point

        # mouse position as a fraction of the screen.
        start = self.uv.mouse_ray.get_ray_clip(s[0], s[1])
        end = self.uv.mouse_ray.get_ray_clip(e[0], e[1])
        diff = end - start

        x = (start[0] + diff[0] * .5)
        y = (start[1] + diff[1] * .5)
        z = 0
        center_position = [x, y, z]

        scaling_factor = [diff[0], diff[1], diff[2]]

        return center_position, scaling_factor

    def get_selection(self) -> list:
        """
        send out a collection of rays through the rubber band box.
        First create an array of "ray starting points" then a second array with ray ending points
        check for unique collisions that are not spheres. Select those items and deselect all other objects.

        Return an array with _selected sphere_base items.

        """

        ray_array_start = []
        ray_array_end = []
        selection = None

        if self._dragging:
            step_x = ((self.mouse_end_point[0] - self.mouse_start_point[0]) / RAY_SEED)
            step_y = ((self.mouse_end_point[1] - self.mouse_start_point[1]) / RAY_SEED)

            for x in range(RAY_SEED):
                for y in range(RAY_SEED):
                    ray_start = self.uv.cam.xyz
                    ray_world = self.uv.mouse_ray.get_mouse_point(self.mouse_start_point[0] + x * step_x,
                                                                  self.mouse_start_point[1] + y * step_y)
                    ray_end = self.uv.cam.xyz + ray_world * 30
                    ray_array_start.append(ray_start)
                    ray_array_end.append(ray_end)

            selection = self.uv.mouse_ray.check_mouse_ray_batch(self.uv.target_sphere, ray_array_start, ray_array_end)

        self._dragging = False

        return selection

    def draw(self):
        """
        Rendering the rubber band box

        """
        if self._dragging:

            self.inner_square.draw(self, texture_id=self.texture_id, color=self.color)
            self.outer_border.draw(self, color=self.border_color)
