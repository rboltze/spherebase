# -*- coding: utf-8 -*-

"""
Default shader. This module contains the Default shader class.

"""

from sphere_base.shader.uv_base_shader import BaseShader

DEBUG = False


class DefaultShader(BaseShader):

    def __init__(self, parent, vertex_shader="vert_default.glsl", fragment_shader="frag_default.glsl", geometry_shader=None):

        super().__init__(parent, vertex_shader=vertex_shader, fragment_shader=fragment_shader, geometry_shader=geometry_shader)

    def set_view(self):
        # overriding base class function avoid crash
        pass

