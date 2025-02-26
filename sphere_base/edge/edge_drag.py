# -*- coding: utf-8 -*-

"""
Edge_drag module. contains the EdgeDraw class which is responsible for drawing a new edge.

"""

from pyrr import quaternion
from sphere_base.node.socket import *
from sphere_base.edge.graphic_edge import GraphicEdge
from sphere_base.shader.sphere_shader import SphereShader
from sphere_base.model.model import Model
from sphere_base.utils.utils import dump_exception


class EdgeDrag:

    GraphicsEdge_class = GraphicEdge
    Shader_class = SphereShader

    """
    This class takes care of dragging a new edge. SLERP-ing Quaternions to determine the angle 
    with the center of the sphere_base.
    
    """

    def __init__(self, sphere):

        self.sphere = sphere
        self.config = sphere.config

        self.map = self.sphere.map

        self.radius = self.sphere.radius
        self.start_socket = None
        self.xyz = None
        self.pos_orientation_offset = None
        self._dragging = False

        self.unit_length = 0.04
        self.pos_array = []

        self.gr_edge = self.__class__.GraphicsEdge_class(self)
        self.model = self.map.models.get_model('drag_edge')
        self.calc = Calc()

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
        return self._dragging

    @dragging.setter
    def dragging(self, value: bool):
        if not self._dragging and value:
            self._dragging = value

    def drag(self, start_socket, dragging: bool, mouse_ray_collision_point=None):
        if not dragging:
            self._stop_dragging()
            return
        else:
            self._dragging = True

        if not self.start_socket:
            self._init_start_dragging(start_socket)
            return

        # we recalculate the xyz from the angles as there is a discrepancy with the collision point
        self.xyz = self.drag_to(mouse_ray_collision_point)

        # self.xyz = Vector3(mouse_ray_collision_point)  # we could use this if there would have been no difference
        self.snap_to_socket()

        # number of points this edge is made off
        n = self.gr_edge.count_vertices(self.start_socket.xyz, self.xyz, self.radius, self.unit_length)

        if n:
            step = 1 / n
            self.update_edge(n, step)

    def snap_to_socket(self):
        """
        When an edge end get close to a socket it 'snaps' to the socket.
        
        """
        # check what is under the mouse_pointer
        item_id, item_pos = self.map.mouse_ray.check_mouse_ray(self.map.map_widget.mouse_x, self.map.map_widget.mouse_y)

        # if under the mouse is a node_disc then 'snap' to its socket
        item = self.sphere.get_item_by_id(item_id)

        if item and item.type == "sphere_node" and item != self.start_socket.node:
            # snap to socket
            self.xyz = item.socket.xyz
            self.pos_orientation_offset = item.socket.pos_orientation_offset

    def update_edge(self, number_of_elements: int, step: float):
        self.pos_array = [[self.xyz[0], self.xyz[1], self.xyz[2]]]  # first point
        for i in range(1, number_of_elements):
            pos_orientation_offset = quaternion.slerp(
                self.pos_orientation_offset, self.start_socket.pos_orientation_offset, step * i)

            # get the position of each point and add to array
            pos = self.gr_edge.get_position(pos_orientation_offset, self.sphere.radius)
            self.pos_array.append([pos[0], pos[1], pos[2]])

    def drag_to(self, mouse_abs_pos):
        self.pos_orientation_offset = self.calc.find_angle(mouse_abs_pos, self.sphere.orientation)
        return self.gr_edge.get_position(self.pos_orientation_offset, self.sphere.radius)

    def draw(self):
        """
        Drawing the edge with dotted lines.

        """
        try:
            if self._dragging:
                self.model.shader.draw_edge(self.pos_array, width=2, color=[0, 0, 0, 1], dotted=True)
        except Exception as e:
            dump_exception(e)
