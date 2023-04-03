# -*- coding: utf-8 -*-

"""
Dynamic shader. This is the dynamic shader class. It allows for dynamic shading lines and objects


"""

from OpenGL.GL import *
from pyrr import Vector3, matrix44
import pyrr
from OpenGL.GL.shaders import compileProgram, compileShader
from sphere_base.shader.base_shader import BaseShader

from sphere_base.constants import *


class DynamicShader(BaseShader):

    def __init__(self, parent, vertex_shader=None, fragment_shader=None, geometry_shader=None, *args, **kwargs):
        """
        Constructor of the ``BaseShader`` class.

        :param parent: The parent that initiates the shader class.

        :Instance Variables:

            - **config** - reference to :class:`~sphere_iot.uv_config.UvConfig`
            - **width** - width of the view.
            - **height** - height of the view.
            - **parent** - In many cases this is :class:`~sphere_iot.uv_models.Model`.
            - **shader_id** - Unique ID of the OpenGL shader.

        """

        self.config = parent.config
        self.width = self.config.view.view_width
        self.height = self.config.view.view_height

        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        self.geometry_shader = geometry_shader

        self._init_values()
        self.shader_id = self.compile_shader()
        self._init_locations()

        self.config.add_win_size_changed_listener(self.set_window_size)
        self.config.add_view_changed_listener(self.set_view)

        self.set_view()

    def _init_values(self):
        self.model_loc = None
        self.view_loc = None
        self.proj_loc = None

        self.transform_loc = None
        self.switcher_loc = None

        self.view = None
        self.fov = FOV  # Field of View
        self.near_val = NEAR_VAL
        self.far_val = FAR_VAL
        self.a_color = []
        self.light_id = None

        self.projection_matrix = None

    def _init_locations(self):
        """
        can be partially or completely overridden.

        """
        self.model_loc = glGetUniformLocation(self.shader_id, "model")
        self.view_loc = glGetUniformLocation(self.shader_id, "view")
        self.proj_loc = glGetUniformLocation(self.shader_id, "projection")
        self.a_color = glGetUniformLocation(self.shader_id, "a_color")
        self.transform_loc = glGetUniformLocation(self.shader_id, "transform")

    @staticmethod
    def shader_from_file(file_name):
        """
        Retrieve shader from .glsl file
        :param file_name: Name of the shader to use
        :param file_name: ``str``
        :returns: the content of the shader to use

        """

        file_name = SHADER_DIR + file_name

        file_name = file_name.replace('\\', '/')

        with open(file_name, "r") as text:
            output = ""
            for line in text:
                output += line
        return output

    def compile_shader(self):
        """
        compiling the OpenGL shaders

        """

        vertex_source = self.shader_from_file(self.vertex_shader)
        fragment_source = self.shader_from_file(self.fragment_shader)

        if self.geometry_shader:
            geometry_source = self.shader_from_file(self.geometry_shader)
            shader_id = compileProgram(compileShader(vertex_source, GL_VERTEX_SHADER),
                                       compileShader(fragment_source, GL_FRAGMENT_SHADER),
                                       compileShader(geometry_source, GL_GEOMETRY_SHADER))
        else:
            shader_id = compileProgram(compileShader(vertex_source, GL_VERTEX_SHADER),
                                       compileShader(fragment_source, GL_FRAGMENT_SHADER))
        return shader_id

    def set_environment(self):
        """
        Set OpenGL environment

        """
        self.set_window_size()
        self.create_light_source()
        self.set_buffer_bits()

    def create_light_source(self):
        """
        Create OpenGL light source

        """
        if self.light_id:
            light_pos = Vector3([0.0, 0.0, 150.0])
            glUniform3f(self.light_id, light_pos.x, light_pos.y, light_pos.z)

    def set_buffer_bits(self):
        """
        Set OpenGL buffer bits

        """
        if self.switcher_loc:

            glUniform1i(self.switcher_loc, 1)

            # background black-ish
            glClearColor(0, 0.1, 0.1, 1)
            glClearStencil(0)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_STENCIL_TEST)
            glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Accept fragment if it closer to the camera than the last one
            glDepthFunc(GL_LESS)

    def set_window_size(self):
        """

        Prepare OpenGL projection Matrix

        """
        self.width = self.config.view.view_width
        self.height = self.config.view.view_height
        self.set_projection_matrix()

    def set_projection_matrix(self):
        """

        Set OpenGL projection Matrix

        """

        if self.height > 0:
            self.projection_matrix = \
                pyrr.matrix44.create_perspective_projection_matrix(self.fov,
                                                                   self.width / self.height,
                                                                   self.near_val, self.far_val)
            glUseProgram(self.shader_id)
            glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, self.projection_matrix)

    def set_view(self):
        glUseProgram(self.shader_id)
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.config.view_loc)

    @staticmethod
    def create_scale_matrix(scale=None):
        """

        Scale matrix to scale all objects

        :param scale: used for scaling an object
        :type scale: ``Vector3``

        """
        # Used to scale objects
        if scale is None:
            scale = Vector3([1.0, 1.0, 1.0])
        else:
            scale = Vector3(scale)

        return matrix44.create_from_scale(scale)

    def draw(self, object_index: int = 0, object_type: str = "", mesh_index: int = 0, indices_len=0,
             position: 'Vector3' = None, orientation: 'Quaternion' = None,
             scale: 'Vector3' = None, texture_id: int = 0, color: 'Vector4' = None,
             switch: int = 0, ):

        """

        Needs to be extended

        Rendering and preparing the OpenGL shader

        :param object_index: ID of the object
        :type object_index: ``int``
        :param object_type: Object type name
        :type object_type: ``str``
        :param mesh_index: ID of the Mesh
        :type mesh_index: ``int``
        :param indices_len: length of Indices
        :type indices_len: ``int``
        :param vertices: List of vertex coordinates
        :type indices: ``list``
        :param position: Position of the object
        :type position: ``Vector3``
        :param orientation: Orientation of the object
        :type orientation: ``Quaternion``
        :param scale: object scaling factor
        :type scale: ``Vector3``
        :param texture_id: ID of the texture to apply
        :type texture_id: ``int``
        :param color: color to apply
        :type color: ``Vector4``
        :param switch: OpenGL shader switch
        :type switch: ``int``
        """

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id,
                     color=color, switch=switch)

        # glUniform1i(self.switcher_loc, switch)
        glUniform4f(self.a_color, *color)

        # One way to draw with indexes
        glEnable(GL_CULL_FACE)
        glDrawElements(GL_POINTS, indices_len * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))

        # alternative possibility drawing arrays.....
        # glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glDisable(GL_CULL_FACE)
        glStencilFunc(GL_ALWAYS, object_index, -1)

