# -*- coding: utf-8 -*-

"""
Module Sphere. Each sphere_base represents a scene object for ``sphere_base items``. these items include nodes,
edges and sockets.
One sphere_base at the time can become the 'target sphere_base'.

"""

from random import *
from sphere_base.serializable import Serializable
from sphere_base.utils import dump_exception
from collections import OrderedDict
from sphere_base.sphere_universe_base.suv_node import SphereNode
from sphere_base.sphere_universe_base.suv_edge_drag import EdgeDrag
from sphere_base.sphere_universe_base.suv_surface_edge import SphereSurfaceEdge
from sphere_base.history import History
from pyrr import quaternion
from math import pi
from sphere_base.calc import UvCalc
import numpy as np
import pyperclip
import json

# for testing purposes a number of nodes can be _selected
NUMBER_OF_TEST_NODES = 0


class Sphere(Serializable):
    """
    Class representing a ``Sphere`` in the IOT ``Universe``. Each sphere_base represents a related group of people and
    or items. These `items` can include persons, entities or objects. They can have a relationship between each other.
    """

    Node_class = SphereNode
    Edge_class = SphereSurfaceEdge
    Calc_class = UvCalc
    Edge_drag_class = EdgeDrag
    History_class = History

    def __init__(self, universe: 'universe', position: list = None, texture_id: int = None, sphere_type='sphere_base'):
        """
        Constructor of the sphere_base class.

        :param universe: reference to the :class:`~sphere_iot.uv_universe.Universe`
        :type universe: :class:`~sphere_iot.uv_universe.Universe`
        :param position: position of the sphere_base in universe
        :type position: ``list`` with x, y, z values
        :param texture_id: number indicating which texture to use for the sphere_base
        :type texture_id: int

        :Instance Attributes:

            - **node** - Instance of :class:`~sphere_iot.uv_node.SphereNode`
            - **edge** - Instance of :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
            - **calc** - Instance of :class:`~sphere_iot.uv_calc.UvCalc`
            - **config** - Instance of :class:`~sphere_iot.uv_config.UvConfig`
            - **edge_drag** - Instance of :class:`~sphere_iot.uv_edge_drag.EdgeDrag`
            - **history** - Instance of :class:`~sphere_iot.uv_history.History`
            - **shader** - Instance of :class:`~sphere_iot.shader.uv_sphere_shader.SphereShader`

        :Instance Variables:

            - **xyz** - position of the center of the sphere_base [x, y, z]
            - **texture_id** - ``int`` id of the current texture applied to the sphere_base
            - **collision_object_id** - ``int`` id of the current 'pybullet' collision object
            - **scale** - scaling used for this model - None
            - **radius** - ``float`` radius of the sphere_base. In this implementation 1.0
            - **orientation** - ``quaternion`` orientation of the sphere_base
            - **selected_item** - First item _selected

        : Properties:
            - **dragging** - property flag indicating whether the sphere_base is being rotated by mouse dragging
            - **has_been_modified** - property flag indicating if the sphere_base has had some changes
        """

        super().__init__(sphere_type)
        self.uv = universe
        self.texture_id = texture_id
        self.config = universe.config

        self._init_flags()
        self._init_variables()
        self._init_listeners()

        self.get_model()

        # instance attributes
        self.Node = self.__class__.Node_class
        self.Edge = self.__class__.Edge_class
        self.calc = self.__class__.Calc_class()
        self.edge_drag = self.__class__.Edge_drag_class(self)
        self.history = self.__class__.History_class(self)

        self.xyz = position if position else ([randint(-25, 25), randint(-25, 25), randint(-25, 25)])
        self.texture_id = texture_id if texture_id or texture_id == 0 else randint(1, 5)

        # self.collision_object_id = self.create_collision_object(self)
        self.collision_object_id = self.uv.mouse_ray.create_collision_object(self)

        # for testing purposes a number of random nodes can be created
        # self.create_test_node(NUMBER_OF_TEST_NODES)

        # add the sphere_base to the universe
        self.uv.add_sphere(self)
        self.history.store_initial_history_stamp()

    def _init_variables(self):
        self.scale = None
        self.index = 0
        self.radius = 1.0
        self.color = [1, 1, 1, 1]
        self.orientation = quaternion.create_from_eulers([0.0, 0.0, 0.0])
        self._hovered_item = None
        self.animation = 0  # rotation speed

        self.selected_item = None
        self.items = []
        self.items_selected = []
        self.items_deselected = []

    def _init_listeners(self):
        self._selection_changed_listeners = []
        self._items_deselected_listeners = []
        self._has_been_modified_listeners = []

    def _init_flags(self):
        self._has_been_modified = False
        self._dragging = False
        self.selected = False

    def get_model(self):
        # likely to be overridden
        self.model = self.uv.models.get_model('sphere_base')

    @property
    def dragging(self) -> bool:
        """
        Something on the sphere_base has been modified. Sets modified value and calls all registered listeners.

        :getter: Returns current state
        :setter: Sets _dragging value
        :type: ``bool``
        """
        return self._dragging

    @dragging.setter
    def dragging(self, value: bool):
        if not self._dragging and value:
            self._dragging = value

    @property
    def has_been_modified(self) -> bool:
        """
        Something on the sphere_base has been modified. Sets modified value and calls all registered listeners.

        :getter: Returns current state
        :setter: Sets _has_been_modified value
        :type: ``bool``
        """
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            # set it now, because we will be reading it soon
            self._has_been_modified = value

            # call all registered listeners
            for callback in self._has_been_modified_listeners:
                callback()
        else:
            self._has_been_modified = value

    def add_has_been_modified_listener(self, callback: 'function'):
        """
        Register callback for 'has been modified' event.
        :param callback: callback function
        """
        self._has_been_modified_listeners.append(callback)

    def add_selection_changed_listener(self, callback: 'function'):
        """
        Register callback for 'selection changed' event.
        :param callback: callback function
        """
        self._selection_changed_listeners.append(callback)

    def add_item_deselected_listener(self, callback: 'function'):
        """
        Register callback for `deselected item` event.
        :param callback: callback function
        """
        self._items_deselected_listeners.append(callback)

    def create_new_node(self, node_type: str = "person", mouse_x: int = 0, mouse_y: int = 0) -> 'node':
        """
        Needs to be overridden.
        Can be used to create any type of node at the mouse pointer.

        :param node_type: can be ``person`` or ``item``
        :type node_type: ``string``
        :param mouse_x: x position of the mouse
        :type mouse_x: ``float``
        :param mouse_y: y position of the mouse
        :type mouse_y: ``float``
        :return: :class:`~sphere_iot.uv_node.SphereNode`
        """
        # calculate the cumulative angle based on the mouse position
        orientation = self.calc_mouse_position_in_angles(mouse_x, mouse_y)

        # create new node at the cumulative angle
        node = self.Node(self, orientation)
        self.history.store_history("node created", True)
        return node

    def on_item_selected(self, items_selected):
        """
        Handles item selection and triggers event `Item _selected`.
        """
        if items_selected:
            for callback in self._selection_changed_listeners:
                callback(self, items_selected)
                self.history.store_history("Selection Changed")

    def on_item_deselected(self, item: 'Node or Edge'):
        """
        Handles item deselection and triggers event `Items deselected`. Not used in the current implementation.

        :param item: Node or Edge
        :type item: :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_surface_edge.SphereSurfaceEdge`
        """
        for callback in self._items_deselected_listeners:
            callback(self, item)
            self.history.store_history("Deselected Everything")

    def get_item_by_id(self, item_id: int) -> 'item':
        """
        Helper function returns an item of type `node` or `edge` based on id.

        :param item_id: The id of the item to be returned
        :type item_id: ``int``
        :return: :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def get_selected_item(self, selected_item_id: int, shift: bool = False):
        """
        Helper function returns an item of type `node` or `edge` based on _selected item id.

        :param selected_item_id: id of the item to return
        :type selected_item_id: ``int``
        :param shift: ``True`` means that the shift is hold down while selecting
        :type shift: ``bool``
        :return: :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        """

        for item in self.items:
            if selected_item_id == item.id:
                self.select_item(item, shift)
                return item
        return None

    def get_socket_edges(self, socket: 'socket') -> list:
        """
        Helper function returns a list of all edges connected to a node socket.

        :param socket: _selected node socket
        :type socket: :class:`~sphere_iot.uv_socket.Socket`
        :return: returns a ``list`` with edges of type :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        """

        edges = []
        for item in self.items:
            if item.type == "edge" and socket in [item.start_socket, item.end_socket]:
                edges.append(item)
        return edges

    def add_item(self, item: 'Node or Edge or Socket'):
        """Add :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge` to the `Sphere`.

        :param item: Node or Edge
        :type item: :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
                    or :class:`~sphere_iot.uv_socket.Socket`
        """

        # adding item to sphere_base
        self.items.append(item)

    def remove_item(self, item: 'Node or Edge or Socket'):
        """Remove :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_edge.SphereEdge` from the target `Sphere`.
        :param item: Node or Edge to remove from this `Sphere`
        :type item: :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_surface_edge.SphereSurfaceEdge` or :class:`~sphere_iot.uv_socket.Socket`

        """
        # removing item from sphere_base
        if item in self.items:
            self.items.remove(item)

    def has_edge(self, start_socket: 'socket', end_socket: 'socket') -> bool:
        """
        Helper function that checks whether an edge with the same start and end socket already exists

        :param start_socket: edge start socket
        :type start_socket: :class:`~sphere_iot.uv_socket.Socket`
        :param end_socket: edge end socket
        :type end_socket: :class:`~sphere_iot.uv_socket.Socket`
        :return: ``True`` or ``False``
        """

        # Could possibly be optimized by not checking all edges on the sphere_base
        for item in self.items:
            if item.type == "edge":
                if item.start_socket in [start_socket, end_socket] and item.end_socket in [start_socket, end_socket]:
                    return True
        return False

    def create_edge(self, end_socket: 'socket') -> 'edge':
        """
        Create an edge between the _selected start socket and the received end socket if it does not already exist.

        :param end_socket: the end socket where the edge has to be drawn to.
        :type end_socket: :class:`~sphere_iot.uv_socket.Socket`
        :return: return :class:`~sphere_iot.uv_edge.SphereSurfaceEdge` or ``None``
        """

        if not self.has_edge(self.start_socket, end_socket):
            edge = self.Edge(self, self.start_socket, end_socket)
            self.history.store_history("edge created", True)
            return edge

        return None

    def get_edges(self, start_socket=None, end_socket=None):
        """
        find the edge that has the given start and end socket.

        :param start_socket: start socket for the edge.
        :type start_socket: :class:`~sphere_iot.uv_socket.Socket`
        :param end_socket: end socket for the edge.
        :type end_socket: :class:`~sphere_iot.uv_socket.Socket`
        :return: return list of edges of type :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`

        .. warning::

           Start and end sockets have no further meaning in this  implementation. There is no significant difference
           between start and end other than the order of where the line is initially drawn from.

           In future implementations there could be a need to indicate the direction of the relationship between parents
           and children or the direction of owner ship that goes from a person to the product.

           This type of order or direction is currently not implemented.

        """

        sockets = [start_socket, end_socket]
        edges = []

        for item in self.items:
            if item.type == "edge":
                if item.start_socket in sockets or item.end_socket in sockets:
                    edges.append(item)
        return edges

    def remove_edges(self, edges: list):
        """
        Remove all edges in the edges list received.

        :param edges: list of edges of type :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        :type edges: ``list``
        """
        for item in edges:
            if item in self.items:
                self.items.remove(item)

    def update_item_positions(self):
        """
        Update the orientation of all items on the sphere_base.

        .. note::

            This method only explicitly instructs nodes to update themselves.
            updating nodes will trickle down, causing the connected node socket and connected edges to update as well.
        """
        # update orientation of all nodes on sphere_base
        for item in self.items:
            if item.type == "node":
                # updating the node trickles down to updating sockets and edges"
                item.update_position()

    def rotate_sphere(self, offset_degrees: int):
        """
        Rotating the sphere_base over the y-axis as per the offset_degrees.

        :param offset_degrees: degrees that the sphere_base rotates over its y-axis
        :type offset_degrees: ``int``
        """

        # rotating the sphere_base over the y-axis
        pitch = (pi / 180 * offset_degrees)
        rotation = quaternion.create_from_eulers([0.0, pitch, 0.0])
        self.orientation = quaternion.cross(self.orientation, rotation)
        self.update_item_positions()

    def calc_mouse_position_in_angles(self, mouse_x: float, mouse_y: float) -> 'quaternion':
        """
        Calculates the angle of the mouse pointer with the center of the target sphere_base. It takes into account the
        distance of the camera with the target sphere_base and the distance of the mouse from the center of the screen.

        Todo: this is not a correct calculation and needs to be revised. The new calculation needs to find the point
              where the mouse_ray hits the sphere. And this pint needs to be calculated in angles.

        :param mouse_x: x-position of the mouse pointer
        :type mouse_x: ``float``
        :param mouse_y: y-position of the mouse pointer
        :type mouse_y: ``float``
        :return: orientation quaternion
        """

        # ratio offset from center
        x_offset = (2.0 * mouse_x) / self.uv.view.view_width - 1.0
        y_offset = 1.0 - (2.0 * mouse_y) / self.uv.view.view_height

        # camera to center of target sphere_base modifier
        m = self.calc.get_distance_modifier(self.uv.cam.distance_to_target)
        p_x = self.calc.get_position_modifier(x_offset, True)
        p_y = self.calc.get_position_modifier(y_offset, False)

        # mouse pointer offset in radians
        mouse_pitch = -(pi / 180 * (x_offset * p_x * m))
        mouse_roll = -(pi / 180 * (y_offset * p_y * m))

        # mouse pointer offset quaternions
        mouse_pitch = quaternion.create_from_eulers([0.0, mouse_pitch, 0.0])
        mouse_roll = quaternion.create_from_eulers([mouse_roll, 0.0, 0.0])

        # camera direction in radians
        pitch, roll = self.uv.cam.get_angles()
        cam_roll = (pi / 180 * (90 - roll))
        cam_pitch = (pi / 180 * (pitch + 90))
        yaw = 0.0  # no yaw

        # camera direction offset quaternions
        camera_pitch = quaternion.create_from_eulers([0.0, cam_pitch, yaw])
        camera_roll = quaternion.create_from_eulers([cam_roll, 0.0, yaw])

        # vertical angles first
        roll = quaternion.cross(mouse_roll, camera_roll)

        # horizontal adjustment
        pitch = quaternion.cross(mouse_pitch, camera_pitch)

        # join all offsets
        orientation = quaternion.cross(roll, pitch)
        orientation = quaternion.cross(orientation, self.orientation)

        # return orientation quaternion
        return orientation

    def drag_items(self, x_offset: float, y_offset: float):
        """
        Dragging all _selected items. The offset is the difference between the current and last stored location
        of the mouse pointer on the screen.

        :param x_offset: x_position offset of the current mouse_position and the last stored mouse position.
        :type x_offset: ``float``
        :param y_offset: y_position offset of the current mouse_position and the last stored mouse position.
        :type y_offset: ``float``
        :return:

        .. note::

           This method uses a distance modifier. The dragging speed depends on the distance
           of the camera to the center of the target sphere_base.

           Only existing nodes need to be dragged, as the position of sockets and edges are
           adjusted automatically. Updating the position of a node trickles down to adjusting the position of the
           center sockets of the _selected nodes and any connected edges.
        """

        # distance modifier
        m = self.calc.get_distance_modifier(self.uv.cam.distance_to_target)

        x_offset *= .02 * m
        y_offset *= .02 * m

        for item in self.items_selected:
            # only drag any nodes in the _selected item list
            if item.type == "node":
                item.drag_to(x_offset, y_offset)
                self.dragging = item.is_dragging(True)

    def drag_edge(self, start_socket: 'socket', x_offset: float, y_offset: float, dragging: bool = True):
        """
        This methods is the start of creating a new edge.
        A new edge is dragged from the start socket and shown as a dashed line.
        This method adds a distance modifier before handing over to the :class:`~sphere_iot.uv_edge_drag.EdgeDrag`

        :param start_socket: starting socket
        :type start_socket: :class:`~sphere_iot.uv_socket.Socket`
        :param x_offset: x_position offset of the current mouse_position and the last stored mouse position.
        :type x_offset: ``float``
        :param y_offset: y_position offset of the current mouse_position and the last stored mouse position.
        :type y_offset:  ``float``
        :param dragging: ``True`` when dragging
        :type dragging: ``bool``
        """
        self.start_socket = start_socket
        m = self.calc.get_distance_modifier(self.uv.cam.distance_to_target) * .02

        x_offset *= m
        y_offset *= m

        self.edge_drag.drag(start_socket, x_offset, y_offset, dragging)

    def select_item(self, item: 'node or edge', shift: bool = False):
        """
        Select an item by clicking on it. Holding shift down while clicking on an item, adds it to the _selected list.
        Sockets cannot be _selected.

        :param item: ``Node`` or ``Edge``
        :type item: :class:`~sphere_iot.uv_node.SphereNode` or :class:`~sphere_iot.uv_surface_edge.SphereSurfaceEdge`
        :param shift: ``bool``, ``True`` when shift is down while clicking on an item
        """

        if shift:
            if item:
                self.items_deselected = []
                if item not in self.items_selected:
                    self.selected_item = item
                    self.items_selected.append(item)
        else:
            if item not in self.items_selected:
                self.items_deselected = self.items_selected
                self.items_selected = []
                if item:
                    self.selected_item = item
                    self.items_selected.append(item)

        for item in self.items_selected:
            item.on_selected_event(True)

        for item in self.items_deselected:
            item.on_selected_event(False)

        self.on_item_selected(self.items_selected)

    def delete_selected_items(self):
        """
        Remove _selected items. If item is node then the socket and the connected edges are also removed.
        """
        for selected_item in self.items_selected:
            for i, item in enumerate(self.items):
                if item.id == selected_item.id:
                    if item.type == "node":
                        # remove node, socket and connected items
                        item.remove(with_edges=True)

                    elif item.type == "edge":
                        self.remove_edges([item])

        self.items_selected = []
        self.on_item_selected(self.items_selected)

    def batch_selected_items(self, item_list=None):
        """
        Select all items in the item_list. These items will be put in the selection list and each item
        will has it _selected flag set.

        :param item_list: list of items to select
        :type item_list: ``list``
        """

        if item_list:
            self.items_deselected = self.items_selected
            self.items_selected = []
            for selected in item_list:
                for item in self.items:
                    if selected == item.id and item.type == 'node':
                        self.select_item(item, True)
                    if selected == item.id and item.type == 'edge':
                        self.select_item(item, True)

    def check_for_hover(self, mouse_x, mouse_y):
        """
        When the camera is close to the sphere_base hover checking is activated. If the mouse is above an item
        its hover flag is set. It also takes of the flag of items that are not anymore hovered.

        :param mouse_x: mouse position x
        :type mouse_x: ``float``
        :param mouse_y: mouse position y
        :type mouse_y: ``float``
        """

        # find the current item that is under the mouse pointer
        hovered_item, hovered_item_pos = self.uv.mouse_ray.check_mouse_ray(mouse_x, mouse_y)

        # if there is no sphere_base item under the mouse pointer the id will be the id of the sphere_base
        if hovered_item and self._hovered_item and hovered_item == self.id:
            # no hovered items
            self._hovered_item.set_hovered(False)
            self._hovered_item = None

        if hovered_item and hovered_item != self.id:
            for item in self.items:
                if item.id == hovered_item:
                    # set hover
                    item.set_hovered(True)
                    self._hovered_item = item
                else:
                    # remove hover
                    item.set_hovered(False)

    def edit_cut(self):
        """
        Cut _selected sphere_base items to clipboard
        """
        data = self.uv.clipboard.serialize_selected(delete=True)
        str_data = json.dumps(data, indent=4)

        pyperclip.copy(str_data)

    def edit_copy(self):
        """
        Copy _selected sphere_base items to clipboard
        """
        data = self.uv.clipboard.serialize_selected(delete=False)
        str_data = json.dumps(data, indent=4)
        pyperclip.copy(str_data)

    def edit_paste(self):
        """
        Paste _selected sphere_base items from clipboard to the target sphere_base
        """
        raw_data = pyperclip.paste()

        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting of not valid json data!", e)
            return

        # check if the json data is correct
        if "nodes" not in data:
            print("JSON does not contain any nodes!")
            return

        self.uv.clipboard.deserialize_from_clipboard(data)

    def remove(self):
        """
         Safely remove this sphere_base and all items on it.
        """
        for item in self.items:
            item.remove()

        self.uv.mouse_ray.delete_collision_object(self)
        self.uv.remove_sphere(self)

    def set_node_class_selector(self, class_selecting_function: 'function'):
        """
        Helper method that sets the function which decides what `Node` class to instantiate when deserializing
        If not set, we will always instantiate :class:`~3dSphere.editor_node.Node` for each `Node` in the `UV`.

        :param class_selecting_function: node class

        """
        self.node_class_selector = class_selecting_function

    def get_node_class_from_data(self, data):
        """
        Takes `Node` serialized data and determines which `Node Class` to instantiate according to the description
        in the serialized Node.
        """
        return SphereNode if self.node_class_selector is None else self.node_class_selector(data)

    def draw(self):
        """
        Render the sphere_base and all the items on it.
        """

        if self.animation != 0:
            self.rotate_sphere(self.animation)

        self.model.draw(self, texture_id=self.texture_id,  color=self.color)
        for item in self.items:
            if item.type == "node":
                item.draw()
            elif item.type == "edge":
                item.draw()

        if self.edge_drag.dragging:
            self.edge_drag.draw()

    def serialize(self):
        nodes, edges = [], []
        for item in self.items:
            if item.type == "node":
                nodes.append(item.serialize())
            elif item.type == "edge":
                edges.append(item.serialize())

        return OrderedDict([
            ('id', self.id),
            ('type', self.type),
            ('pos', self.xyz),
            ('orientation', self.orientation.tolist()),
            ('texture_id', self.texture_id),
            ('color', self.color),
            # ('color_id', self.color_id),
            # ('color_id_per_lens', self.get_color_id_per_lens()),
            ('nodes', nodes),
            ('edges', edges),
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        if restore_id:
            self.id = data['id']
        hashmap[data['id']] = self

        self.xyz = data['pos']
        self.orientation = np.array(data['orientation'])
        self.texture_id = data['texture_id']
        if 'color' in data:
            self.color = data['color']

        self.uv.mouse_ray.reset_position_collision_object(self)

        # -- deserialize nodes on sphere_base

        # Instead of recreating all the nodes, reuse existing ones...
        all_items = self.items.copy()

        # removing socket of the list as each node has precisely 1 socket
        for item in all_items:
            if item.type == "socket":
                all_items.remove(item)

        # go through deserialized nodes:
        for node_data in data['nodes']:
            # can we find this node in the data?
            found = None
            for item in all_items:
                if item.id == node_data['id']:
                    found = item
                    break
            if not found:
                try:
                    new_node = self.get_node_class_from_data(node_data)(self)
                    new_node.deserialize(node_data, hashmap, restore_id)
                except Exception as e:
                    dump_exception(e)
            else:
                try:
                    found.deserialize(node_data, hashmap, restore_id)
                    all_items.remove(found)
                except Exception as e:
                    dump_exception(e)

        # go through all deserialized edges:
        for edge_data in data['edges']:
            # can we find this edge in the data?
            found = None
            for item in all_items:
                if item.id == edge_data['id']:
                    found = item
                    break

            if not found:
                self.Edge(self).deserialize(edge_data, hashmap, restore_id)
            else:
                found.deserialize(edge_data, hashmap, restore_id)
                all_items.remove(found)

            # remove items which are left in the scene and were NOT in the serialized data!
        while all_items:
            item = all_items.pop()
            item.remove()
        return True
