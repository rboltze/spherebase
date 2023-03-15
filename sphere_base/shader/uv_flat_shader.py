# -*- coding: utf-8 -*-


from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.uv_base_shader import BaseShader


class FlatShader(BaseShader):

    def draw(self, object_index=0, object_type="", mesh_index=0, indices=None,
             vertices: list = None, position=None, orientation=None, scale=None, texture_id=0, color=None, switch=0):

        scale = [scale[0] * .97, scale[1] * .97, scale[2]]
        super().draw(object_index, object_type, mesh_index, indices, vertices,
                     position, orientation, scale, texture_id, color)

        if object_type == "rubber_band":
            glUniform4f(self.a_color, *color)

        glDrawElements(GL_TRIANGLES, len(indices) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))


