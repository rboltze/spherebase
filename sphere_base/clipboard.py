# -*- coding: utf-8 -*-

"""
Clipboard module. Contains the clipboard class.

"""

from collections import OrderedDict
from pyrr import quaternion, Quaternion
from sphere_base.sphere_universe_base.suv_surface_edge import SphereSurfaceEdge

DEBUG = False


class Clipboard:
    """
    This class deals with serializing and deserializing form and to the clipboard.

    """
    def __init__(self, universe):
        """
        Constructor of the clipboard class.

        :param universe: The ``Universe``
        :type universe: reference the :class:`~sphere_iot.uv_universe.Universe`

        """

        self.uv = universe

    def serialize_selected(self, delete: bool = False) -> 'OrderedDict':
        """
        Copy to clipboard

        :param delete: when ``cutting`` the _selected items
        :type delete: ``bool``
        :returns: ``serialized data`` as a ``OrderedDict``

        """

        if DEBUG: print("-- COPY TO CLIPBOARD ---")

        selected_nodes, selected_sockets_ids, selected_edges = [], [], []

        # sort edges and nodes
        for item in self.uv.target_sphere.items_selected:
            if item.type == 'node':
                selected_nodes.append(item.serialize())
                selected_sockets_ids.append(item.socket.id)
            elif item.type == 'edge':
                selected_edges.append(item)

        # debug
        if DEBUG:
            print("   NODES\n      ", selected_nodes)
            print("   EDGES\n      ", selected_edges)

        # remove all edges in the list that are not connected on both sides with _selected nodes
        edges_to_remove = []
        for edge in selected_edges:
             if edge.start_socket.id in selected_sockets_ids and edge.end_socket.id in selected_sockets_ids:
                 if DEBUG:
                     print(" edge is ok, connected at both sides with _selected nodes")
                 pass
             else:
                if DEBUG:
                    print("edge", edge, "is not connected on both sides with _selected nodes")
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            selected_edges.remove(edge)

        # make final list of edges
        edges_final = []
        for edge in selected_edges:
            edges_final.append(edge.serialize())

        if DEBUG:
            print("our final list of edges:", edges_final)

        data = OrderedDict([
            ('nodes', selected_nodes),
            ('edges', edges_final),
            ])

        # if CUT (aka delete) remove _selected items from the sphere_base
        if delete:
            self.uv.target_sphere.delete_selected_items()
            self.uv.target_sphere.history.store_history("Cut out elements from scene", set_modified=True)

        return data

    def deserialize_from_clipboard(self, data: 'OrderedDict') -> list:
        """
        Paste data from clipboard to the target sphere_base.

        :param data: Data to deserialize
        :type data: ``OrderedDict``
        :return: list with nodes

        .. warning::

            Pasting a group of sphere_base nodes does locate the nodes in the expected position. The nodes are pasted
            inverse of what is expected. The top node is pasted at the bottom and the bottom node is pasted at the top.

            Also the connected edges are not copied and pasted.

            This needs to be looked into in a future iteration.

        """
        hashmap = {}

        # # create each node
        created_nodes = []

        length = len(data['nodes'])

        for i, node_data in enumerate(data['nodes']):
            q = Quaternion(node_data['orientation_offset'])

            if i == 0:
                a = q
                middle = q
            else:
                middle = quaternion.slerp(a, q, .5)

        for i, node_data in enumerate(data['nodes']):

            new_node = self.uv.target_sphere.get_node_class_from_data(node_data)(self.uv.target_sphere)
            new_node.deserialize(node_data, hashmap, restore_id=False)
            created_nodes.append(new_node)

            new_node.on_selected_event(True)
            self.uv.target_sphere.select_item(new_node, False if i == 0 else True)

            diff = quaternion.cross(quaternion.inverse(new_node.pos_orientation_offset), middle)

            if length == 1:
                new_center = self.uv.target_sphere.calc_mouse_position_in_angles(self.uv.mouse_x, self.uv.mouse_y)
                new_node.pos_orientation_offset = new_center
                new_node.update_position()
            else:
                new_center = self.uv.target_sphere.calc_mouse_position_in_angles(self.uv.mouse_x, self.uv.mouse_y)
                new_node.pos_orientation_offset = quaternion.cross(new_center, diff)
                new_node.update_position()

        # create each edge
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = SphereSurfaceEdge(self.uv.target_sphere)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)

        # store history
        self.uv.target_sphere.history.store_history("Pasted elements in scene", set_modified=True)

        return created_nodes






