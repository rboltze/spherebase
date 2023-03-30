# -*- coding: utf-8 -*-


from OpenGL.GL import *
from OpenGL.GLU import *
from sphere_base.shader.base_shader import BaseShader


class FlatShader(BaseShader):

    def draw(self, object_index=0, object_type="", mesh_index=0, indices_len=0, indices=None,
             position=None, orientation=None, scale=None, texture_id=0,
             color=None, switch=0):

        scale = [scale[0] * .97, scale[1] * .97, scale[2]]

        super().draw(object_index=object_index, object_type=object_type, mesh_index=mesh_index, indices_len=indices_len, indices=indices,
                     position=position, orientation=orientation, scale=scale, texture_id=texture_id,
                     color=color, switch=switch)

        if object_type == "rubber_band":
            glUniform4f(self.a_color, *color)

        glDrawElements(GL_TRIANGLES, len(indices) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
