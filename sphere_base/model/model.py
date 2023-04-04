# -*- coding: utf-8 -*-

# Do not remove these!!!
# -------------- these will be dynamically late loaded! -----------------------
from sphere_base.shader.skybox_shader import SkyboxShader
from sphere_base.shader.sphere_shader import SphereShader
from sphere_base.shader.node_shader import NodeShader
from sphere_base.shader.socket_shader import SocketShader
from sphere_base.shader.flat_shader import FlatShader
from sphere_base.shader.default_shader import DefaultShader
from sphere_base.shader.circle_shader import CircleShader
from sphere_base.shader.square_shader import SquareShader
from sphere_base.shader.sphere_edge_shader import SphereEdgeShader
from sphere_base.shader.cross_shader import CrossShader
from sphere_base.shader.holo_sphere_shader import HoloSphereShader
from sphere_base.shader.sphere_small_shader import SphereSmallShader
from sphere_base.shader.Edge_shader import EdgeShader
# -----------------------------------------------------------------------

from sphere_base.sphere_universe_base.suv_graphic_item import GraphicItem
from sphere_base.model.mesh import Mesh
from sphere_base.model.obj_file_loader import ObjectFileLoader
import pathlib

DEBUG = True


class Model(GraphicItem):
    Mesh_class = Mesh

    """
    Class representing a ``Model``. 
    """

    def __init__(self, models, model_id, model_name, obj_file=None, shader=None, vertex_shader=None,
                 fragment_shader=None, geometry_shader=None):
        """

        Contructor of the ``Model`` class. Creates a new model from data received.

        :param models: Instance of :class:`~sphere_iot.uv_models.Models`
        :type models: :class:`~sphere_iot.uv_models.Models`
        :param model_id: The ``id`` of this ``model``
        :type model_id: ``int``
        :param model_name: The ``Name`` of this ``model``
        :type model_name: ´´str´´
        :param obj_file: filename
        :type obj_file: ´´str´´
        :param shader: The ``shader`` to use for this ``Model``
        :type shader:  :class:`~sphere_iot.shader.uv_base_shader.Shader`

        :Instance Attributes:

            - **Mesh** - Instance of :class:`~sphere_iot.uv_models.Mesh`

        :Instance Variables:

            - **config** - :class:`~sphere_iot.uv_config.UvConfig`
            - **uv** - :class:`~sphere_iot.uv_universe.Universe`
            - **models** - :class:`~sphere_iot.uv_models.Models`
            - **model_id** - ``int`` id of this ``Model``
            - **shader** - specific class inherited from :class:`~sphere_iot.shader.uv_base_shader.Shader`
            - **model** - ``model`` loaded

        .. note::

            Each ``Model`` has its own shader.

            The shader name is stored with the data that is used to load the Model.
            In this implementation of the library there can be only one shader per model.

            A model can have many Meshes which all use the same shader.

        """
        super().__init__(self, model_name)

        self.config = models.config
        self.uv = models.uv
        self.models = models
        self.model_id = model_id if model_id else self.id
        self.name = model_name

        self.meshes = []  # list holding instances of mesh class
        self.texture_coordinates = []

        # passing shader source file names to the shader
        self.shader = eval(shader)(self, vertex_shader, fragment_shader, geometry_shader)

        if ".obj" == pathlib.Path(obj_file).suffix:
            self.loader = ObjectFileLoader(self, config=self.config)
            self.meshes = self.loader.get_meshes(obj_file)
        else:
            pass
            # No object file passed, meshes need to be loaded later.
            self.loader = ObjectFileLoader(self, config=self.config)
            self.meshes = self.loader.create_empty_mesh()

    def get_number_of_meshes_in_model(self) -> int:
        """
        Returns the number of ``Meshes`` in this ``Model``
        """
        return len(self.meshes)

    def draw(self, parent, texture_id=0, color=None, switch=0, scale=None):
        """
        Draw all ``Meshes`` for this ``Model``.

        :param parent: Parent object where this model was created.
        :param texture_id: Id of the ``Texture`` that needs to be applied.
        :type texture_id: ``int``
        :param color: color array rgb with alpha value
        :type color: ``Vector4``
        :param switch: Used in the shader to switch from one mode to another
        :type switch: ``int``
        :param scale: ``list`` used for scaling the model
        :type scale:   ``list``

        """
        # if self.model_id in [12]:
        #     # print("model_id", self.model_id, self.meshes[0].vertices)
        #     print("model_id", self.model_id, parent.orientation, parent.xyz)
        #     for mesh in self.meshes:
        #         print(mesh.vertices)

        # draws all meshes
        color = color if color else [1.0, 1.0, 1.0, 1.0]
        for mesh in self.meshes:
            mesh.draw(self.shader,
                      model_id=self.model_id,
                      position=parent.xyz,
                      orientation=parent.orientation,
                      scale=scale if scale else parent.scale,
                      texture_id=texture_id,
                      color=color,
                      switch=switch
                      )

# Do not remove these!!!
# from sphere_base.shader.uv_skybox_shader import SkyboxShader
# from sphere_base.shader.uv_sphere_shader import SphereShader
# from sphere_base.shader.uv_node_shader import NodeShader
# from sphere_base.shader.uv_socket_shader import SocketShader
# from sphere_base.shader.uv_flat_shader import FlatShader
# from sphere_base.shader.uv_default_shader import DefaultShader
# from sphere_base.shader.uv_circle_shader import CircleShader
# from sphere_base.shader.uv_square_shader import SquareShader
# from sphere_base.shader.uv_sphere_edge_shader import SphereEdgeShader
# from sphere_base.shader.uv_cross_shader import CrossShader
# from sphere_base.shader.uv_holo_sphere_shader import HoloSphereShader
# from sphere_base.shader.uv_sphere_small_shader import SphereSmallShader
