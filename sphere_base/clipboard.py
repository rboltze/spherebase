# -*- coding: utf-8 -*-

"""
Clipboard module. Contains the clipboard class.

"""

from collections import OrderedDict
from pyrr import quaternion, Quaternion
from sphere_base.edge.surface_edge import SurfaceEdge
from sphere_base.utils.utils import dump_exception
from sphere_base.calc import Calc

DEBUG_COPY = False
DEBUG_PASTE = False

class Clipboard:
    """
    This class deals with serializing and deserializing form and to the clipboard.

    """
    def __init__(self, universe):
        """
        Constructor of the clipboard class.

        :param universe: The ``Map``
        :type universe: reference the :class:`~sphere_iot.uv_universe.Map`

        """

        self.uv = universe

    def serialize_selected(self, delete: bool = False) -> 'OrderedDict':
        """

        Copy to clipboard, take the selection and serialize it.

        :param delete: when ``cutting`` the _selected items
        :type delete: ``bool``
        :returns: ``serialized data`` as a ``OrderedDict``

        """

        if DEBUG_COPY:
            print("-- COPY TO CLIPBOARD ---")

        selected_nodes, selected_sockets_ids, selected_edges = [], [], []

        # sort edges and nodes
        for item in self.uv.target_sphere.items_selected:
            if item.type == 'sphere_node':
                selected_nodes.append(item.serialize())
                selected_edges.extend(item.socket.edges)  # find any edges that are connecting selected sockets
                selected_sockets_ids.append(item.socket.id)
            elif item.type == 'edge':
                selected_edges.append(item)

        # remove duplicates
        selected_edges = [*set(selected_edges)]

        # debug
        if DEBUG_COPY:
            print("   NODES\n      ", selected_nodes)
            print("   EDGES\n      ", selected_edges)

        # remove all edges in the list that are not connected on both sides with _selected nodes
        edges_to_remove = []
        for edge in selected_edges:
            if edge.start_socket.id in selected_sockets_ids and edge.end_socket.id in selected_sockets_ids:
                if DEBUG_COPY:
                    print(" edge is ok, connected at both sides with _selected nodes")
                pass
            else:
                if DEBUG_COPY:
                    print("edge", edge, "is not connected on both sides with _selected nodes")
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            selected_edges.remove(edge)

        # make final list of edges
        edges_final = []
        for edge in selected_edges:
            edges_final.append(edge.serialize())

        if DEBUG_COPY:
            print("our final list of edges:", edges_final)

        data = OrderedDict([
            ('sphere_nodes', selected_nodes),
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

        when there is one node to be pasted the location is at the mouse_ray_collision_point.
        When there are multiple objects they will be pasted around a mouse ray collision point.

        The edges need to be connected to the new sockets. We need to first map the old sockets with the new ones.

        """
        if DEBUG_PASTE:
            print("-- PASTE FROM CLIPBOARD ---")

        try:
            hashmap = {}
            created_nodes = []
            length = len(data['sphere_nodes'])

            sphere_id, cp, mouse_x, mouse_y = self.uv.get_mouse_pos()
            orientation = Calc.find_angle(cp, self.uv.target_sphere.orientation)

            if DEBUG_PASTE:
                print("     mouse_ray_collision point - xyz:\n     ", cp)
                print("     pos_orientation_offset - quaternion:\n        ", orientation)

            # Find the middle between the nodes
            old_centre, first_node = None, None
            for i, node_data in enumerate(data['sphere_nodes']):
                q = Quaternion(node_data['orientation_offset'])
                if i == 0:
                    old_centre = q
                else:
                    old_centre = quaternion.slerp(old_centre, q, 0.5)

            sockets_map = {}
            for i, node_data in enumerate(data['sphere_nodes']):
                new_node = self.uv.target_sphere.get_node_class_from_data(node_data)(self.uv.target_sphere)
                new_node.deserialize(node_data, hashmap, restore_id=False)
                created_nodes.append(new_node)
                new_node.on_selected_event(True)

                # create a map linking each old socket with the newly created ones
                sockets_map[node_data['socket_id']] = new_node.socket.id

                self.uv.target_sphere.select_item(new_node, False if i == 0 else True)

                # For each node we need to find the offset between the old center and its old position
                offset = quaternion.cross(new_node.pos_orientation_offset, quaternion.inverse(old_centre))

                if length == 1:
                    new_node.pos_orientation_offset = orientation
                    new_node.update_position()
                    new_node.update_collision_object()
                else:
                    new_center = orientation

                    # apply the offset with the old center to the mouse_ray_collision point
                    new_node.pos_orientation_offset = quaternion.cross(offset, new_center)
                    new_node.update_position()
                    new_node.update_collision_object()

            # create each edge
            if 'edges' in data:
                for edge_data in data['edges']:
                    # find the old id matching the new id in the sockets map
                    edge_data['start_socket_id'] = sockets_map[edge_data['start_socket_id']]
                    edge_data['end_socket_id'] = sockets_map[edge_data['end_socket_id']]
                    new_edge = SurfaceEdge(self.uv.target_sphere)

                    new_edge.deserialize(edge_data, hashmap, restore_id=False)

            # store history
            self.uv.target_sphere.history.store_history("Pasted elements on globe", set_modified=True)
            return created_nodes

        except Exception as e:
            dump_exception(e)
