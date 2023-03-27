# -*- coding: utf-8 -*-

"""
Module Node. A node is the basis for all nodes. Further nodes are derived from SphereNode
"""

from pyrr import quaternion
from sphere_base.serializable import Serializable
from collections import OrderedDict
from sphere_base.sphere_universe_base.suv_graphic_node import GraphicNode
from sphere_base.sphere_universe_base.suv_socket import Socket
from sphere_base.constants import *
# from sphere_iot.uv_calc import UvCalc
import numpy as np


class SphereNode(Serializable):
    """
    Class representing a ``Node`` on a ``Sphere``. Each node can represent a person, an object or any entity.
    ``Sphere Nodes`` are sphere_base items like ``Sphere Edges`` and ``Sphere Sockets``.
    """

    GraphicNode_class = GraphicNode
    NodeContent_class = None
    Socket_class = Socket

    def __init__(self, target_sphere: 'sphere_base', orientation_offset: 'quaternion' = None, node_type: str = "node"):
        """
        Constructor of the ``Node`` class. Creates a node and calculates where to place it on the sphere_base.
        Needs to be overridden in the implementation to allow for other type of nodes.

        :param target_sphere: The :class:`~sphere_iot.uv_sphere.Sphere` the ``node`` is on.
        :type target_sphere:  :class:`~sphere_iot.uv_sphere.Sphere`
        :param orientation_offset: Quaternion representing the offset angle with the 0 position of
         the ``sphere_base``
        :type orientation_offset: ``Quaternion``
        :param node_type: The type of the node to create
        :type node_type: ``str``

        :Instance Attributes:

            - **sphere_base** - Instance of :class:`~sphere_iot.uv_sphere.Sphere`
            - **socket** - Instance of :class:`~sphere_iot.uv_socket.Socket`
            - **gr_node** - Instance of :class:`~sphere_iot.uv_graphic_node.GraphicNode`
            - **config** - Instance of :class:`~sphere_iot.uv_config.UvConfig`
            - **calc** - Instance of :class:`~sphere_iot.uv_calc.UvCalc`
            - **node_disc** - Instance of :class:`~sphere_iot.uv_models.Model`
            - **circle** - Instance of :class:`~sphere_iot.uv_models.Model`
            - **shader** - Instance of :class:`~sphere_iot.shader.uv_node_shader.NodeShader`

        :Instance Variables:

            - **radius** - radius of the sphere_base this node is on.
            - **collision_object_id** - id of the collision cylinder pointing out.
            - **collision_object_radius** - radius of the node disc for pybullet collision object.
            - **pos_orientation_offset** - quaternion position of the node relative to the zero rotation of the
              sphere_base.
            - **orientation** - quaternion with the orientation of the disc pointing away from the center of the
              sphere_base.
            - **scale** - scaling the node with the gr_node.scale value.
            - **texture_id** - ``int`` id of the current texture, image or icon applied to the node disc.
            - **serialized_detail_scene** - contains the ``json`` data of the detail node editor for this node.
            - **xyz** - ``Vector`` location of the ``node``.

        """

        super().__init__(node_type)
        self.node_type_name = "node"
        self.sphere = target_sphere
        self.config = self.sphere.config
        self.calc = self.sphere.calc
        self.node_disc = self.sphere.uv.models.get_model('node')
        self.circle = self.sphere.uv.models.get_model('circle')

        self.Socket = self.__class__.Socket_class  # initiate later

        self._init_inner_classes()
        self._init_variables()
        self._init_flags()

        self.collision_object_radius = NODE_DISC_RADIUS

        # radius of the node to the center of the sphere_base. node can hover above surface of sphere_base
        self.radius = target_sphere.radius - 0.01

        # position_orientation (angle) of the node on the sphere_base relative to the zero rotation of the sphere_base
        self.pos_orientation_offset = np.array(
            [0.1, 0.1, 0.1, 1.0]) if orientation_offset is None else orientation_offset

        # cumulative sphere_base rotation with position offset of node
        cumulative_orientation = self.get_cumulative_rotation()
        self.xyz = self.calc.move_to_position(cumulative_orientation, self.sphere, self.radius)

        # get the orientation of the disc pointing away from the center of the sphere_base
        self.orientation = self.calc.get_item_direction_pointing_outwards(self, self.sphere)

        # create a collision object (cylinder) pointing out
        self.collision_object_id = self.sphere.uv.mouse_ray.create_collision_object(self)
        self.socket = self.Socket(self)

        self.sphere.add_item(self)
        self.sphere.add_item(self.socket)

    def _init_variables(self):
        self.scale = self.gr_node.scale
        self.texture_id = self.gr_node.default_img_id
        self.orientation = None

        self.serialized_detail_scene = None

    def _init_flags(self):
        self._node_moved = False

    def _init_inner_classes(self):
        """
        Sets up graphic node and content class
        """
        node_content_class = self.get_node_content_class()
        graphics_node_class = self.get_graphic_node_class()
        if node_content_class:
            self.content = node_content_class(self)
        if graphics_node_class:
            self.gr_node = graphics_node_class(self)

    def get_node_content_class(self):
        """
        Helper function returns class representing content.
        """
        return self.__class__.NodeContent_class

    def get_graphic_node_class(self):
        """
        Helper function returns class representing GraphicNode.
        """
        return self.__class__.GraphicNode_class

    def get_cumulative_rotation(self):
        """
        Helper function returns a quaternion with a cumulative rotation of both the rotation
        offset of the node with the rotation of the sphere_base.
        """

        return quaternion.cross(self.pos_orientation_offset, quaternion.inverse(self.sphere.orientation))

    def is_dragging(self, value: bool = False):
        """
        Returns the status of the _node_moved flag
        :return: ``bool``
        """
        if self._node_moved == value:
            # keep doing what you are doing
            return value
        elif self._node_moved and not value:
            # end dragging
            self._node_moved = False
            self.sphere.history.store_history("node moved", True)
        elif not self._node_moved and value:
            # start dragging
            self._node_moved = True
        return self._node_moved

    def drag_to(self, pitch_degrees, roll_degrees):
        """
        Dragging the node_disc over the surface of the sphere_base

        :param pitch_degrees: vertical degrees over the x as (while roll degrees is 0) in euler degrees
        :type pitch_degrees: ``float``
        :param roll_degrees: horizontal degrees following the equator in euler degrees
        :type roll_degrees: ``float``

        """

        # get the new position orientation offset angle based on pitch and roll
        self.pos_orientation_offset = self.calc.get_pos_orientation_offset(pitch_degrees, roll_degrees,
                                                                           self.pos_orientation_offset)

        self.update_position()

    def update_position(self):
        """
        update the position of the node_disc on the sphere_base. Calculate the position and the direction.
        also update the position of the collision object for use with the mouse pointer ray.
        """
        # update the position of the node_disc on the sphere_base
        cumulative_orientation = self.get_cumulative_rotation()

        # get the position of the node on the sphere_base
        self.xyz = self.calc.move_to_position(cumulative_orientation, self.sphere, self.radius)

        # get the orientation of the disc pointing away from the center of the sphere_base
        self.orientation = self.calc.get_item_direction_pointing_outwards(self, self.sphere)

        # set the collision object for mouse pointer ray collision
        self.sphere.uv.mouse_ray.reset_position_collision_object(self)

        self.socket.update_position()

    def update_content(self, texture_id: int, sphere_id: int):
        """
        Updates the content like icons and images

        :param texture_id: new texture, image or icon
        :type texture_id: ``int``
        :param sphere_id: current target_sphere
        :type sphere_id:  ``int``
        """

        # needs to be overridden
        pass

    def on_selected_event(self, event: bool):
        """
        Sets all flags and all images and colors to match the new state.
        If the event is 'True' the circle around the node will show the '_selected' color.

        :param event: ``True`` sets the state to '_selected'
        :type event: ``bool``
        """
        self.texture_id = self.gr_node.on_selected_event(event)

    def set_hovered(self, event: bool):
        """
        Sets all flags and all images and colors to match the new state.
        If the event is 'True' the circle around the ``Node`` will show the 'hovered' color.

        :param event: ``True`` sets the state to 'hovered'
        :type event: ``bool``
        """
        self.texture_id = self.gr_node.on_hover_event(event)

    def remove(self, with_edges: bool = True):
        """
        Safely remove this Node. It also removes the socket, the connected edges and the collision object.

        :param with_edges: With edges is the default
        :type with_edges: ``bool``
        """
        self.socket.remove(with_edges)

        self.grNode = None
        self.sphere.uv.mouse_ray.delete_collision_object(self)
        self.sphere.remove_item(self)

    def draw(self):
        """
        Renders all the icons and circles of the node_disc.
        """
        self.socket.draw()
        self.node_disc.draw(self, texture_id=self.texture_id, color=self.gr_node.main_image_color, switch=0)
        self.node_disc.draw(self, color=self.gr_node.current_background_color, switch=2)

        self.circle.shader.line_width = self.gr_node.current_border_width
        self.circle.draw(self, scale=self.gr_node.circle_scale, color=self.gr_node.current_border_color)

    def serialize(self):
        socket = self.socket.serialize()

        return OrderedDict([
            ('id', self.id),
            ('node_type_name', self.node_type_name),
            ('texture_id', self.texture_id),
            ('orientation_offset', self.pos_orientation_offset.tolist()),
            ('scene', self.serialized_detail_scene),
            ('socket_id', self.socket.id),
            ('socket', socket)

        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        """
        copy, cut paste also uses this. When pasting rtore id is false and new id's are created.
        """
        if restore_id:
            self.id = data['id']
            self.socket.id = data['socket_id']

        self.node_type_name = data['node_type_name']
        self.pos_orientation_offset = np.array(data['orientation_offset'])
        self.serialized_detail_scene = data['scene']
        self.texture_id = data['texture_id']
        self.update_position()

        return True
