# -*- coding: utf-8 -*-

"""
The ``Models`` class holds all textures and all models used in this implementation. This includes the skybox.
"""

from collections import namedtuple
from sphere_base.constants import *
from sphere_base.model.model import Model
from sphere_base.model.obj_file_loader import ObjectFileLoader


class Models:
    Model_class = Model

    Texture = namedtuple("texture", "id, name, type, path")

    def __init__(self, universe):
        """
        Constructor of the ``Models`` class.

        :param universe: reference to the :class:`~sphere_iot.uv_universe.Universe`
        :type universe: :class:`~sphere_iot.uv_universe.Universe`

        :Instance Attributes:

            - **Model** - Instance of :class:`~sphere_iot.uv_models.Model`

        :Instance Variables:

            - **config** - :class:`~sphere_iot.uv_config.UvConfig`
            - **uv** - :class:`~sphere_iot.uv_universe.Universe`
            - **mesh_id** - Holds the last ``Mesh id`` Created. Functions as a counter to create new id`s

        """

        self.uv = universe
        self.config = universe.config

        self._models = []
        self.loader = ObjectFileLoader(config=self.config)
        self.loader.load_all_textures_into_opengl()
        self.Model = self.__class__.Model_class
        self.setup_models()
        self.create_all_meshes()

    def setup_models(self):
        """
        Initiate all models from stored data
        """
        no_of_meshes = 0

        # iterate through all models from the Model dictionary
        for _name in MODELS.keys():
            model_name = _name
            model_id = MODELS[_name]["model_id"]
            # model_file = MESH_DIR + MODELS[_name]["model_file_name"]
            model_file = MODELS[_name]["model_file_name"]
            shader = MODELS[_name]["shader"]
            vertex_shader = MODELS[_name]["vertex_shader"]
            fragment_shader = MODELS[_name]["fragment_shader"]
            geometry_shader = None if MODELS[_name]["geometry_shader"] == "none" else MODELS[_name]["geometry_shader"]

            if 'edge' not in model_name:
                # Create a new model
                model = self.Model(self, model_id, model_name, model_file, shader, vertex_shader, fragment_shader,
                                   geometry_shader)

                # add model to internal list
                self._models.append(model)

                # calculate total number of meshes
                no_of_meshes += model.get_number_of_meshes_in_model()

        self.loader.create_buffers(no_of_meshes)

    def create_all_meshes(self):
        """
        Create all meshes of all models
        """
        for model in self._models:
            for mesh in model.meshes:
                self.loader.load_mesh_into_opengl(mesh.mesh_id, mesh.buffer, mesh.indices, mesh.shader)
                mesh.save_memory()

    def get_model(self, model_type) -> 'Model':
        """
        Returns a model by its name

        :param model_type: name of the model to retrieve
        :type model_type: ``str``
        :returns: :class:`~sphere_iot.uv_models.Model`
        """

        for model in self._models:
            if model.type and model.type == model_type:
                return model


