# -*- coding: utf-8 -*-

"""
Sphere Surface Edge module. Contains the SphereSurfaceEdge class.
Edges are drawn between sockets over the surface of a sphere_base.

"""

from pyrr import quaternion, vector, Vector3
from sphere_base.edge.graphic_edge import GraphicEdge
from sphere_base.serializable import Serializable
from sphere_base.model.model import Model
from sphere_base.model.mesh import Mesh
from collections import OrderedDict
from sphere_base.utils import dump_exception
import numpy as np
from sphere_base.constants import *

DEBUG = False


class SurfaceEdge(Serializable):
    Mesh_class = Mesh

    """
    Class representing an ``Edge`` on a ``Sphere``. ``Edges`` are drawn between ``Sphere Sockets``.

    This class represents the edge between two sockets. The edges follow the surface of an sphere_base.
    We are using SLERP to determine the angle of each of the points between start and end
    with the center of the sphere_base.

    .. note::

    There is no difference between start and end socket. It is not relevant in the current deployment. In
    future iterations this is likely to change as the direction of the edge may have significance.

    The edge starts and ends at sockets. It takes the shortest distance over the surface of the sphere.

        All the variables needed are known:

            - Start_socket angle with origin sphere
            - end socket angle with origin sphere
            - radius of the sphere

        We then need to plot points between start and end over the great sphere based on the distance over the sphere.

        When creating or dragging a node with an edge, the vertices change and need to replace the existing
        vertices before drawing the new ones.

    """
    GraphicsEdge_class = GraphicEdge

    def __init__(self, target_sphere, socket_start=None, socket_end=None):
        """
        Constructor of the edge class. Creates an edge between a start and an end socket.

        :param target_sphere: The sphere_base on which the edge is drawn
        :type target_sphere: :class:`~sphere_iot.uv_sphere.Sphere`
        :param socket_start: start socket from where is drawn.
        :type socket_start: :class:`~sphere_iot.uv_socket.Socket`
        :param socket_end: end socket where the edge is drawn to.
        :type socket_end: :class:`~sphere_iot.uv_socket.Socket`

        :Instance Attributes:

            - **uv** - Instance of :class:`~sphere_iot.uv_universe.Universe`
            - **sphere_base** - Instance of :class:`~sphere_iot.uv_sphere.Sphere`
            - **calc** - Instance of :class:`~sphere_iot.uv_calc.UvCalc`
            - **model** - Instance of :class:`~sphere_iot.uv_models.Model`
            - **gr_edge** - Instance of :class:`~sphere_iot.uv_graphic_edge.GraphicEdge`
            - **shader** - Instance of :class:`~sphere_iot.shader.uv_base_shader.BaseShader`

        """

        super().__init__("edge")
        self.sphere = target_sphere
        self.calc = self.sphere.calc
        self.config = self.sphere.config
        self.uv = self.sphere.uv

        self.gr_edge = self.__class__.GraphicsEdge_class(self)

        self._start_socket, self._end_socket = None, None
        self.start_socket = socket_start if socket_start else None
        self.end_socket = socket_end if socket_end else None
        self.xyz, self.pos_orientation_offset = None, None
        self.collision_object_id = None
        self.vert = []  # vertices needed for pybullet mouse ray
        self.serialized_detail_scene = None
        self._edge_moved = False
        self.line_width = 2
        self.scale = [1.0, 1.0, 1.0]
        self.color = self.gr_edge.color
        self.edge_type = 0
        self.orientation = self.sphere.orientation
        self._new_edge = True
        self.model = self.set_up_model('edge')

        self.mesh = self.model.meshes[0]
        self.mesh_id = self.mesh.mesh_id

        self.model.name = 'edge_' + str(self.mesh_id)

        self.radius = self.sphere.radius  # - 0.01
        self.sphere.add_item(self)  # register the edge to the base for rendering
        self.create_edge()

    def set_up_model(self, model_name):
        shader, vertex_shader, fragment_shader, geometry_shader = None, None, None, None

        # get the shaders for the edge
        for _name in MODELS.keys():
            if _name == model_name:
                shader = MODELS[_name]["shader"]
                vertex_shader = MODELS[_name]["vertex_shader"]
                fragment_shader = MODELS[_name]["fragment_shader"]
                geometry_shader = MODELS[_name]["geometry_shader"]
                geometry_shader = None if geometry_shader == "none" else geometry_shader

        # create a model for the edge
        model = Model(
                      models=self.uv.models,
                      model_id=0,
                      model_name=model_name,
                      obj_file="",
                      shader=shader,
                      vertex_shader=vertex_shader,
                      fragment_shader=fragment_shader,
                      geometry_shader=geometry_shader)

        return model

    @property
    def start_socket(self):
        """
        Start socket

        :getter: Returns start :class:`~sphere_iot.uv_socket.Socket`
        :setter: Sets start :class:`~sphere_iot.uv_socket.Socket` safely
        :type: :class:`~sphere_iot.uv_socket.Socket`
        """
        return self._start_socket

    @start_socket.setter
    def start_socket(self, start_socket):

        # if already connected, delete  from  socket
        if self._start_socket is not None:
            self._start_socket.remove_edge(self)

        # assign new start socket
        self._start_socket = start_socket

        # add edge to the new socket class
        if self.start_socket is not None:
            self.start_socket.add_edge(self)
            self.xyz = self.sphere.xyz
            self.pos_orientation_offset = self.start_socket.pos_orientation_offset

    @property
    def end_socket(self):
        """
        End socket

        :getter: Returns end :class:`~sphere_iot.uv_socket.Socket`
        :setter: Sets end :class:`~sphere_iot.uv_socket.Socket` safely
        :type: :class:`~sphere_iot.uv_socket.Socket`
        """
        return self._end_socket

    @end_socket.setter
    def end_socket(self, end_socket):

        # if already connected, delete  from  socket
        if self._end_socket is not None:
            self._end_socket.remove_edge(self)

        # assign new end socket
        self._end_socket = end_socket

        # add edge to the Socket class
        if self.end_socket is not None:
            self.end_socket.add_edge(self)

    def update_collision_object(self):
        # set the collision object for mouse pointer ray collision
        self.sphere.uv.mouse_ray.reset_position_collision_object(self, self.vert)

    def update_position(self):
        """º
        Recreate the edge when any of the sockets positions change

        """

        a = set(self.orientation)
        b = set(self.sphere.orientation)

        if a == b:
            # socket(s) have changed
            self.create_edge()
        else:
            # sphere rotates - just update the rotation
            self.orientation = self.sphere.orientation

    def create_edge(self):
        # create an edge for the first time or recreate it during dragging

        if self.start_socket and self.end_socket:
            count = self.gr_edge.count_vertices(self.start_socket.xyz, self.end_socket.xyz,
                                                self.radius, self.gr_edge.unit_length)

            step = 1 / count if count > 1 else 1

            if count > 0:
                self.update_line_points_position(count, step)

    def update_line_points_position(self, number_of_vertices: int, step: float):
        """
        Creates an array of vertex locations. SLERP is used to find angles with the center of the sphere_base for
        each of the points. Each point receives also a normal.

        :param number_of_vertices: Number of points on the edge
        :type number_of_vertices: ``int``
        :param step: percentage of increase for each point on the edge
        :type step: ``float``
        """

        start, end = self.get_edge_start_end()
        self.vert = []
        vertices = []  # vertex coordinates
        buffer = []
        indices = []

        tex = [1.0, 1.0]  # made up surface edge, that needs to be added to the buffer
        for i in range(number_of_vertices):
            pos = quaternion.slerp(start, end, step * i)

            p = self.calc.move_to_position(pos, self.sphere)
            n = vector.normalize(Vector3(p) - Vector3(self.sphere.xyz))  # finding the normal of the vertex

            vertices, buffer, indices = self.expand_mesh(vertices, buffer, indices, p, tex, n, i)

        if self._new_edge:
            # creating a collision object for mouse ray collisions
            self.collision_object_id = self.sphere.uv.mouse_ray.create_collision_object(self, self.vert)
            self._new_edge = False

        self.mesh.vertices = np.array(vertices, dtype=np.float32)
        self.mesh.indices = np.array(indices, dtype='uint32')
        self.mesh.buffer = np.array(buffer, dtype=np.float32)
        self.mesh.indices_len = len(indices)

        self.xyz = self.sphere.xyz
        self.model.loader.load_mesh_into_opengl(self.mesh_id, self.mesh.buffer,
                                                self.mesh.indices, self.model.shader)

    def expand_mesh(self, vertices, buffer, indices, point, texture, normals, i):
        # This can be used to expanding each point into a mesh.
        p = point
        self.vert.append([p[0], p[1], p[2]])  # we need this for pybullet
        vertices.extend(p)  # extending the vertices list with the vertex
        buffer = self.extend_buffer(buffer, point, texture, normals)
        indices.append(i)
        return vertices, buffer, indices

    @staticmethod
    def extend_buffer(buffer, vertex, texture, normal):
        buffer.extend(vertex)  # extending the buffer with the vertex
        buffer.extend(texture)  # extending the buffer with the texture
        buffer.extend(normal)  # extending the buffer with the normal
        return buffer

    def get_edge_start_end(self):
        """
        returns start and end angles in quaternions.

        """
        # get clearance from start socket
        r0 = self.start_socket.node.gr_node.node_disc_radius
        r1 = self.end_socket.node.gr_node.node_disc_radius

        start_angle = self.start_socket.pos_orientation_offset
        end_angle = self.end_socket.pos_orientation_offset

        # the length between start and end
        ln = self.calc.get_distance_on_sphere(self.end_socket, self.start_socket, self.radius)

        step = (r0 * .9) / ln
        start = quaternion.slerp(start_angle, end_angle, step)
        step = (r1 * .5) / ln
        end = quaternion.slerp(end_angle, start_angle,  step)

        # start and end in angles
        return start, end

    def update_content(self, value, item_id):
        """
        This is called on all sphere_base items but is currently not used on edges.
        Updates the content like icons and images

        """
        # needs to be overridden
        pass

    def is_dragging(self, value=False):
        if self._edge_moved == value:
            return value
        elif self._edge_moved and not value:
            # end dragging
            self._edge_moved = False
            # self.sphere.history.store_history("edge moved", set_modified=True)
        elif not self._edge_moved and value:
            # start dragging
            self._edge_moved = True
        return self._edge_moved

    def on_selected_event(self, event: bool):
        """
        Sets all flags and colors to match the new state.

        :param event: ``True`` sets the state to '_selected'
        :type event: ``bool``
        """
        self.color = self.gr_edge.on_selected_event(event)

    def set_hovered(self, event: bool):
        """
        Sets all flags and colors to match the new state.

        :param event: ``True`` sets the state to 'hovered'
        :type event: ``bool``
        """
        self.color = self.gr_edge.on_hover_event(event)

    def remove(self):
        """
        Removes the edge and the collision object
        """

        # make sure that the edge gets removed from both sockets
        self.start_socket.remove_edge(self)
        self.end_socket.remove_edge(self)
        self.sphere.remove_item(self)

        if self.collision_object_id:
            self.sphere.uv.mouse_ray.delete_collision_object(self)

    def draw(self):
        """
        Renders the edge.
        """
        try:
            self.model.draw(self, color=self.color, line_width=self.line_width)
        except Exception as e:
            dump_exception(e)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('type', self.type),
            ('edge_type', self.edge_type),
            ('start_socket_id', self.start_socket.id),
            ('end_socket_id', self.end_socket.id),
            ('scene', self.serialized_detail_scene)
        ])

    def deserialize(self, data: dict, hashmap: dict = None, restore_id: bool = True) -> bool:
        if restore_id:
            self.id = data['id']
        self.edge_type = data['edge_type']
        self.start_socket = self.sphere.get_item_by_id(data['start_socket_id'])
        self.end_socket = self.sphere.get_item_by_id(data['end_socket_id'])
        self.serialized_detail_scene = data['scene']
        self.update_position()
        return True
