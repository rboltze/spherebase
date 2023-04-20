# -*- coding: utf-8 -*-

"""
Sphere edge shader module. This module contains the edge shader class which inherits from the base shader class.
It is used to render edges between spheres.

It works different from the other shaders as it does not use indices.

    - Each shader instance holds one edge


"""

from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.base_shader import BaseShader
import numpy as np


class SphereEdgeShader(BaseShader):
    def __init__(self, parent, vertex_shader=None, fragment_shader=None, geometry_shader=None):
        super().__init__(parent, vertex_shader=vertex_shader, fragment_shader=fragment_shader,
                         geometry_shader=geometry_shader)

    def _init_locations(self):
        """
        Initiates the OpenGL locations

        """
        super()._init_locations()
        self.switcher_loc = glGetUniformLocation(self.shader_id, "switcher")
        self.vertices = []
        self.buffer = np.array(self.vertices, dtype=np.float32)
        self.vertices = np.array(self.vertices, dtype=np.float32)

    def draw(self, object_index=0, object_type="", mesh_index=0, indices_len=0, position=None, orientation=None,
             scale=None, texture_id=0, color=None, switch=0, line_width=1):

        print("mesh_index", self.vertices)
        color = [0, 0, 0, 1]

        print("----------------- variables for drawing -----------------")
        print("object_index", object_index)
        print("object_type", object_type)
        print("mesh_index", mesh_index)
        print("indices_len", indices_len)
        print("position", position)
        print("orientation", orientation)
        print("scale", scale)
        print("texture_id", texture_id)
        print("color", color)
        print("switch", switch, "\n")


        # super().draw(object_index=object_index,
        #              object_type=object_type,
        #              mesh_index=mesh_index,
        #              indices_len=indices_len,
        #              position=position,
        #              orientation=orientation,
        #              scale=scale,
        #              texture_id=texture_id,
        #              color=color,
        #              switch=switch)

        # ------------------------------

        glBindVertexArray(self.mesh_index)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_id)
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices), self.vertices, GL_STATIC_DRAW)

        # print(mesh_index, self.vertices)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.buffer.itemsize * 3, ctypes.c_void_p(0))
        # print("mesh_index", mesh_index, self.config.EBO[mesh_index])
        # ------------------------------

        glBindVertexArray(self.config.VAO[mesh_index])

        # enable blending
        glEnable(GL_BLEND)
        glUniform4f(self.a_color, *color)
        glDrawArrays(GL_LINES, 0, 2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
