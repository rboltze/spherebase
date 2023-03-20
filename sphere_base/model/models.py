# -*- coding: utf-8 -*-

"""
The ``Models`` class holds all textures and all models used in this implementation. This includes the skybox.
"""

from collections import namedtuple
from sphere_base.sphere_universe_base.suv_constants import *
from PIL import Image
from OpenGL.GL import *
from sphere_base.model.model import Model


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

        self.load_textures_into_opengl()
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
            model_file = MESH_DIR + MODELS[_name]["model_file_name"]
            shader = MODELS[_name]["shader"]
            vertex_shader = MODELS[_name]["vertex_shader"]
            fragment_shader = MODELS[_name]["fragment_shader"]
            geometry_shader = MODELS[_name]["geometry_shader"]
            geometry_shader = None if geometry_shader == "none" else geometry_shader

            # Create a new model
            model = self.Model(self, model_id, model_name, model_file, shader, vertex_shader, fragment_shader,
                               geometry_shader)

            # add model to internal list
            self._models.append(model)

            # calculate total number of meshes
            no_of_meshes += model.get_number_of_meshes_in_model()

        self.create_buffers(no_of_meshes)

    def create_buffers(self, size):
        """
        Creates the 'size' number of Vertex Array Objects, Vertex Buffer Objects and Element Buffer Objects

        :param size: Number of ``buffers`` to create
        :type size: ``int``

        """
        self.config.VAO = glGenVertexArrays(size)
        self.config.VBO = glGenBuffers(size)
        self.config.EBO = glGenBuffers(size)

    def create_all_meshes(self):
        """
        Create all meshes of all models
        """
        for model in self._models:
            for mesh in model.meshes:
                self.load_mesh_into_opengl(mesh.mesh_id, mesh.buffer, mesh.indices, mesh.shader)

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

    # def get_all_textures(self):
    #     """
    #     Returns a list with named tuples containing all textures
    #
    #     """
    #
    #     textures = []
    #     for t in TEXTURES:
    #         id, name, type, path = t[0], t[1], t[2], TEXTURE_DIR + t[3]
    #         textures.append(self.Texture(id, name, type, path))
    #
    #     return textures

    def load_mesh_into_opengl(self, mesh_id=0, buffer=[], indices=[], shader=""):
        """
        Loads a single mesh into Opengl buffers

        :param mesh_id: id of the :class:`~sphere_iot.uv_models.Mesh` to store into ``OpenGl``
        :type mesh_id: ``int``
        :param buffer: Buffer array
        :type buffer: ``np.array``
        :param indices: Indices array
        :type indices: ``np.array``
        :param shader: 'Shader' to use for this :class:`~sphere_iot.uv_models.Mesh`
        :type shader: Overridden version of :class:`~sphere_iot.shader.uv_base_shader.BaseShader`

        """

        glBindVertexArray(self.config.VAO[mesh_id])

        # vertex Buffer Object
        glBindBuffer(GL_ARRAY_BUFFER, self.config.VBO[mesh_id])
        glBufferData(GL_ARRAY_BUFFER, buffer.nbytes, buffer, GL_STATIC_DRAW)

        # element Buffer Object
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.config.EBO[mesh_id])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        # vertex positions
        # Enable the Vertex Attribute so that OpenGL knows to use it
        glEnableVertexAttribArray(0)
        # Configure the Vertex Attribute so that OpenGL knows how to read the VBO
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, buffer.itemsize * 8, ctypes.c_void_p(0))

        # textures
        # Enable the Vertex Attribute so that OpenGL knows to use it
        glEnableVertexAttribArray(1)
        # Configure the Vertex Attribute so that OpenGL knows how to read the VBO
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, buffer.itemsize * 8, ctypes.c_void_p(12))

        # normals
        # Enable the Vertex Attribute so that OpenGL knows to use it
        glEnableVertexAttribArray(2)
        # Configure the Vertex Attribute so that OpenGL knows how to read the VBO
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, buffer.itemsize * 8, ctypes.c_void_p(20))

        #  Bind the VBO, VAO to 0 so that we don't accidentally modify the VAO and VBO we created
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        # Bind the EBO to 0 so that we don't accidentally modify it
        # MAKE SURE TO UNBIND IT AFTER UNBINDING THE VAO, as the EBO is linked in the VAO
        # This does not apply to the VBO because the VBO is already linked to the VAO during glVertexAttribPointer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        shader.set_environment()

    def load_textures_into_opengl(self):
        """
        Receives a list of ``named tuples`` representing all textures used in this implementation
        and loads them into OpenGl

        :param textures: list of textures
        :type textures: list of ``named tuples``

        """
        # print("len", len(textures))
        # print("len", len(self.uv.config.all_textures))
        self.config.textures = glGenTextures(len(self.uv.config.all_textures))
        # self.config.textures = glGenTextures(len(textures))

        # self.load_texture_into_opengl('..//sphere_base/model/resources/sphere_textures/grid1.jpg', 0)

        for index, item in enumerate(self.uv.config.all_textures.values()):
            # print(index, item['file_dir_name'], item['texture_id'])
            self.load_texture_into_opengl(item['file_dir_name'], item['texture_id'] + 1)

            # # print("here")
            # for i, texture in enumerate(textures):
            #     if texture:
            #         pass
            #         # self.load_texture_into_opengl(texture.path, self.config.textures[i])
            #         # print("here", texture.path, self.config.textures[i])

            # self.config.create_texture_by_name_dictionary()

        """
                : note

                A separate dictionary of textures is created in :class:`~sphere_iot.uv_config.UvConfig`.
                This is used to find the id of a texture in OpenGl by its 'img_name'.

        """

    @staticmethod
    def load_texture_into_opengl(texture_path, texture_id):
        """
        Load a texture into ``OpenGl``

        :param texture_path: Texture path and texture name
        :type texture_path: ``str``
        :param texture_id: Id of the texture to load
        :type texture_id: ``int``

        """

        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Mip_maps
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

        # load image
        img = Image.open(texture_path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = img.convert("RGBA").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #  Bind to 0 so it cannot be changed by mistake
        glBindTexture(GL_TEXTURE_2D, 0)
