# -*- coding: utf-8 -*-

"""
    This shader is used to render the skybox

"""

from OpenGL.GL import *
from pyrr import Vector3, matrix44
from sphere_base.shader.base_shader import BaseShader


class SkyboxShader(BaseShader):

    def _init_locations(self):
        """
        Initiates the OpenGL locations

        """
        super()._init_locations()
        self.skybox = glGetUniformLocation(self.shader_id, "skybox")

    @staticmethod
    def load_texture_skybox(faces):
        """
        Loading into OpenGL textures for all six faces of the skybox

        :param faces: list with six images
        :type faces: ``list``

        """
        # Define all 6 faces of the skybox
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

        start = GL_TEXTURE_CUBE_MAP_POSITIVE_X

        for i in range(6):
            glTexImage2D(start + i, 0, GL_RGBA, faces[i].width, faces[i].height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE, faces[i].img_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def draw(self, object_index=0, object_type="", mesh_index=0, indices_len=0, position=None, orientation=None,
             scale=None, texture_id=0, color=None, switch=0, line_width=1):

        glUseProgram(self.shader_id)
        # glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.config.view_loc)

        glBindVertexArray(self.config.VAO[mesh_index])

        obj_pos = matrix44.create_from_translation(Vector3(self.config.uv.cam.xyz))
        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, obj_pos)

        glDepthMask(GL_FALSE)
        glDrawElements(GL_TRIANGLES, indices_len * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))

        # clean up code
        glDepthMask(GL_TRUE)


