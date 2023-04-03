# -*- coding: utf-8 -*-

from sphere_base.model.mesh import Mesh
from sphere_base.utils import dump_exception
from OpenGL.GL import *
from PIL import Image

DEBUG = False

"""
Wavefront .obj file loader, replacing PyAssimp file loader which could not be installed on MAC.
This replacement file loader is based on code from an OpenGl youtube course (ES
OpenGL in python e15 - loading 3D .obj files) and only works with .obj wavefront files.

"""


class ObjectFileLoader:
    Mesh_class = Mesh

    def __init__(self, model=None, config=None):
        self.model = model
        self.config = config
        self.index = 0

    def create_buffers(self, size=1):
        """
        Creates the 'size' number of Vertex Array Objects, Vertex Buffer Objects and Element Buffer Objects

        :param size: Number of ``buffers`` to create
        :type size: ``int``

        """
        VAO = glGenVertexArrays(size)
        VBO = glGenBuffers(size)
        EBO = glGenBuffers(size)

        if size == 1:
            self.config.VAO.append(VAO)  # I know, I know, I could also use the value here
            self.config.VBO.append(VBO)
            self.config.EBO.append(EBO)
        else:
            for counter, value in enumerate(VAO):
                self.config.VAO.append(VAO[counter])  # I know, I know, I could also use the value here
                self.config.VBO.append(VBO[counter])
                self.config.EBO.append(EBO[counter])

        return len(self.config.VAO) - 1

    def get_meshes(self, file_name):
        # Creates:
        indices = []  # how many f x/x/x indices there are
        vert = []  # vertex coordinates
        tex = []  # texture coordinates
        norm = []  # vertex normals
        all_indices = []  # indices for indexed drawing
        meshes, buffer = [], []

        try:
            with open(file_name, 'r') as f:
                for line in self.non_blank_lines(f):

                    values = line.split()

                    if values[0] == 'v':
                        vert = self.search_data(values, vert, 'v', 'float')
                    elif values[0] == 'vt':
                        tex = self.search_data(values, tex, 'vt', 'float')
                    elif values[0] == 'vn':
                        norm = self.search_data(values, norm, 'vn', 'float')
                    elif values[0] == 'f':
                        for value in values[1:]:
                            val = value.split('/')
                            all_indices = self.search_data(val, all_indices, 'f', 'int')
                            indices.append(self.index)
                            self.index += 1

            buffer = self.create_sorted_vertex_buffer(all_indices, vert, tex, norm)

            if self.model.name == "square1x1" or self.model.name == "rubber_band":
                vert, indices, buffer = self.load_square1x1()
            elif self.model.name == "circle" or self.model.name == "square" or self.model.name == "cross_hair1":
                vert, indices, buffer = self.load_vertex1()
            elif self.model.name == "node" or self.model.name == "socket":
                vert, indices, buffer = self.load_node_disc()

            mesh_id = self.config.get_mesh_id()
            mesh = self.__class__.Mesh_class(self.model, mesh_id, vertices=vert, indices=indices,
                                             buffer=buffer)
            meshes.append(mesh)
        except Exception as e:
            dump_exception(e)

        if DEBUG:
            if self.model.name == "node":
                print("vertices", self.model.name, vert)
                print("indices", self.model.name, indices)
                print("buffer", self.model.name, buffer)
                self.show_buffer_data(buffer)
                print("\n")

        return meshes

    @staticmethod
    def create_sorted_vertex_buffer(indices_data, vertices, textures, normals):
        # sorted vertex buffer for use with glDrawArrays function
        buffer = []
        for i, ind in enumerate(indices_data):

            if i % 3 == 0:  # sort the vertex coordinates
                start = ind * 3
                end = start + 3
                buffer.extend(vertices[start:end])
            elif i % 3 == 1:  # sort the texture coordinates
                start = ind * 2
                end = start + 2
                buffer.extend(textures[start:end])
            elif i % 3 == 2:  # sort the normal vectors
                start = ind * 3
                end = start + 3
                buffer.extend(normals[start:end])
        return buffer

    @staticmethod
    def non_blank_lines(f):
        # removes blank lines
        for line in f:
            line = line.rstrip()
            if line:
                yield line

    @staticmethod
    def search_data(data_values, val_list, skip, data_type):
        # appends each data value found in the data value line to the val_list
        for d in data_values:
            if d == skip:
                continue
            if data_type == 'float':
                val_list.append(float(d))
            elif data_type == 'int':
                val_list.append(int(d) - 1)
        return val_list

    @staticmethod
    def show_buffer_data(buffer):
        print("buffer data in blocks")
        for i in range(len(buffer) // 8):
            start = i * 8
            end = start + 8
            print(buffer[start:end])

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

    def load_all_textures_into_opengl(self):
        """
        Gets all the images and textures in the config dictionary. Retrieves image file location and
        loads them into OpenGl

        """

        self.config.textures = glGenTextures(len(self.config.all_textures))
        for index, item in enumerate(self.config.all_textures.values()):
            self.load_texture_into_opengl(item['file_dir_name'], item['img_id'] + 1)

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


    @staticmethod
    def load_square1x1():
        # a manual way to load object square1x1
        vert = [0.5, -0.5, 0., -0.5, 0.5, 0., -0.5, -0.5, 0., 0.5, -0.5, 0., 0.5, 0.5, 0., -0.5, 0.5, 0.]
        ind = [0, 1, 2, 3, 4, 5]
        buffer = \
            [0.5, -0.5, 0., 1., 0., 0., 0., 1., -0.5, 0.5, 0., 0., 1., 0., 0., 1., -0.5, -0.5, 0., 0., 0., 0., 0.,
             1., 0.5, -0.5, 0., 1., 0., 0., 0., 1., 0.5, 0.5, 0., 1., 1., 0., 0., 1., -0.5, 0.5, 0., 0., 1., 0., 0., 1.]
        return vert, ind, buffer

    @staticmethod
    def load_vertex1():
        # a manual way to load object vertex1
        vert = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]
        ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        buffer = [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
                  0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
                  0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
                  0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
                  0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
                  0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
                  0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
                  0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.]
        return vert, ind, buffer

    @staticmethod
    def load_node_disc():
        # a manual way to load object node_disc
        vert = [
            -0.003901779, -0.0196157, 0.0, 0.0196157, -0.003901779, 0.0, 0.00390172, 0.0196157, 0.0, 0.00390172,
            0.0196157, 0.0, 0.0, 0.01999998, 0.0, -0.003901779, 0.0196157, 0.0, -0.003901779, 0.0196157, 0.0,
            -0.007653653, 0.01847755, 0.0, 0.00390172, 0.0196157, 0.0, -0.007653653, 0.01847755, 0.0, -0.01111137,
            0.01662939, 0.0, 0.00390172, 0.0196157, 0.0, -0.01111137, 0.01662939, 0.0, -0.01414209, 0.01414209,
            0.0, -0.01662939, 0.01111137, 0.0, -0.01662939, 0.01111137, 0.0, -0.01847755, 0.007653653, 0.0,
            -0.01111137, 0.01662939, 0.0, -0.01847755, 0.007653653, 0.0, -0.0196157, 0.003901779, 0.0, -0.01111137,
            0.01662939, 0.0, -0.0196157, 0.003901779, 0.0, -0.01999998, 0.0, 0.0, -0.0196157, -0.003901779,
            0.0, -0.0196157, -0.003901779, 0.0, -0.01847755, -0.007653653, 0.0, -0.0196157, 0.003901779, 0.0,
            -0.01847755, -0.007653653, 0.0, -0.01662939, -0.01111137, 0.0, -0.0196157, 0.003901779, 0.0, -0.01662939,
            -0.01111137, 0.0, -0.01414209, -0.01414209, 0.0, -0.01111137, -0.01662939, 0.0, -0.01111137, -0.01662939,
            0.0, -0.007653653, -0.01847755, 0.0, -0.003901779, -0.0196157, 0.0, -0.003901779, -0.0196157, 0.0,
            0.0, -0.01999998, 0.0, 0.003901779, -0.0196157, 0.0, 0.003901779, -0.0196157, 0.0, 0.007653653,
            -0.01847755, 0.0, -0.003901779, -0.0196157, 0.0, 0.007653653, -0.01847755, 0.0, 0.01111137, -0.01662933,
            0.0, -0.003901779, -0.0196157, 0.0, 0.01111137, -0.01662933, 0.0, 0.01414209, -0.01414209, 0.0,
            0.01662939, -0.01111137, 0.0, 0.01662939, -0.01111137, 0.0, 0.01847755, -0.007653653, 0.0, 0.0196157,
            -0.003901779, 0.0, 0.0196157, -0.003901779, 0.0, 0.01999998, 0.0, 0.0, 0.01961565, 0.003901779,
            0.0, 0.01961565, 0.003901779, 0.0, 0.01847755, 0.007653653, 0.0, 0.01662933, 0.01111137, 0.0,
            0.01662933, 0.01111137, 0.0, 0.01414209, 0.01414215, 0.0, 0.00390172, 0.0196157, 0.0, 0.01414209,
            0.01414215, 0.0, 0.01111137, 0.01662939, 0.0, 0.00390172, 0.0196157, 0.0, 0.01111137, 0.01662939,
            0.0, 0.007653594, 0.01847755, 0.0, 0.00390172, 0.0196157, 0.0, -0.01662939, -0.01111137, 0.0,
            -0.01111137, -0.01662939, 0.0, -0.003901779, -0.0196157, 0.0, 0.01111137, -0.01662933, 0.0, 0.01662939,
            -0.01111137, 0.0, 0.0196157, -0.003901779, 0.0, 0.0196157, -0.003901779, 0.0, 0.01961565, 0.003901779,
            0.0, 0.00390172, 0.0196157, 0.0, 0.01961565, 0.003901779, 0.0, 0.01662933, 0.01111137, 0.0,
            0.00390172, 0.0196157, 0.0, 0.00390172, 0.0196157, 0.0, -0.01111137, 0.01662939, 0.0, -0.0196157,
            0.003901779, 0.0, -0.0196157, 0.003901779, 0.0, -0.01662939, -0.01111137, 0.0, 0.00390172, 0.0196157,
            0.0, -0.01662939, -0.01111137, 0.0, -0.003901779, -0.0196157, 0.0, 0.00390172, 0.0196157, 0.0,
            -0.003901779, -0.0196157, 0.0, 0.01111137, -0.01662933, 0.0, 0.0196157, -0.003901779, 0.0, ]
        ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
               24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
               48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
               72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
        buffer = [-0.003901779,
                  -0.0196157, 0.0, 0.402455, 0.009607315, 0.0, 0.0, 1.0, 0.0196157, -0.003901779, 0.0, 0.9903927,
                  0.4024553, 0.0, 0.0, 1.0, 0.00390172, 0.0196157, 0.0, 0.5975444, 0.9903928, 0.0, 0.0,
                  1.0, 0.00390172, 0.0196157, 0.0, 0.5975444, 0.9903928, 0.0, 0.0, 1.0, 0.0, 0.01999998,
                  0.0, 0.5, 1.0, 0.0, 0.0, 1.0, -0.003901779, 0.0196157, 0.0, 0.4024549, 0.9903926,
                  0.0, 0.0, 1.0, -0.003901779, 0.0196157, 0.0, 0.4024549, 0.9903926, 0.0, 0.0, 1.0,
                  -0.007653653, 0.01847755, 0.0, 0.3086583, 0.9619397, 0.0, 0.0, 1.0, 0.00390172, 0.0196157, 0.0,
                  0.5975444, 0.9903928, 0.0, 0.0, 1.0, -0.007653653, 0.01847755, 0.0, 0.3086583, 0.9619397, 0.0,
                  0.0, 1.0, -0.01111137, 0.01662939, 0.0, 0.2222148, 0.9157348, 0.0, 0.0, 1.0, 0.00390172,
                  0.0196157, 0.0, 0.5975444, 0.9903928, 0.0, 0.0, 1.0, -0.01111137, 0.01662939, 0.0, 0.2222148,
                  0.9157348, 0.0, 0.0, 1.0, -0.01414209, 0.01414209, 0.0, 0.1464466, 0.8535534, 0.0, 0.0,
                  1.0, -0.01662939, 0.01111137, 0.0, 0.08426517, 0.7777851, 0.0, 0.0, 1.0, -0.01662939, 0.01111137,
                  0.0, 0.08426517, 0.7777851, 0.0, 0.0, 1.0, -0.01847755, 0.007653653, 0.0, 0.03806024, 0.6913417,
                  0.0, 0.0, 1.0, -0.01111137, 0.01662939, 0.0, 0.2222148, 0.9157348, 0.0, 0.0, 1.0,
                  -0.01847755, 0.007653653, 0.0, 0.03806024, 0.6913417, 0.0, 0.0, 1.0, -0.0196157, 0.003901779, 0.0,
                  0.009607374, 0.5975452, 0.0, 0.0, 1.0, -0.01111137, 0.01662939, 0.0, 0.2222148, 0.9157348, 0.0,
                  0.0, 1.0, -0.0196157, 0.003901779, 0.0, 0.009607374, 0.5975452, 0.0, 0.0, 1.0, -0.01999998,
                  0.0, 0.0, 0.0, 0.5000001, 0.0, 0.0, 1.0, -0.0196157, -0.003901779, 0.0, 0.009607315,
                  0.4024549, 0.0, 0.0, 1.0, -0.0196157, -0.003901779, 0.0, 0.009607315, 0.4024549, 0.0, 0.0,
                  1.0, -0.01847755, -0.007653653, 0.0, 0.03806018, 0.3086584, 0.0, 0.0, 1.0, -0.0196157, 0.003901779,
                  0.0, 0.009607374, 0.5975452, 0.0, 0.0, 1.0, -0.01847755, -0.007653653, 0.0, 0.03806018, 0.3086584,
                  0.0, 0.0, 1.0, -0.01662939, -0.01111137, 0.0, 0.08426517, 0.2222149, 0.0, 0.0, 1.0,
                  -0.0196157, 0.003901779, 0.0, 0.009607374, 0.5975452, 0.0, 0.0, 1.0, -0.01662939, -0.01111137, 0.0,
                  0.08426517, 0.2222149, 0.0, 0.0, 1.0, -0.01414209, -0.01414209, 0.0, 0.1464466, 0.1464466, 0.0,
                  0.0, 1.0, -0.01111137, -0.01662939, 0.0, 0.2222149, 0.08426517, 0.0, 0.0, 1.0, -0.01111137,
                  -0.01662939, 0.0, 0.2222149, 0.08426517, 0.0, 0.0, 1.0, -0.007653653, -0.01847755, 0.0, 0.3086584,
                  0.03806018, 0.0, 0.0, 1.0, -0.003901779, -0.0196157, 0.0, 0.402455, 0.009607315, 0.0, 0.0,
                  1.0, -0.003901779, -0.0196157, 0.0, 0.402455, 0.009607315, 0.0, 0.0, 1.0, 0.0, -0.01999998,
                  0.0, 0.5000002, 0.0, 0.0, 0.0, 1.0, 0.003901779, -0.0196157, 0.0, 0.5975454, 0.009607374,
                  0.0, 0.0, 1.0, 0.003901779, -0.0196157, 0.0, 0.5975454, 0.009607374, 0.0, 0.0, 1.0,
                  0.007653653, -0.01847755, 0.0, 0.6913419, 0.03806036, 0.0, 0.0, 1.0, -0.003901779, -0.0196157, 0.0,
                  0.402455, 0.009607315, 0.0, 0.0, 1.0, 0.007653653, -0.01847755, 0.0, 0.6913419, 0.03806036, 0.0,
                  0.0, 1.0, 0.01111137, -0.01662933, 0.0, 0.7777854, 0.08426535, 0.0, 0.0, 1.0, -0.003901779,
                  -0.0196157, 0.0, 0.402455, 0.009607315, 0.0, 0.0, 1.0, 0.01111137, -0.01662933, 0.0, 0.7777854,
                  0.08426535, 0.0, 0.0, 1.0, 0.01414209, -0.01414209, 0.0, 0.8535537, 0.1464468, 0.0, 0.0,
                  1.0, 0.01662939, -0.01111137, 0.0, 0.915735, 0.2222151, 0.0, 0.0, 1.0, 0.01662939, -0.01111137,
                  0.0, 0.915735, 0.2222151, 0.0, 0.0, 1.0, 0.01847755, -0.007653653, 0.0, 0.9619399, 0.3086587,
                  0.0, 0.0, 1.0, 0.0196157, -0.003901779, 0.0, 0.9903927, 0.4024553, 0.0, 0.0, 1.0,
                  0.0196157, -0.003901779, 0.0, 0.9903927, 0.4024553, 0.0, 0.0, 1.0, 0.01999998, 0.0, 0.0,
                  1.0, 0.5000005, 0.0, 0.0, 1.0, 0.01961565, 0.003901779, 0.0, 0.9903925, 0.5975457, 0.0,
                  0.0, 1.0, 0.01961565, 0.003901779, 0.0, 0.9903925, 0.5975457, 0.0, 0.0, 1.0, 0.01847755,
                  0.007653653, 0.0, 0.9619396, 0.6913422, 0.0, 0.0, 1.0, 0.01662933, 0.01111137, 0.0, 0.9157345,
                  0.7777857, 0.0, 0.0, 1.0, 0.01662933, 0.01111137, 0.0, 0.9157345, 0.7777857, 0.0, 0.0,
                  1.0, 0.01414209, 0.01414215, 0.0, 0.8535529, 0.8535538, 0.0, 0.0, 1.0, 0.00390172, 0.0196157,
                  0.0, 0.5975444, 0.9903928, 0.0, 0.0, 1.0, 0.01414209, 0.01414215, 0.0, 0.8535529, 0.8535538,
                  0.0, 0.0, 1.0, 0.01111137, 0.01662939, 0.0, 0.7777846, 0.9157352, 0.0, 0.0, 1.0,
                  0.00390172, 0.0196157, 0.0, 0.5975444, 0.9903928, 0.0, 0.0, 1.0, 0.01111137, 0.01662939, 0.0,
                  0.7777846, 0.9157352, 0.0, 0.0, 1.0, 0.007653594, 0.01847755, 0.0, 0.6913411, 0.9619401, 0.0,
                  0.0, 1.0, 0.00390172, 0.0196157, 0.0, 0.5975444, 0.9903928, 0.0, 0.0, 1.0, -0.01662939,
                  -0.01111137, 0.0, 0.08426517, 0.2222149, 0.0, 0.0, 1.0, -0.01111137, -0.01662939, 0.0, 0.2222149,
                  0.08426517, 0.0, 0.0, 1.0, -0.003901779, -0.0196157, 0.0, 0.402455, 0.009607315, 0.0, 0.0,
                  1.0, 0.01111137, -0.01662933, 0.0, 0.7777854, 0.08426535, 0.0, 0.0, 1.0, 0.01662939, -0.01111137,
                  0.0, 0.915735, 0.2222151, 0.0, 0.0, 1.0, 0.0196157, -0.003901779, 0.0, 0.9903927, 0.4024553,
                  0.0, 0.0, 1.0, 0.0196157, -0.003901779, 0.0, 0.9903927, 0.4024553, 0.0, 0.0, 1.0,
                  0.01961565, 0.003901779, 0.0, 0.9903925, 0.5975457, 0.0, 0.0, 1.0, 0.00390172, 0.0196157, 0.0,
                  0.5975444, 0.9903928, 0.0, 0.0, 1.0, 0.01961565, 0.003901779, 0.0, 0.9903925, 0.5975457, 0.0,
                  0.0, 1.0, 0.01662933, 0.01111137, 0.0, 0.9157345, 0.7777857, 0.0, 0.0, 1.0, 0.00390172,
                  0.0196157, 0.0, 0.5975444, 0.9903928, 0.0, 0.0, 1.0, 0.00390172, 0.0196157, 0.0, 0.5975444,
                  0.9903928, 0.0, 0.0, 1.0, -0.01111137, 0.01662939, 0.0, 0.2222148, 0.9157348, 0.0, 0.0,
                  1.0, -0.0196157, 0.003901779, 0.0, 0.009607374, 0.5975452, 0.0, 0.0, 1.0, -0.0196157, 0.003901779,
                  0.0, 0.009607374, 0.5975452, 0.0, 0.0, 1.0, -0.01662939, -0.01111137, 0.0, 0.08426517, 0.2222149,
                  0.0, 0.0, 1.0, 0.00390172, 0.0196157, 0.0, 0.5975444, 0.9903928, 0.0, 0.0, 1.0,
                  -0.01662939, -0.01111137, 0.0, 0.08426517, 0.2222149, 0.0, 0.0, 1.0, -0.003901779, -0.0196157, 0.0,
                  0.402455, 0.009607315, 0.0, 0.0, 1.0, 0.00390172, 0.0196157, 0.0, 0.5975444, 0.9903928, 0.0,
                  0.0, 1.0, -0.003901779, -0.0196157, 0.0, 0.402455, 0.009607315, 0.0, 0.0, 1.0, 0.01111137,
                  -0.01662933, 0.0, 0.7777854, 0.08426535, 0.0, 0.0, 1.0, 0.0196157, -0.003901779, 0.0, 0.9903927,
                  0.4024553, 0.0, 0.0, 1.0]
        return vert, ind, buffer
