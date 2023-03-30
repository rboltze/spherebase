# -*- coding: utf-8 -*-

"""
**mesh** - Instance of :class:`~sphere_iot.uv_models.Mesh`
"""

import numpy as np
from sphere_base.utils import dump_exception


class Mesh:
    def __init__(self, model, mesh_id, vertices, indices, buffer):
        """
        Constructor of the ``Mesh`` class. Holds and draws a single mesh.

        :param model: the :class:`~sphere_iot.uv_models.Model` this ``Mesh`` belongs to.
        :type model: :class:`~sphere_iot.uv_models.Model`
        :param mesh_id: id of this mesh.
        :type mesh_id: ``int``
        :param vertices: Array of Vertex positions
        :type vertices: ``np.array``
        :param indices: Indices array
        :type indices: ``np.array``
        :param buffer: Buffer array
        :type buffer: ``np.array``

        :Instance Variables:

            - **model** - The :class:`~sphere_iot.uv_models.Model` this ``Mesh`` belongs to.
            - **models** - :class:`~sphere_iot.uv_models.Models`.
            - **shader** - A dedicated shader for this ``Mesh``.
            - **model_id** - id of the `:class:`~sphere_iot.uv_models.Model` this ``Mesh`` belongs to.
            - **mesh_id** - id of the Mesh.

        """
        self.model = model
        self.shader = model.shader
        self.model_id = model.id
        self.mesh_id = mesh_id

        self.vertices = np.array(vertices, dtype=np.float32)  # vertex coordinates
        self.indices = np.array(indices, dtype='uint32')
        self.indices_len = len(self.indices)
        self.buffer = np.array(buffer, dtype=np.float32)

    def draw(self, shader: 'Shader', model_id: int, position: 'Vector3', orientation: 'Quaternion', scale: list = None,
             texture_id: int = 0, color: list = None, switch: int = 0):
        """
        Sending the ``Mesh`` with all the parameters to the dedicated shader.

        :param shader: Each ``Model`` gets its own ``Shader`` allocated.
        :type shader: :class:`~sphere_iot.shader.uv_base_shader.BaseShader`.
        :param model_id: The id of :class:`~sphere_iot.uv_models.Model` this ``Mesh`` is on.
        :type model_id: ``int``
        :param position: Position of the :class:`~sphere_iot.uv_models.Model`
        :type position: ``Vector3``
        :param orientation: The direction the :class:`~sphere_iot.uv_models.Model` is pointing at
        :type orientation: ``Quaternion``
        :param scale: ``vector`` used to scale the :class:`~sphere_iot.uv_models.Model`
        :type scale: ``Vector3`` scale of the Mesh
        :param texture_id: The ``id`` of the texture to put on the ``Mesh``.
        :type texture_id: ``int``
        :param color: ``rbg array``
        :type color: ``Array``
        :param switch: Switch used in the shader to switch from one behaviour to another.
        :type switch: ``int``
        """

        try:
            shader.draw(
                         object_index=model_id,
                         object_type=self.model.type,
                         mesh_index=self.mesh_id,
                         indices_len=self.indices_len,
                         position=position,
                         orientation=orientation,
                         scale=scale,
                         texture_id=texture_id,
                         color=color,
                         switch=switch
                         )
        except Exception as e:
            dump_exception(e)
