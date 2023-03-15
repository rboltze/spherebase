# -*- coding: utf-8 -*-

"""
This is the Skybox Module.

It is responsible for creating a cube with a star packed universe background.
The cube is small and is moving with the camera. Whenever there is an object in the view, the skybox is not painted
on those pixels.

It is a curious approach to painting a backdrop as the cube walls are closer than most objects in the scene but the
OpenGl renderer skips those objects if shown in the view.

This is a Modern OpenGL implementation known by the name: ``Skybox``.

"""

from sphere_base.sphere_universe_base.suv_graphic_item import GraphicItem
from collections import namedtuple
from sphere_base.sphere_universe_base.suv_constants import *
from PIL import Image
from random import randint


class Skybox(GraphicItem):
    Face_texture = namedtuple("faces", "id, face_name, img_type, width, height, path, file_and_path, img_data")

    """
    Class creating and maintaining the ``background`` ``Skybox``
    
    """

    def __init__(self, universe=None, skybox_set_name=None):
        """
        Constructor of the Skybox class.

        :param universe: reference to the :class:`~sphere_iot.uv_universe.Universe`
        :type universe: :class:`~sphere_iot.uv_universe.Universe`

        :Instance Attributes:


            - **edge** - Instance of :class:`~sphere_iot.uv_edge.SphereSurfaceEdge`
            - **calc** - Instance of :class:`~sphere_iot.uv_calc.UvCalc`
            - **config** - Instance of :class:`~sphere_iot.uv_config.UvConfig`
            - **edge_drag** - Instance of :class:`~sphere_iot.uv_edge_drag.EdgeDrag`
            - **history** - Instance of :class:`~sphere_iot.uv_history.History`
            - **shader** - Instance of :class:`~sphere_iot.shader.uv_sphere_shader.SphereShader`

        :Instance Variables:

            - **xyz** - position of the center of the cube which is the position of camera [x, y, z]
            - **uv** - reference to :class:`~sphere_iot.uv_universe.Universe`
            - **model** - Instance of :class:`~sphere_iot.uv_model.Model`
            - **shader** - reference to the shader of the ``model``
            - **scale** - scaling used for this model
            - **paint_skybox** - ``int`` id of the current texture applied to the sphere_base
            - **orientation** - ``Vector3`` orientation of the ``skybox``

        """

        super().__init__(self, 'skybox')

        self.uv = universe
        self.model = self.uv.models.get_model('skybox')
        self.xyz = self.uv.cam.xyz

        # We get the shader from the model
        self.shader = self.model.shader

        self._init_variables()
        self._init_skybox_image_set(skybox_set_name)
        self._setup_skybox()

    def _init_variables(self):
        self.scale = None
        self.index = 0
        self.faces = []
        self.orientation = [0, 0, 0]
        self.paint_skybox = True

    def get_random_skybox(self):
        """
        Change the skybox with a new random set of images
        """
        self._get_random_set()
        self._setup_skybox()

    def _init_skybox_image_set(self, skybox_set_name=None):
        if skybox_set_name:
            self.skybox_id = self.get_skybox_id(skybox_set_name)
        else:
            self.skybox_id = self._get_random_set()

    def _setup_skybox(self):
        path = self.get_skybox_path()
        if path:
            self.create_skybox_faces(path)


        self.shader.load_texture_skybox(self.faces)

    @staticmethod
    def _get_random_set() -> int:
        """
        Returns the id of a random image set of all skybox sets stored. This happens at the beginning of the program.
        If you want to allow the user to randomly jump to a new set during the program the new set should be
        compared with the old set to avoid duplication.

        """
        return randint(1, len(SKYBOX_SETS) - 1)

    @staticmethod
    def get_skybox_id(skybox_name) -> int:
        """
        returns the id of a skybox based on its name.

        :param skybox_name: Name of the ``Skybox`` set
        :type skybox_name: ``string``
        :returns: id of the skybox image set

        """

        for i, skybox in enumerate(SKYBOX_SETS):
            if skybox_name == skybox:
                return i

    def get_next_set(self):
        """
        Activate next Skybox set in the id sequence.

        """
        # get next sky box image set
        if self.skybox_id + 1 == len(SKYBOX_SETS):
            self.skybox_id = 0
        else:
            self.skybox_id += 1
        self._setup_skybox()

    def get_former_set(self):
        """
        Activate the former set in the id sequence.

        """
        # get the one before current sky box image set
        if self.skybox_id - 1 < 0:
            self.skybox_id = len(SKYBOX_SETS) - 1
        else:
            self.skybox_id -= 1
        self._setup_skybox()

    def get_skybox_path(self) -> str:
        """
        Returns the image path of the current active Skybox id

        """
        dir_name = SKYBOX_SETS[self.skybox_id]
        if dir_name:
            path = SKYBOX_IMG_DIR + dir_name + "/"
            self.paint_skybox = True
        else:
            path = None
            self.paint_skybox = False
        return path

    def create_skybox_faces(self, path):
        """
        Gets the six faces of the Skybox from the image path and adds them to the faces array.

        :param path: path where the 6 images for the current skybox are located.
        :type path: ``str``
        """
        self.faces = []
        face_order = ["right", "left", "top", "bottom", "back", "front"]
        for i, face in enumerate(face_order):
            img = Image.open(path + face + ".png")
            img_data = img.convert("RGBA").tobytes()
            face = self.Face_texture(i, face, "png", img.width, img.height, path,
                                     path + face + ".png", img_data)
            self.faces.append(face)

    def draw(self):
        """
        Draws the current Skybox

        """
        if self.paint_skybox:
            self.model.draw(self)
