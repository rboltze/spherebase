# -*- coding: utf-8 -*-

"""
A module containing the Configuration class.

"""

from sphere_base.sphere_universe_base.suv_constants import *
import os
import collections


class UvConfig:
    """
    The configuration class contains project wide variables which can be easily shared between modules and classes.

    """
    def __init__(self, universe, skybox_img_dir="", sphere_texture_dir=""):
        """
        Constructor of the sphere_base class.

        :param universe: reference to the :class:`~sphere_iot.uv_universe.Universe`
        :type universe: :class:`~sphere_iot.uv_universe.Universe`

        :Instance Variables:

            - **view** - reference to the universe class universe widget or view.
            - **uv** - Instance of :class:`~sphere_iot.uv_universe.Universe`

        """

        self.uv = universe
        self.view = self.uv.view
        self.view_loc = None

        # project wide opengl buffers
        self.VAO = None  # Vertex arrays objects indexes
        self.VBO = None  # Vertex buffers objects indexes
        self.EBO = None  # Element array buffer object indexes

        self.mesh_id_counter = 0  # used in creating new indexes for meshes

        self.textures = []
        self._textures = {}  # filled in models
        self._win_size_changed_listeners = []
        self._view_changed_listeners = []

        self.skybox_sets = self.create_skybox_set(skybox_img_dir)
        self.sphere_textures = self.create_texture_set(SPHERE_TEXTURE_DIR, sphere_texture_dir)
        self.all_textures = self.create_texture_dict(SPHERE_TEXTURE_DIR, sphere_texture_dir, TEXTURES_DIR)

    def create_skybox_set(self, skybox_dir=""):
        set0 = [None]
        set2 = []
        set1 = [SKYBOX_IMG_DIR + name for name in os.listdir(SKYBOX_IMG_DIR) if
                os.path.isdir(os.path.join(SKYBOX_IMG_DIR, name))]
        if skybox_dir:
            set2 = [skybox_dir + name for name in os.listdir(skybox_dir) if
                    os.path.isdir(os.path.join(skybox_dir, name))]

        return set0 + set1 + set2

    def create_texture_dict(self, dir1, dir2, dir3):
        # Get all textures from the 3 directories in a dictionary
        textures = self.create_texture_set(dir1, dir2, dir3)
        _dict = {}

        for index, file_name in enumerate(textures):
            key = os.path.basename(file_name)
            type = os.path.split(os.path.dirname(file_name))[1]
            if key in _dict:
                continue
            _dict[key] = {}
            _dict[key]['file_name'] = key
            _dict[key]['texture_id'] = index
            _dict[key]['file_dir_name'] = file_name
            _dict[key]['type'] = type[:-1]  # removing the 's'

        return _dict

    def create_texture_set(self, *args):
        # puts all the files of all the directories in a list
        _set = []
        for directory in args:
            s = [directory + file_name for file_name in os.listdir(directory)]
            _set += s
        return _set

    def set_view_loc(self, view: 'matrix'):
        """
        Setting the view matrix to be used in OpenGL

        :param view: The view matrix
        :type view: ``Matrix``

        """
        self.view_loc = view
        self.on_view_changed()

    def add_win_size_changed_listener(self, callback: 'function'):
        """
        Register callback for 'win size changed' event.

        :param callback: callback function

        """
        self._win_size_changed_listeners.append(callback)

    def add_view_changed_listener(self, callback: 'function'):
        """
        Register callback for 'view changed' event.

        :param callback: callback function

        """
        self._view_changed_listeners.append(callback)

    def on_win_size_changed(self):
        """
        Handles 'win sized changed', calls registered listeners.

        """
        for callback in self._win_size_changed_listeners:
            callback()

    def on_view_changed(self):
        """
        Handles 'view changed', calls registered listeners.

        """
        for callback in self._view_changed_listeners:
            callback()

    def create_texture_by_name_dictionary(self):
        """
        Creating a texture dictionary indexed by name

        """
        for texture in TEXTURES:
            texture_id, texture_name = texture[0], texture[1]
            self._textures[texture_name] = texture_id

    def get_img_id(self, img_name) -> int:
        """
        Returns texture id of the texture name received.

        :param img_name: name of the texture/image/icon to retrieve
        :type img_name: str

        """
        if img_name in self._textures:
            return self._textures[img_name]
        return None

    def get_mesh_id(self) -> int:
        """
        Returns a new 'mesh id' and increases the mesh id counter

        """

        mesh_id = self.mesh_id_counter
        self.mesh_id_counter += 1
        return mesh_id
