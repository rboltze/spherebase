# -*- coding: utf-8 -*-

"""
Dynamic shader. This is the dynamic shader class. It allows for dynamic shading lines and objects


"""

from OpenGL.GL import *
from pyrr import Vector3
from sphere_base.shader.base_shader import BaseShader


class EdgeShader(BaseShader):

    def draw(self, object_index: int = 0, object_type: str = "", mesh_index: int = 0, indices_len=0,
             position: 'Vector3' = None, orientation: 'Quaternion' = None,
             scale: 'Vector3' = None, texture_id: int = 0, color: 'Vector4' = None,
             switch: int = 0, ):

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id,
                     color=color, switch=switch)

        # glUniform1i(self.switcher_loc, switch)
        glUniform4f(self.a_color, *color)

        # One way to draw with indexes
        glEnable(GL_CULL_FACE)
        glDrawElements(GL_POINTS, indices_len * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))

        # alternative possibility drawing arrays.....
        # glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glDisable(GL_CULL_FACE)
        glStencilFunc(GL_ALWAYS, object_index, -1)
