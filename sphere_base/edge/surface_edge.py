# -*- coding: utf-8 -*-

"""
Sphere Surface Edge module. Contains the SphereSurfaceEdge class.
Edges are drawn between sockets over the surface of a sphere_base.

"""

# Do not remove these!!!
# -------------- these will be dynamically read! -----------------------

from sphere_base.shader.dynamic_shader import DynamicShader

# -----------------------------------------------------------------------

from pyrr import quaternion, vector, Vector3
from sphere_base.sphere.graphic_edge import GraphicEdge
from sphere_base.serializable import Serializable
from sphere_base.model.model import Model
from sphere_base.model.mesh import Mesh
from sphere_base.model.obj_file_loader import ObjectFileLoader
from collections import OrderedDict
from sphere_base.utils import dump_exception
import numpy as np
from sphere_base.constants import *
from OpenGL.GL import *

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

    def __init__(self, target_sphere: 'sphere_base', socket_start: 'socket' = None, socket_end: 'socket' = None):
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

        self._start_socket, self._end_socket = None, None
        self.start_socket = socket_start if socket_start else None
        self.end_socket = socket_end if socket_end else None
        self.xyz = None
        self.orientation = None

        self.gr_edge = self.__class__.GraphicsEdge_class(self)

        self.model = self.set_up_model('edge1')
        self.shader = self.model.shader

        self.loader = ObjectFileLoader(self.model, self.config)

        # ------------------------------------------------------------

        # self.mesh_id = glGenVertexArrays(1)
        self.mesh_id = self.loader.create_buffers(1)
        self.model.model_id = self.mesh_id
        self.scale = [1.0, 1.0, 1.0]

        self.shader.mesh_id = self.mesh_id

        self.buffer_id = glGenBuffers(1)
        self.shader.buffer_id = self.buffer_id

        # self.VAO_id = glGenVertexArrays(1)
        # self.VBO_id = glGenBuffers(1)
        # self.EBO_id = glGenBuffers(1)

        self.vertices = np.array([], dtype=np.float32)  # vertex coordinates
        self.buffer = np.array([], dtype=np.float32)
        self.indices = np.array([], dtype='uint32')

        self.mesh = self.__class__.Mesh_class(self.model, self.mesh_id, vertices=[], indices=[], buffer=[])
        self.model.meshes.append(self.mesh)
        # position_orientation (angle) of the node on the sphere_base relative to the zero rotation of the
        # sphere_base is the same as the starting socket
        self.pos_orientation_offset = None

        # ------------------------------------------------------------

        self.radius = self.sphere.radius - 0.01
        self.collision_object_id = None
        self.color = self.gr_edge.color
        self.edge_type = 0
        self.serialized_detail_scene = None
        self._edge_moved = False

        # register the edge to the sphere_base for rendering
        self.sphere.add_item(self)
        # self.update_position()
        self.create_edge()

    def set_up_model(self, model_name):
        shader, vertex_shader, fragment_shader, geometry_shader = None, None, None, None

        for _name in MODELS.keys():
            if _name == model_name:
                shader = MODELS[_name]["shader"]
                vertex_shader = MODELS[_name]["vertex_shader"]
                fragment_shader = MODELS[_name]["fragment_shader"]
                geometry_shader = MODELS[_name]["geometry_shader"]
                geometry_shader = None if geometry_shader == "none" else geometry_shader

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

    def update_position(self):
        """
        Updates the position of the edge.

        """
        # self.pos_orientation_offset = self.start_socket.pos_orientation_offset
        # cumulative_orientation = self.get_cumulative_rotation()
        # self.xyz = self.calc.move_to_position(cumulative_orientation, self.sphere, self.radius)
        #
        # self.orientation = self.start_socket.orientation  # same orientation as the start socket
        #
        # # self.node.sphere.uv.mouse_ray.reset_position_collision_object(self)
        #

        # get number of vertices on the edge
        if self.start_socket and self.end_socket:
            number_of_vertices = self.gr_edge.get_number_of_vertices(self.start_socket.xyz, self.end_socket.xyz,
                                                                     self.sphere.radius, self.gr_edge.unit_length)
            step = 1 / number_of_vertices if number_of_vertices > 1 else 1

            if number_of_vertices > 0:
                self.update_line_points_position(number_of_vertices, step)

            self.loader.load_mesh_into_opengl(self.mesh_id, self.mesh.buffer, self.mesh.indices, self.shader)
            # self.load_mesh_into_opengl(self.mesh_id, self.mesh.buffer, self.mesh.indices, self.shader)

    def create_edge(self):
        # create an edge for the first time or recreate it during dragging
        if self.start_socket and self.end_socket:
            number_of_vertices = self.gr_edge.get_number_of_vertices(self.start_socket.xyz, self.end_socket.xyz,
                                                                     self.sphere.radius, self.gr_edge.unit_length)
            step = 1 / number_of_vertices if number_of_vertices > 1 else 1

            if number_of_vertices > 0:
                self.update_line_points_position(number_of_vertices, step)



    def get_cumulative_rotation(self):
        """
        Helper function returns a quaternion with a cumulative rotation of both the rotation
        offset of the edge with the rotation of the sphere_base.
        """

        return quaternion.cross(self.pos_orientation_offset, quaternion.inverse(self.sphere.orientation))

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
        vert = []  # vertex coordinates
        vertex = []  # vertex coordinates
        buffer = []
        indices = []

        for i in range(number_of_vertices):
            pos_orientation_offset = quaternion.slerp(start, end, step * i)
            p = self.gr_edge.get_position(pos_orientation_offset)  # finding the vertex xyz
            n = vector.normalize(Vector3(p) - Vector3(self.sphere.xyz))  # finding the normal of the vertex

            vert.append([p[0], p[1], p[2]])  # we need this for pybullet
            vertex.extend(p)  # extending the vertices list with the vertex
            buffer.extend(p)  # extending the buffer with the vertex
            buffer.extend(n)  # extending the buffer with the normal
            indices.append(i)

        # creating a collision object for mouse ray collisions
        self.collision_object_id = self.sphere.uv.mouse_ray.create_collision_object(self, vert)

        self.shader.vertices = np.array(vertex, dtype=np.float32)
        self.shader.buffer = np.array(buffer, dtype=np.float32)

        self.mesh.vertices = np.array(vertex, dtype=np.float32)
        self.mesh.indices = np.array(indices, dtype='uint32')
        self.mesh.buffer = np.array(buffer, dtype=np.float32)

        self.orientation = self.start_socket.orientation
        self.mesh.indices_len = len(indices)

        self.loader.load_mesh_into_opengl(self.mesh_id, self.mesh.buffer, self.mesh.indices, self.shader)

    def get_edge_start_end(self):
        # get clearance from start socket
        r = self.start_socket.node.gr_node.node_disc_radius * .9
        ln = self.calc.get_distance_on_sphere(self.end_socket, self.start_socket, self.radius)
        t = r / ln

        s_angle = self.start_socket.pos_orientation_offset
        end = self.end_socket.pos_orientation_offset

        start = quaternion.slerp(s_angle, end, t)

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
            self.sphere.history.store_history("edge moved", True)
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
        # in some cases color turns to none. The reason is not known. The following line patches this problem
        self.color = [0.0, 0.0, 0.0, 0.5] if not self.color else self.color
        # self.shader.draw_edge(self.pos_array, width=1.5, color=self.color, dotted=False)
        # self.model.shader.draw_edge(self.pos_array, width=4, color=self.color, dotted=False)

        try:
            pass
            # self.shader.draw(
            #     object_index=0,
            #     object_type="",
            #     mesh_index=self.mesh_id,
            #     indices_len=0,
            #     position=self.sphere.xyz,
            #     orientation=self.sphere.orientation,
            #     scale=None,
            #     texture_id=0,
            #     color=[1.0, 1.0, 1.0, 1.0],
            #     switch=0)

            self.model.draw(self)

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
