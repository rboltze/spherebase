# -*- coding: utf-8 -*-

"""
Circle shader module contains the circle shader class which extends the base shader.

the circle shader uses an OpenGL geometry shader to draw circles around node discs and sockets.

"""

from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.base_shader import BaseShader
from pyrr import matrix44


class CrossShader(BaseShader):
    """
    Class representing the circle shader.

    """

    def __init__(self, parent, vertex_shader=None, fragment_shader=None, geometry_shader=None):
        super().__init__(parent, vertex_shader, fragment_shader, geometry_shader)
        """
        Constructor of the ``circle shader`` class.

        :param parent: The parent (model) that initiates the class.

        :Instance Variables:

            - **line_width** - width of the circle line
            - **scale** - scaling of the circle

        """

        self.line_width = 1
        self.scale = [1.0, 1.0, 1.0]

    def draw(self, object_index=0, object_type="", mesh_index=0, indices_len=0, indices=None,
             position=None, orientation=None, scale=None,
             texture_id=0, color=None, switch=0):

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len, indices=indices,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id,
                     color=color, switch=switch)

        glLineWidth(self.line_width)

        rm = matrix44.create_from_inverse_of_quaternion(orientation)
        sm = self.create_scale_matrix(scale)

        # combined transformation matrix
        tm = matrix44.multiply(sm, rm)

        glUniformMatrix4fv(self.transform_loc, 1, GL_FALSE, tm)

        glDrawElements(GL_POINTS, len(indices) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glStencilFunc(GL_ALWAYS, object_index, -1)
        glLineWidth(1)
