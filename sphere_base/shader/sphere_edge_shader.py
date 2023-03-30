# -*- coding: utf-8 -*-

"""
Sphere edge shader module. This module contains the edge shader class which inherits from the base shader class.
It is used to render edges between spheres. It does not yet render any edges on the surface of spheres.

"""

from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.base_shader import BaseShader


class SphereEdgeShader(BaseShader):

    def _init_locations(self):
        """
        Initiates the OpenGL locations

        """
        super()._init_locations()
        self.switcher_loc = glGetUniformLocation(self.shader_id, "switcher")

    def draw(self, object_index=0, object_type="", mesh_index=0, indices=None, position=None,
             orientation=None, scale=None, texture_id=0, color=None, switch=0):
        print("here")
        color = [1, 1, 1, .1]

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices=indices,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id,
                     color=color, switch=switch)

        switch = 2

        glUniform1i(self.switcher_loc, switch)

        # enable blending
        glEnable(GL_BLEND)
        glUniform4f(self.a_color, *color)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDrawElements(GL_LINES, len(indices) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        # glDrawArrays(GL_LINES, 0, 2)
