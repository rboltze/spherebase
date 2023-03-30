# -*- coding: utf-8 -*-

"""
Square shader module. This module contains the Node shader class which inherits from the base shader class.
It is used to render squares like the one used in the rubber band selection box.

"""

from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.base_shader import BaseShader


class SquareShader(BaseShader):
    def __init__(self, parent, vertex_shader=None, fragment_shader=None, geometry_shader=None):
        super().__init__(parent, vertex_shader, fragment_shader, geometry_shader)
        """
        Square shader constructor calls the constructor of the base shader

        """

        self.line_width = 1
        self.scale = [1.0, 1.0, 1.0]

    def _init_locations(self):
        """
        Adds a scale location to the geometric shader to. This scale is the fraction used to
        correctly scale the border box of size 1 by 1

        """
        super()._init_locations()
        self.scale_loc = glGetUniformLocation(self.shader_id, "scale")

    def draw(self, object_index=0, object_type="", mesh_index=0, indices_len=0, indices=None, position=None,
             orientation=None, scale=None, texture_id=0, color=None, switch=0):

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len, indices=indices,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id,
                     color=color, switch=switch)

        glLineWidth(self.line_width)
        glUniform3f(self.scale_loc, *scale)  # sending the size of the box to the geometric shader

        glDrawElements(GL_POINTS, len(indices) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glStencilFunc(GL_ALWAYS, object_index, -1)
        glLineWidth(1)
