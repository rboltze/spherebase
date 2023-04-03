# -*- coding: utf-8 -*-

"""
Module Socket. Each sphere_base node has exactly one socket.
The position of the socket is always is always in the center of the node disc it belongs to
"""


from sphere_base.serializable import Serializable
from sphere_base.node.graphic_socket import GraphicSocket
from sphere_base.calc import Calc
from sphere_base.constants import *
from collections import OrderedDict

DEBUG = False
DEBUG_REMOVE_WARNINGS = False


class Socket(Serializable):
    GraphicSocket_class = GraphicSocket

    """
        Class representing a ``Socket`` in the center of a ``Node``. 
        The position of the socket in the center of the node disc it belongs to. It has the same orientation 
        and position orientation as the disc, the distance to the center of the ``Sphere`` is a bit larger.
    """

    def __init__(self, node):
        """
        Constructor of the node class. Creates a node and calculates where to place it on the sphere_base. Needs to be
        overridden in the implementation to allow for other type of nodes.

        :param node: The ``node`` the ``socket`` belongs to.
        :type node:  :class:`~sphere_iot.uv_node.Node`


        :Instance Attributes:

            - **gr_socket** - Instance of :class:`~sphere_iot.uv_graphic_socket.GraphicSocket`
            - **calc** - Instance of :class:`~sphere_iot.uv_calc.UvCalc`
            - **socket_disc** - Instance of :class:`~sphere_iot.uv_models.Model`
            - **circle** - Instance of :class:`~sphere_iot.uv_models.Model`
            - **shader** - Instance of :class:`~sphere_iot.shader.uv_socket_shader.SocketShader`

        :Instance Variables:

            - **radius** - radius of the sphere_base this node is on.
            - **collision_object_radius** - radius of the socket for pybullet collision object.
            - **collision_object_id** - id of the collision cylinder pointing out.
            - **xyz** - ``Vector`` location of the ``Socket``.
            - **pos_orientation_offset** - copy from quaternion position of the node.
            - **orientation** - quaternion with the orientation of the disc pointing away from the center of
              the sphere_base.
            - **scale** - scaling the node with the gr_socket.scale value.
            - **texture_id** - ``int`` id of the current texture, image or icon applied to the node disc.

        """
        super().__init__('socket')
        self.node = node

        self.socket_disc = self.node.sphere.uv.models.get_model('socket')
        self.circle = self.node.sphere.uv.models.get_model('circle')

        self.gr_socket = self.__class__.GraphicSocket_class(self.node)
        self.calc = Calc()

        self.scale = self.gr_socket.scale
        self.texture_id = self.gr_socket.default_img_id

        self.radius = self.node.radius + 0.001
        self.orientation = self.node.orientation
        self.xyz = self.node.xyz
        self.pos_orientation_offset = self.node.pos_orientation_offset

        self.edges = []
        self.serialized_detail_scene = None

        self.collision_object_radius = SOCKET_RADIUS

        # create a collision object (cylinder) pointing out from the center of the sphere_base
        self.collision_object_id = self.create_collision_object()

        self.update_position()

    def create_collision_object(self) -> int:
        """
        Creating a``pybullet`` collision object in the form of a cylinder with the same size
        as the ``Socket``. The cylinder is pointing out from the center of the ``Sphere``.
        """
        return self.node.sphere.uv.mouse_ray.create_collision_object(self)

    def delete_collision_object(self) -> None:
        """
        Deleting the ``pybullet`` collision object.
        """
        self.node.sphere.uv.mouse_ray.delete_collision_object(self)

    def update_position(self):
        """
        Updating the position of the ``Socket``. The socket is always located in the center of the
        Node Disc. The collision object and the connected edges are also updated.
        """
        cumulative_orientation = self.node.get_cumulative_rotation()
        self.xyz = self.calc.move_to_position(cumulative_orientation, self.node.sphere, self.radius)

        self.orientation = self.node.orientation  # same orientation as the node disc
        self.pos_orientation_offset = self.node.pos_orientation_offset
        self.node.sphere.uv.mouse_ray.reset_position_collision_object(self)
        self.update_connected_edges()

    def update_connected_edges(self):
        """
        Update the connected edges
        """

        # find connected edges
        edges = self.node.sphere.get_edges(self)
        for edge in edges:
            edge.update_position()

    def add_edge(self, edge):
        self.edges.append(edge)

    def remove_edge(self, edge: 'Edge'):
        """
        :param edge: remove an :class:`~sphere_iot.uv_edge.SphereEdge` from the socket.
        :type edge: :class:`~sphere_iot.uv_surface_edge.SphereSurfaceEdge`
        """
        if edge in self.edges:
            self.edges.remove(edge)
        else:
            if DEBUG_REMOVE_WARNINGS:
                print("!W:", "Socket::removeEdge", "wanna remove edge", edge,
                      "from self.edges but it's not in the list!")

    def remove_all_edges(self, silent=False):
        """
        Remove all `Edges` from this `Socket`

        :param silent: if ``True`` remove all edges without notifications.
        :type silent:  ``bool``
        """
        while self.edges:
            edge = self.edges.pop(0)
            if silent:
                edge.remove(silent_for_socket=self)
            else:
                edge.remove()  # just remove all with notifications

    def on_selected_event(self, event: bool):
        """
        Sets all flags and all images and colors to match the new state.
        If the event is 'True' the circle around the ``Socket`` will show the '_selected' color.

        :param event: ``True`` sets the state to '_selected'
        :type event: ``bool``
        """
        self.texture_id = self.gr_socket.on_selected_event(event)

    def set_hovered(self, event: bool):
        """
        Sets all flags and all images and colors to match the new state.
        If the event is 'True' the circle around the ``Node`` will show the 'hovered' color.

        :param event: ``True`` sets the state to 'hovered'
        :type event: ``bool``
        """
        self.texture_id = self.gr_socket.on_hover_event(event)

    def is_dragging(self, value: bool = False):
        """
        Returns the 'dragging status' of the node this socket belongs to.
        """
        return self.node.is_dragging(value)

    def draw(self):
        """
        Renders all the icons and circles of the ``Socket``.
        """
        if self.gr_socket.is_hover():
            self.socket_disc.draw(self, color=self.gr_socket.current_background_color, switch=2)
            self.circle.shader.line_width = self.gr_socket.current_border_width
            self.circle.draw(self, scale=self.gr_socket.circle_scale, color=self.gr_socket.current_border_color)

    def remove(self, with_edges: bool = True):
        """
        Safely remove this socket and all edges connect to it

        :param with_edges: default behaviour is to remove all edges connected.
        :type with_edges: ``bool``
        """

        if with_edges:
            for edge in self.edges.copy():
                edge.remove()
                self.node.sphere.remove_item(edge)

        self.node.sphere.remove_item(self)
        self.delete_collision_object()

    def update_content(self):
        """
        Do not remove. All sphere_base objects needs this method. Needs to be overridden.
        """

        pass

    def serialize(self):
        # not needed - not used, is part of the node
        return OrderedDict([
            ('id', self.id),
            ('type', self.type),
            ('scene', self.serialized_detail_scene),
        ])

    def deserialize(self, data, hashmap=None, restore_id=True):
        # not needed - not used, is included in node
        if restore_id:
            self.id = data['id']

        self.serialized_detail_scene = data['scene']
        return True
