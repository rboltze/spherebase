# -*- coding: utf-8 -*-

"""
Module Node. A node is the basis for all nodes. Further nodes are derived from Node
"""

from pyrr import quaternion, Quaternion
from sphere_base.utils.serializable import Serializable
from collections import OrderedDict
from sphere_base.node.graphic_node import GraphicNode
from sphere_base.node.socket import Socket
from sphere_base.constants import *
from sphere_base.utils.utils import dump_exception
import numpy as np


class Node(Serializable):
    """
    Class representing a ``Node`` on a ``Sphere``. Each node can represent a person, an object or any entity.
    ``Sphere Nodes`` are sphere_base items like ``Sphere Edges`` and ``Sphere Sockets``.
    """

    GraphicNode_class = GraphicNode
    NodeContent_class = None
    Socket_class = Socket

    def __init__(self, target_sphere, orientation_offset=None,
                 yaw_degrees=0, pitch_degrees=0, node_type: str = "sphere_node"):
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

        self.node_type_name = 'sphere_node'
        self.sphere = target_sphere
        self.config = self.sphere.config
        self.calc = self.sphere.calc
        self.node_disc = self.sphere.map.models.get_model('sphere_node')
        self.circle = self.sphere.map.models.get_model('circle')
        self.ray = self.sphere.map.mouse_ray

        # (angle) of the node on the sphere_base relative to the zero rotation of the sphere_base
        self.pos_orientation_offset = np.array(
            [0.1, 0.1, 0.1, 1.0]) if orientation_offset is None else orientation_offset
        self.yaw_degrees = yaw_degrees
        self.pitch_degrees = pitch_degrees

        self.orientation = None
        self.offset_with_collision_point = None  # difference center node with collision point
        self.mouse_ray_collision_point = None
        self.grNode = None
        self.serialized_detail_scene = None
        self._node_moved = False
        self.xyz = None
        self.collision_object_radius = NODE_DISC_RADIUS

        self.Socket = self.__class__.Socket_class  # initiate later

        self._init_inner_classes()
        self.scale = self.gr_node.scale
        self.img_name = 'icon_question_mark'
        self.img_id = self.gr_node.default_img_id
        self.radius = target_sphere.radius

        self.xyz = self.get_position(self.radius)  # the xyz position of the node on the surface of the sphere
        # get the orientation of the disc pointing away from the center of the sphere_base
        self.orientation = self.get_orientation()  # the normal for the node
        self.cumulative_rotation = self.get_cumulative_rotation(self.pos_orientation_offset, self.sphere.orientation)

        # create a collision object (cylinder) pointing out
        self.collision_object_id = self.ray.create_collision_object(self)
        self.socket = self.Socket(self)

        self.sphere.add_item(self)
        self.sphere.add_item(self.socket)

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

    @staticmethod
    def get_cumulative_rotation(angle1, angle2):
        """
        Helper function returns a quaternion with a cumulative rotation of two rotations

        """

        return quaternion.cross(angle1, quaternion.inverse(angle2))

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
            self.offset_with_collision_point = None
            self.mouse_ray_collision_point = None
        elif not self._node_moved and value:
            # start dragging
            self._node_moved = True
        return self._node_moved

    def drag_to(self, mouse_ray_collision_point=None):
        """
        Dragging the node_disc over the surface of the sphere_base

        The difference between the mouse_ray collision point and the center of the disc is stored at the start of
        the dragging. This difference is applied during the dragging and makes sure that the distance between the
        collision point and the disc remains the same. This is very important when dragging groups of objects. Not
        using this would mean that all objects would collect under the mouse pointer.

        :param mouse_ray_collision_point: collision point of the mouse_ray with the target sphere
        :type mouse_ray_collision_point: ``float``

        """
        q, cp = quaternion, None
        try:

            # first find the angle of the collision point
            cp = self.calc.find_angle(mouse_ray_collision_point, self.sphere.orientation)

            # print(mouse_ray_collision_point, self.sphere.orientation)
            if self.offset_with_collision_point is None:

                # store the difference between the node center and the collision point
                self.offset_with_collision_point = q.cross(self.pos_orientation_offset, q.inverse(cp))

            # Move the node center to the position of the collision point
            self.pos_orientation_offset = cp

            # correct the position of the node with the stored difference with the mouse pointer
            self.pos_orientation_offset = q.cross(self.offset_with_collision_point, self.pos_orientation_offset)

            self.update_position()
            return self.pos_orientation_offset

        except Exception as e:
            print('collision_point', cp)
            print('pos_orientation_offset', self.pos_orientation_offset)
            print('offset_with_collision_point', self.offset_with_collision_point)
            dump_exception(e)

    def get_position(self, radius):
        # cumulative sphere_base rotation with position offset of node
        cumulative_orientation = self.get_cumulative_rotation(self.pos_orientation_offset, self.sphere.orientation)

        # get the position of the node on the sphere
        xyz = self.calc.move_to_position(cumulative_orientation, self.sphere, radius)

        return xyz

    def get_orientation(self):
        # get the orientation of the disc pointing away from the center of the sphere_base
        normal = self.calc.get_item_direction_pointing_outwards(self, self.sphere)
        return normal

    def update_position(self):
        """
        update the position of the node_disc on the sphere_base. Calculate the position and the direction.
        """
        self.xyz = self.get_position(self.radius)
        self.orientation = self.get_orientation()
        self.socket.update_position()

        return self.xyz

    def update_collision_object(self):
        # set the collision object for mouse pointer ray collision
        self.ray.reset_position_collision_object(self)
        self.socket.update_collision_object()

    def update_content(self, texture_id: int, sphere_id: int):
        """
        Updates the content like sphere_icons and images

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
        self.img_id = self.gr_node.on_selected_event(event)

    def set_hovered(self, event: bool):
        """
        Sets all flags and all images and colors to match the new state.
        If the event is 'True' the circle around the ``Node`` will show the 'hovered' color.

        :param event: ``True`` sets the state to 'hovered'
        :type event: ``bool``
        """
        self.img_id = self.gr_node.on_hover_event(event)

    def remove(self, with_edges: bool = True):
        """
        Safely remove this Node. It also removes the socket, the connected edges and the collision object.

        :param with_edges: With edges is the default
        :type with_edges: ``bool``
        """
        self.socket.remove(with_edges)

        self.grNode = None
        self.sphere.map.mouse_ray.delete_collision_object(self)
        self.sphere.remove_item(self)

    def draw(self):
        """
        Renders all the sphere_icons and circles of the node_disc.
        """
        self.socket.draw()
        self.node_disc.draw(self, texture_id=self.img_id, color=self.gr_node.main_image_color, switch=0)
        self.node_disc.draw(self, color=self.gr_node.current_background_color, switch=2)

        self.circle.shader.line_width = self.gr_node.current_border_width
        self.circle.draw(self, scale=self.gr_node.circle_scale, color=self.gr_node.current_border_color)

    def set_img(self, img_name):
        self.img_name = img_name
        self.img_id = self.gr_node.set_icon_by_name(img_name)

    def serialize(self):
        socket = self.socket.serialize()
        return OrderedDict([
            ('id', self.id),
            ('node_type_name', self.node_type_name),
            ('img_name', self.img_name),
            ('orientation_offset', self.pos_orientation_offset.tolist()),
            ('scene', self.serialized_detail_scene),
            ('socket_id', self.socket.id),
            ('socket', socket)
        ])

    def deserialize(self, data: dict, hashmap: dict = None, restore_id: bool = True) -> bool:
        """
        copy, cut paste also uses this. When pasting restore_id is false and new ids are created.
        """

        # hashmap = {} if hashmap is None else hashmap

        if restore_id:
            self.id = data['id']
            self.socket.id = data['socket_id']

        self.node_type_name = data['node_type_name']
        self.pos_orientation_offset = np.array(data['orientation_offset'])
        self.serialized_detail_scene = data['scene']

        if 'img_name' in data:
            self.img_name = data['img_name']
            self.img_id = self.config.get_img_id(self.img_name)
            self.set_img(self.img_name)
        self.update_position()
        self.update_collision_object()

        return True
