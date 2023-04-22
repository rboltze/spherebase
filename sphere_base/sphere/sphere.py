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
from sphere_base.node.node import Node
from sphere_base.edge.edge_drag import EdgeDrag
from sphere_base.edge.surface_edge import SurfaceEdge
from sphere_base.sphere.sphere_lines import SphereLines
from sphere_base.history import History
from pyrr import quaternion
from math import pi
from sphere_base.calc import Calc
from sphere_base.constants import *
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

    Node_class = Node
    Edge_class = SurfaceEdge
    Calc_class = Calc
    Edge_drag_class = EdgeDrag
    History_class = History

    def __init__(self, universe, position: list = None, texture_id: int = None, sphere_type='sphere_base'):
        """
        Constructor of the sphere_base class.

        :param universe: reference to the :class:`~sphere_iot.uv_universe.Universe`
        :type universe: :class:`~sphere_iot.uv_universe.Universe`
        :param position: position of the sphere_base in universe
        :type position: ``list`` with x, y, z values
        :param texture_id: number indicating which texture to use for the sphere_base
        :type texture_id: int.

        :Instance Attributes:

            - **node** - Instance of :class:`~sphere_iot.uv_node.Node`
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

        self._has_been_modified = False
        self._dragging = False
        self.selected = False

        # The sphere rotates
        self.rotation_degrees = 0

        self.index = 0
        self.radius = SPHERE_RADIUS
        self.scale = [self.radius, self.radius, self.radius]
        self.color = [1, 1, 1, 1]
        self.orientation = quaternion.create_from_eulers([0.0, self.radius, 0.0])
        self.start_socket = None
        self._hovered_item = None
        self.animation = 0  # rotation speed
        self.node_class_selector = None

        self.selected_item = None
        self._last_selected_items = None

        self.items = []
        self.items_selected = []
        self.items_deselected = []
        self._selection_changed_listeners = []
        self._items_deselected_listeners = []
        self._has_been_modified_listeners = []

        self.model = None
        self.get_model()

        # instance attributes
        self.Node = self.__class__.Node_class
        self.Edge = self.__class__.Edge_class
        self.calc = self.__class__.Calc_class()
        self.edge_drag = self.__class__.Edge_drag_class(self)
        self.history = self.__class__.History_class(self)

        self.xyz = position if position else ([randint(-25, 25), randint(-25, 25), randint(-25, 25)])
        self.texture_id = texture_id if texture_id or texture_id == 0 else randint(1, 5)

        self.collision_shape_id = self.uv.mouse_ray.get_collision_shape(self)
        self.collision_object_id = self.uv.mouse_ray.create_collision_object(self)

        self.sphere_lines_mayor = SphereLines(self, 20, 20, 0, [0.5, 0, 0, 0.05], 4)  # red lines
        self.sphere_lines_minor = SphereLines(self, 40, 40, 0, [0.3, 0.3, 0.5, 0.1], 3)  # blue lines
        self.sphere_lines_micro = SphereLines(self, 100, 100, 0, [0, 0, 0, 0.1], 1)  # black lines
        self.sphere_lines_nano = SphereLines(self, 200, 200, 0, [0, 0, 0, 0.03], 1, 7)  # close distance only

        # for testing purposes a number of random nodes can be created
        # self.create_test_node(NUMBER_OF_TEST_NODES)

        # add the sphere_base to the universe
        self.uv.add_sphere(self)
        self.history.store_initial_history_stamp()

    def get_model(self):
        # likely to be overridden
        self.model = self.uv.models.get_model('sphere_base')

    @property
    def dragging(self) -> bool:
        """

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

    def add_has_been_modified_listener(self, callback):
        """
        Register callback for 'has been modified' event.
        :param callback: callback function
        """
        self._has_been_modified_listeners.append(callback)

    def add_selection_changed_listener(self, callback):
        """
        Register callback for 'selection changed' event.
        :param callback: callback function
        """
        self._selection_changed_listeners.append(callback)

    def add_item_deselected_listener(self, callback):
        """
        Register callback for `deselected item` event.
        :param callback: callback function
        """
        self._items_deselected_listeners.append(callback)

    def create_new_node(self, node_type: str = "person", abs_pos=None):
        """
        Needs to be overridden.
        Can be used to create any type of node at the mouse pointer.

        :param node_type: can be ``person`` or ``item``
        :type node_type: ``string``
        :return: :class:`~sphere_iot.uv_node.Node`
        :param abs_pos: position in space
        :type abs_pos:
        """
        # # calculate the cumulative angle based on the mouse position
        # orientation = self.calc_mouse_position_in_angles(mouse_x, mouse_y)
        #
        # # create new node at the cumulative angle
        # node = self.Node(self, orientation)
        # self.history.store_history("node created", True)
        # return node

        return NotImplemented

    def on_item_selected(self, current_selected_items):
        """
        Handles item selection and triggers event `Item _selected`.
        """

        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items

            for callback in self._selection_changed_listeners:
                callback(self, current_selected_items)

                self.history.store_history("Selection Changed")

    def on_item_deselected(self, item: 'Node or Edge'):
        """
        Handles item deselection and triggers event `Items deselected`. Not used in the current implementation.

        :param item: Node or Edge
        :type item: :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_surface_edge.SphereSurfaceEdge`
        """
        current_selected_items = self.items_selected
        if current_selected_items == self._last_selected_items:
            return

        if not current_selected_items:
            self._last_selected_items = []

            for callback in self._items_deselected_listeners:
                callback(self, item)
                self.history.store_history("Deselected Everything")

    def get_item_by_id(self, item_id: int):
        """
        Helper function returns an item of type `node` or `edge` based on id.

        :param item_id: The id of the item to be returned
        :type item_id: ``int``
        :return: :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
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
        :return: :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        """

        for item in self.items:
            if selected_item_id == item.id:
                self.select_item(item, shift)
                return item
        return None

    def get_socket_edges(self, socket) -> list:
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
        """Add :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
        to the `Sphere`.

        :param item: Node or Edge
        :type item: :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
                    or :class:`~sphere_iot.uv_socket.Socket`
        """

        # adding item to sphere_base
        self.items.append(item)

    def remove_item(self, item: 'Node or Edge or Socket'):
        """Remove :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_edge.SphereEdge`
        from the target `Sphere`.
        :param item: Node or Edge to remove from this `Sphere`
        :type item: :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_surface_edge.SphereSurfaceEdge`
        or :class:`~sphere_iot.uv_socket.Socket`

        """
        # removing item from sphere_base
        if item in self.items:
            self.items.remove(item)

    def has_edge(self, start_socket, end_socket) -> bool:
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

    def create_edge(self, end_socket):
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
           and children or the direction of ownership that goes from a person to the product.

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
            if item.type in ('node', 'sphere_lines'):
                # updating the node trickles down to updating sockets and edges"
                item.update_position()

    def rotate_sphere(self, offset_degrees: int):
        """
        Rotating the sphere_base over the y-axis as per the offset_degrees.

        :param offset_degrees: degrees that the sphere_base rotates over its y-axis
        :type offset_degrees: ``int``
        """

        self.rotation_degrees += offset_degrees

        if self.rotation_degrees > 180:
            self.rotation_degrees -= 360
        elif self.rotation_degrees < -180:
            self.rotation_degrees = self.rotation_degrees + 360

        pitch = (pi / 180 * offset_degrees)
        rotation = quaternion.create_from_eulers([0.0, pitch, 0.0])
        self.orientation = quaternion.normalize(quaternion.cross(self.orientation, rotation))
        self.update_item_positions()

    def drag_items(self, mouse_ray_collision_point=None):
        """
        Dragging all _selected items. The offset is the difference between the current and last stored location
        of the mouse pointer on the screen.

        :param mouse_ray_collision_point:
        :type mouse_ray_collision_point: ``float``
        :return:

        .. note::

           Only existing nodes need to be dragged, as the position of sockets and edges are
           adjusted automatically. Updating the position of a node trickles down to adjusting the position of the
           center sockets of the _selected nodes and any connected edges.

           It is important to maintain the distance to the mouse. So we need to calculate the difference between the
           current mouse position and the center of the items we are dragging, otherwise the node centers jumps to
           the collision point.

        """
        for item in self.items_selected:
            if item.type == "node":
                # only drag any nodes in the _selected item list
                item.drag_to(mouse_ray_collision_point)
                item.mouse_ray_collision_point = mouse_ray_collision_point
                self.dragging = item.is_dragging(True)

    def select_item(self, item: 'node or edge', shift: bool = False):
        """
        Select an item by clicking on it. Holding shift down while clicking on an item, adds it to the _selected list.
        Sockets cannot be _selected.

        :param item: ``Node`` or ``Edge``
        :type item: :class:`~sphere_iot.uv_node.Node` or :class:`~sphere_iot.uv_surface_edge.SphereSurfaceEdge`
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
                        item.remove(with_edges=True)  # remove node, socket and connected items
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

        # if there is no sphere item under the mouse pointer the id will be the id of the sphere
        if hovered_item and self._hovered_item and hovered_item == self.id:
            # no hovered items
            self._hovered_item.set_hovered(False)
            self._hovered_item = None

        if hovered_item and hovered_item != self.id:
            for item in self.items:
                if item.id == hovered_item:
                    # set hover
                    if item.type in ('node', 'socket', 'edge'):
                        item.set_hovered(True)
                        self._hovered_item = item
                else:
                    # remove hover
                    if item.type in ('node', 'socket', 'edge'):
                        item.set_hovered(False)

        return self._hovered_item

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
        check that the mouse pointer is above the sphere and get the position of the mouse_ray collision point.
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

    def set_radius(self, radius):
        """
        setting the radius of the sphere

        :param radius:
        :return:
        """
        self.radius = radius
        self.scale = [radius, radius, radius]
        self.orientation = quaternion.create_from_eulers([0.0, radius, 0.0])
        self.uv.cam.reset_to_default_view(self)
        self.collision_shape_id = self.uv.mouse_ray.get_collision_shape(self)

    def set_node_class_selector(self, class_selecting_function):
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
        return Node if self.node_class_selector is None else self.node_class_selector(data)

    def draw(self):
        """
        Render the sphere_base and all the items on it.
        """

        if self.animation != 0:
            self.rotate_sphere(self.animation)

        self.model.draw(self, texture_id=self.texture_id, color=self.color)
        for item in self.items:
            if item.type == "node":
                item.draw()
            elif item.type == "edge":
                item.draw()
            elif item.type == "sphere_lines":
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
            ('radius', self.radius),
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
        if 'radius' in data:
            self.set_radius(data['radius'])
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
