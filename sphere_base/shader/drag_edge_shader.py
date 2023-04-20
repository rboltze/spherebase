# -*- coding: utf-8 -*-

"""
Dynamic shader. This is the dynamic shader class. It allows for dynamic shading lines and objects


"""

from OpenGL.GL import *
from sphere_base.shader.base_shader import BaseShader


class DragEdgeShader(BaseShader):

    def _init_locations(self):
        """
        Initiates the OpenGL locations

        """
        super()._init_locations()
        self.light_id = glGetUniformLocation(self.shader_id, "LightPosition_world_space")
        self.switcher_loc = glGetUniformLocation(self.shader_id, "switcher")

    def draw_edge(self, points, width=1.5, color=None, dotted=False, switch=0):
        """
        Drawing edges. Using direct Open GL

        :param points: list of Vector3 points positions
        :type points: ``list``
        :param width: width of the line
        :type width: ``float``
        :param color: color of the line
        :type color: ``Vector4``
        :param dotted: is the line dotted
        :type dotted: ``bool``
        :param switch: OpenGL switch
        :type switch: ``int``

        .. Warning::

            This method is using obsolete direct OpenGL instead of modern OpenGL.
            This needs to be updated in a future iteration, however this will not impact performance, as there
            is only one edge being dragged at any one moment.

        """
        # drawing lines
        glUseProgram(self.shader_id)  # using the standard shader
        glUniform1i(self.switcher_loc, 3)  # switch to use fragment and vertex shader for lines
        glLineWidth(width)

        if color:
            # enable blending
            glUniform4f(self.a_color, *color)
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        if dotted:
            # dotted line for dragging
            glLineStipple(4, 0xAAAA)
            glEnable(GL_LINE_STIPPLE)
        else:
            # reset to normal
            glDisable(GL_LINE_STIPPLE)

        glBegin(GL_LINE_STRIP)
        for point in points:
            glVertex3f(point[0], point[1], point[2])
        glEnd()
        glDisable(GL_LINE_STIPPLE)  # just in case ....
        glLineWidth(1)