# -*- coding: utf-8 -*-

"""
Socket shader module. This module contains the Socket shader class which inherits from the base shader class.
It is used to render nodes

"""

from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.base_shader import BaseShader


class SocketShader(BaseShader):

    def _init_locations(self):
        """
        Initiates the OpenGL locations

        """
        super()._init_locations()
        self.switcher_loc = glGetUniformLocation(self.shader_id, "switcher")

    def draw(self, object_index=0, object_type="", mesh_index=0, indices_len=0, position=None, orientation=None,
             scale=None, texture_id=0, color=None, switch=0, line_width=1):

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id, color=color,
                     switch=switch, line_width=line_width)

        # switch = SHADER_SWITCH[object_type]
        glUniform1i(self.switcher_loc, 2)

        glUniform4f(self.a_color, *color)

        glDrawElements(GL_TRIANGLES, indices_len * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
