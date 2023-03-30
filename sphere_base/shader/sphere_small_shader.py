# -*- coding: utf-8 -*-

"""
This class contains the class that colors the small overview spheres. It inherits from the base shader class.

"""

from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.base_shader import BaseShader


class SphereSmallShader(BaseShader):

    def _init_locations(self):
        """
        Initiates the OpenGL locations

        """
        super()._init_locations()
        self.switcher_loc = glGetUniformLocation(self.shader_id, "switcher")

    def draw(self, object_index=0, object_type="", mesh_index=0, indices_len=0, indices=None, vertices=None, position=None,
             orientation=None, scale=None, texture_id=0, color=None, switch=0):

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len, indices=indices,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id,
                     color=color, switch=switch)

        glUniform1i(self.switcher_loc, 2)

        glUniform4f(self.a_color, *color)
        glEnable(GL_CULL_FACE)
        glDrawElements(GL_TRIANGLES, len(indices) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glDisable(GL_CULL_FACE)
