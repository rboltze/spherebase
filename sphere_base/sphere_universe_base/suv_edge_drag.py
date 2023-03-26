# -*- coding: utf-8 -*-

"""
Edge_drag module. contains the EdgeDraw class which is responsible for drawing a new edge.

"""

from pyrr import quaternion
from sphere_base.sphere_universe_base.suv_socket import *
from sphere_base.sphere_universe_base.suv_graphic_edge import GraphicEdge
from sphere_base.shader.uv_sphere_shader import SphereShader


class EdgeDrag:

    GraphicsEdge_class = GraphicEdge
    Shader_class = SphereShader

    """
    This class takes care of dragging a new edge. SLERP-ing Quaternions to determine the angle 
    with the center of the sphere_base.
    
    """

    def __init__(self, sphere):
        """
        Constructor of the edge dragg class.

        :param Sphere: This class is instantiated from the :class:`~sphere_iot.uv_sphere.Sphere`
        :type Sphere: :class:`~sphere_iot.uv_sphere.Sphere`

        :Instance Attributes:

        - **gr_edge** - Instance of :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        - **calc** - Instance of :class:`~sphere_iot.uv_calc.UvCalc` from universe

        :Instance Variables:

        - **uv** - reference to :class:`~sphere_iot.uv_universe.Universe`
        - **sphere_base** - reference to :class:`~sphere_iot.uv_sphere.Sphere`
        - **config** - reference to :class:`~sphere_iot.uv_config.UvConfig`
        - **shader** - reference to :class:`~sphere_iot.shader.uv_base_shader.BaseShader`
        - **radius** - radius of the sphere_base this node is on.
        - **start_socket** - reference to :class:`~sphere_iot.uv_socket.Socket`
        - **xyz** - ``Vector`` location of the loose edge end.
        - **pos_orientation_offset** - quaternion position of the edge end relative to the
          zero rotation of the sphere_base.

        : Properties:
            - **dragging** - property flag indicating whether the edge being dragged

        """
        self.sphere = sphere
        self.config = sphere.config
        self._init_variables()

    def _init_variables(self):
        self.uv = self.sphere.uv
        self.shader = self.sphere.shader
        # self.shader = self.__class__.Shader_class(self)

        self.radius = self.sphere.radius
        self.start_socket = None
        self.xyz = None
        self.pos_orientation_offset = None
        self._dragging = False

        self.unit_length = 0.04
        self.pos_array = []

        self.gr_edge = self.__class__.GraphicsEdge_class(self)
        self.calc = UvCalc()

    def _init_start_dragging(self, start_socket: 'Socket'):
        # dragging start point is the start socket
        self.start_socket = start_socket
        self.xyz = start_socket.xyz  # position of the mouse at start
        self.pos_orientation_offset = self.start_socket.node.pos_orientation_offset

    def _stop_dragging(self):
        self._dragging = False
        self.start_socket = None
        self.pos_array = []

    @property
    def dragging(self) -> bool:
        """
        Edge dragging flag

        :getter: Returns current state
        :setter: Sets _dragging value
        :type: ``bool``
        """
        return self._dragging

    @dragging.setter
    def dragging(self, value: bool):
        if not self._dragging and value:
            self._dragging = value

    def drag(self, start_socket: 'socket', x_offset: float, y_offset: float, dragging: bool):
        """
        Dragging an edge

        :param start_socket:
        :type start_socket: :class:`~sphere_iot.uv_socket.Socket`
        :param x_offset: mouse x-offset
        :type x_offset: ``float``
        :param y_offset: mouse y-offset
        :type y_offset: ``float``
        :param dragging: ``True`` when dragging
        :type dragging: ``bool``

        """

        if not dragging:
            self._stop_dragging()
            return
        else:
            self._dragging = True

        if not self.start_socket:
            self._init_start_dragging(start_socket)
            return

        # the location of the point under the mouse pointer
        self.xyz = self.drag_to(x_offset, y_offset)
        self.snap_to_socket()

        # number of points this edge is made off
        n = self.gr_edge.get_number_of_points(self.start_socket.xyz, self.xyz, self.radius, self.unit_length)

        if n > 0:
            step = 1 / n
            self.update_edge(n, step)

    def snap_to_socket(self):
        """
        When an edge end get close to a socket it 'snaps' to the socket.
        
        """
        # check what is under the mouse_pointer
        item_id, item_pos = self.uv.mouse_ray.check_mouse_ray(self.uv.view.mouse_x, self.uv.view.mouse_y)

        # if under the mouse is a node_disc then 'snap' to its socket
        item = self.sphere.get_item_by_id(item_id)

        if item and item.type == "node" and item != self.start_socket.node:
            # snap to socket
            self.xyz = item.socket.xyz
            self.pos_orientation_offset = item.socket.pos_orientation_offset

    def update_edge(self, number_of_elements: int, step: float):
        """
        Update the position of the edge

        :param number_of_elements:
        :type number_of_elements: ``int``
        :param step: size of each step
        :type step: ``float``

        """
        self.pos_array = [[self.xyz[0], self.xyz[1], self.xyz[2]]]  # first point
        for i in range(1, number_of_elements):
            pos_orientation_offset = quaternion.slerp(
                self.pos_orientation_offset, self.start_socket.pos_orientation_offset, step * i)

            # take the position of each point and add to array
            pos = self.gr_edge.get_position(pos_orientation_offset)
            self.pos_array.append([pos[0], pos[1], pos[2]])

    def drag_to(self, pitch_degrees: float, yaw_degrees: float) -> 'Vector3':
        """

        :param pitch_degrees: horizontal rotation
        :param yaw_degrees: vertical yaw
        :returns: xyz 'Vector3'
        """
        # get the new position orientation offset angle based on pitch and yaw
        self.pos_orientation_offset = self.calc.get_pos_orientation_offset(pitch_degrees, yaw_degrees,
                                                                           self.pos_orientation_offset)
        return self.gr_edge.get_position(self.pos_orientation_offset)

    def drag_to_mouse_ray(self):
        # The ray test of return object gives the hit position. This is the position in 3d space where the mouse
        # ray intersects with the first object.
        pass

    def draw(self):
        """
        Drawing the edge with dotted lines.

        """
        if self._dragging:
            self.shader.draw_edge(self.pos_array, width=3, color=[0, 0, 0, 1], dotted=True)
