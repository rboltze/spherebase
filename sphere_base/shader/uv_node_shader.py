# -*- coding: utf-8 -*-

"""
Node shader module. This module contains the Node shader class which inherits from the base shader class.
It is used to render nodes

"""

from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.uv_base_shader import BaseShader


class NodeShader(BaseShader):

    def _init_locations(self):
        """
        Initiates the OpenGL locations

        """
        super()._init_locations()
        self.switcher_loc = glGetUniformLocation(self.shader_id, "switcher")

    def draw(self, object_index=0, object_type="", mesh_index=0, indices=None,
             vertices=None, position=None, orientation=None, scale=None, texture_id=0, color=None, switch=0):

        super().draw(object_index, object_type, mesh_index, indices, vertices,
                     position, orientation, scale, texture_id, color)

        glUniform1i(self.switcher_loc, switch)
        glDrawElements(GL_TRIANGLES, len(indices) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))


