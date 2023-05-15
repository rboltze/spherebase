# -*- coding: utf-8 -*-

"""
Base shader. This module contains the base shader class. It needs to be inherited and extended.

"""

from OpenGL.GL import *
from pyrr import Vector3, matrix44
import pyrr
from sphere_base.constants import *
from sphere_base.utils import dump_exception
from importlib_resources import files
import sphere_base.model.resources.shaders

DEBUG = False


class BaseShader:

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

        self.projection_matrix = None

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

        try:

            with files(sphere_base.model.resources.shaders).joinpath(file_name).open('r') as text:
                output = ""
                for line in text:
                    output += line
            return output
        except Exception as e:
            dump_exception(e)

    # activate the shader
    # ------------------------------------------------------------------------
    def use(self) -> None:
        glUseProgram(self.shader_id)

    def compile_shader(self):
        """
        compiling the OpenGL shaders

        """
        geometry_source, geometry = None, None

        vertex_source = self.shader_from_file(self.vertex_shader)
        fragment_source = self.shader_from_file(self.fragment_shader)

        if self.geometry_shader:
            geometry_source = self.shader_from_file(self.geometry_shader)

        # 2. compile shaders
        # vertex shader
        vertex = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex, vertex_source)
        glCompileShader(vertex)
        self.check_compile_errors(vertex, "VERTEX")

        # fragment Shader
        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment, fragment_source)
        glCompileShader(fragment)
        self.check_compile_errors(fragment, "FRAGMENT")

        # geometry shader
        if self.geometry_shader:
            geometry = glCreateShader(GL_GEOMETRY_SHADER)
            glShaderSource(geometry, geometry_source)
            glCompileShader(geometry)
            self.check_compile_errors(geometry, "GEOMETRY")

        # shader Program
        shader_id = glCreateProgram()
        glAttachShader(shader_id, vertex)
        glAttachShader(shader_id, fragment)

        if self.geometry_shader:
            glAttachShader(shader_id, geometry)

        glLinkProgram(shader_id)
        self.check_compile_errors(shader_id, "PROGRAM")
        # delete the shaders as they're linked into our program now and no longer necessary
        glDeleteShader(vertex)
        glDeleteShader(fragment)

        if self.geometry_shader:
            glDeleteShader(geometry)


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
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

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
        # glUseProgram(self.shader_id)
        self.use()
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

    def draw(self, object_index: int = 0, object_type: str = "", mesh_index: int = 0, indices_len=0, position=None,
             orientation=None, scale: 'Vector3' = None, texture_id: int = 0, color=None, switch: int = 0, line_width=1):

        """

        Needs to be extended

        Rendering and preparing the OpenGL shader

        :param line_width:
        :param object_index: ID of the object
        :type object_index: ``int``
        :param object_type: Object type name
        :type object_type: ``str``
        :param mesh_index: ID of the Mesh
        :type mesh_index: ``int``
        :param indices_len: length of Indices
        :type indices_len: ``int``
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

        if DEBUG:
            if object_type == "edge1":
                print("-------------- DRAW MESH -----------")
                print("mesh_id", mesh_index)
                print("position", position)
                print("orientation", orientation)
                print("scale", scale)
                print("texture_id", texture_id, "\n")

        self.use()
        glBindVertexArray(self.config.VAO[mesh_index])

        # if texture_id > 0:
        glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, self.config.textures[texture_id])
        glBindTexture(GL_TEXTURE_2D, self.config.get_texture(texture_id))
        obj_pos = matrix44.create_from_translation(Vector3(position))
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, obj_pos)

        if color:
            glUniform4f(self.a_color, *color)

        rm = matrix44.create_from_inverse_of_quaternion(orientation)
        sm = self.create_scale_matrix(scale)

        # combined transformation matrix rotation and scale
        tm = matrix44.multiply(sm, rm)
        glUniformMatrix4fv(self.transform_loc, 1, GL_FALSE, tm)

    def draw_edge(self, points, width=1.5, color=None, dotted=False, switch=0):
        """
        Drawing edges. Using direct Open GL

        .. Warning::

            This method is using obsolete direct OpenGL instead of modern OpenGL.
            This needs to be updated in a future iteration.

        """
        return NotImplemented

    @staticmethod
    def check_compile_errors(shader: int, activity_type: str) -> None:
        if activity_type != "PROGRAM":
            success = glGetShaderiv(shader, GL_COMPILE_STATUS)
            if not success:
                info_log = glGetShaderInfoLog(shader)
                print(
                    "ERROR::SHADER_COMPILATION_ERROR of type: " + activity_type + "\n" + info_log.decode() + "\n -- --------------------------------------------------- -- ")
        else:
            success = glGetProgramiv(shader, GL_LINK_STATUS)
            if not success:
                info_log = glGetProgramInfoLog(shader)
                print(
                    "ERROR::PROGRAM_LINKING_ERROR of type: " + activity_type + "\n" + info_log.decode() + "\n -- --------------------------------------------------- -- ")


