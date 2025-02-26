# -*- coding: utf-8 -*-

"""
A module containing the Configuration class.

"""

from sphere_base.utils.utils import dump_exception
import os

from importlib_resources import files
import sphere_base.model.resources.icons


class UvConfig:
    """
    The configuration class contains project wide variables which can be easily shared between modules and classes.

    """
    def __init__(self, map, skybox_img_dir="", sphere_texture_dir="", sphere_icon_dir=""):
        """
        Constructor of the sphere_base class.

        :param map: reference to the :class:`~sphere_iot.uv_universe.Map`
        :type map: :class:`~sphere_iot.uv_universe.Map`

        :Instance Variables:

            - **view** - reference to the map class map widget or view.
            - **map** - Instance of :class:`~sphere_iot.uv_universe.Map`

        """
        self.map = map
        self.map_widget = self.map.map_widget
        self.view_loc = None

        # project wide opengl buffers
        self.VAO = []  # Vertex arrays objects indexes
        self.VBO = []  # Vertex buffers objects indexes
        self.EBO = []  # Element array buffer object indexes

        self.mesh_id_counter = 0  # used in creating new indexes for meshes

        self._win_size_changed_listeners = []
        self._view_changed_listeners = []
        self.textures = []

        self.skybox_sets = self.create_skybox_set(skybox_img_dir)
        self.sphere_textures = self.create_texture_set(sphere_texture_dir)
        self.all_textures = self.create_texture_dict(sphere_texture_dir, sphere_icon_dir)

    @staticmethod
    def create_skybox_set(skybox_dir=""):

        set0, set1 = [None], []
        try:
            if skybox_dir:
                set1 = [skybox_dir + name for name in os.listdir(skybox_dir) if
                        os.path.isdir(os.path.join(skybox_dir, name))]

            return set0 + set1
        except Exception as e:
            dump_exception(e)

    def create_texture_dict(self, dir1, dir2):
        # Get all textures from the directories in a dictionary
        textures = self.create_texture_set(dir1, dir2)
        _dict = {}

        try:
            for index, file_name in enumerate(textures):
                key = os.path.basename(file_name)
                _type = os.path.split(os.path.dirname(file_name))[1]
                if key in _dict:
                    continue
                if os.path.isfile(file_name):
                    if file_name.endswith('.jpg') or file_name.endswith('.png'):
                        _dict[key] = {}
                        _dict[key]['file_name'] = key
                        _dict[key]['img_id'] = index
                        _dict[key]['file_dir_name'] = file_name
                        _dict[key]['type'] = _type[:-1]  # removing the 's'
            return _dict
        except Exception as e:
            dump_exception(e)

    @staticmethod
    def create_texture_set(*args):
        # puts all the files of all the directories in a list
        _set = []
        for directory in args:
            s = [directory + file_name for file_name in os.listdir(directory)]
            _set += s
        return _set

    def set_view_loc(self, view):
        """
        Setting the view matrix to be used in OpenGL

        :param view: The view matrix
        :type view: ``Matrix``

        """
        self.view_loc = view
        self.on_view_changed()

    def add_win_size_changed_listener(self, callback):
        """
        Register callback for 'win size changed' event.

        :param callback: callback function

        """
        self._win_size_changed_listeners.append(callback)

    def add_view_changed_listener(self, callback):
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

    def get_img_id(self, img_name) -> int:
        """
        Returns texture id of the texture name received.

        :param img_name: name of the texture/image/icon to retrieve
        :type img_name: str

        """
        img_name = img_name if img_name else 'icon_question_mark'
        image_id = None
        for index, _item in enumerate(self.map.config.all_textures.values()):
            if _item['file_name'] == img_name or _item['file_name'][:-4] == img_name:
                image_id = _item['img_id']
                continue
        return image_id

    def get_mesh_id(self) -> int:
        """
        Returns a new 'mesh id' and increases the mesh id counter

        """

        mesh_id = self.mesh_id_counter
        self.mesh_id_counter += 1
        return mesh_id

    def get_texture(self, texture_id):

        if texture_id is None:
            tex = self.textures[self.get_img_id('')]  # default question mark icon
        else:
            tex = self.textures[texture_id]
        return tex

