# -*- coding: utf-8 -*-

"""
Dynamic shader. This is the dynamic shader class. It allows for dynamic shading lines and objects


"""

from PyQt6.QtGui import *
from OpenGL.GL import *
from sphere_base.shader.base_shader import BaseShader


class EdgeShader(BaseShader):

    def __init__(self, parent, vertex_shader=None, fragment_shader=None, geometry_shader=None, *args, **kwargs):
        super().__init__(parent, vertex_shader, fragment_shader, geometry_shader)
        self.context = QOpenGLContext.currentContext()

    def draw(self, object_index: int = 0, object_type: str = "", mesh_index: int = 0, indices_len=0, position=None,
             orientation=None, scale=None, texture_id: int = 0, color=None, switch: int = 0, line_width=1):

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id, color=color,
                     switch=switch, line_width=line_width)

        # self.context.makeCurrent(self.uv_widget.surface)
        self.use()
        glBindVertexArray(self.config.VAO[mesh_index])

        glUniform4f(self.a_color, *color)
        glLineWidth(line_width)
        glEnable(GL_CULL_FACE)
        glEnable(GL_POLYGON_SMOOTH)
        glEnable(GL_LINE_SMOOTH)

        glDrawElements(GL_LINE_STRIP, indices_len, GL_UNSIGNED_INT, ctypes.c_void_p(0))

        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_POLYGON_SMOOTH)
        glDisable(GL_CULL_FACE)
