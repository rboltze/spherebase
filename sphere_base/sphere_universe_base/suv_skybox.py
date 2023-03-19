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
from PIL import Image
from random import randint
import os


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
        self.cf = self.uv.config

        # We get the shader from the model
        self.shader = self.model.shader

        self._init_variables()

    def _init_variables(self):
        self.scale = None
        self.index = 0
        self.faces = []
        self.orientation = [0, 0, 0]
        self.paint_skybox = True

    def get_skybox_set(self, skybox_name=None, skybox_id=None, random=False):

        if skybox_id == 0:  # Do not use a skybox
            self.skb_id = skybox_id
        elif not skybox_name and not skybox_id and not random:
            random = True  # select a random skybox
        elif skybox_name:
            lst = ['None' if not txt else os.path.basename(txt) for txt in self.uv.config.skybox_sets]
            self.skb_id = lst.index(skybox_name)  # choose a skybox by its name
        elif skybox_id:
            self.skb_id = skybox_id  # choose a skybox by its index

        if random:
            self.skb_id = randint(1, len(self.cf.skybox_sets) - 1)  # select a random skybox

        self.create_skybox_faces()

    def get_next_set(self):
        """
        Activate next Skybox set in the id sequence.

        """
        _id = self.skb_id
        _id = 0 if self.skb_id + 1 == len(self.cf.skybox_sets) else _id + 1
        self.skb_id = _id
        self.create_skybox_faces()

    def get_former_set(self):
        """
        Activate the former set in the id sequence.

        """
        # get the one before current sky box image set
        if self.skb_id - 1 < 0:
            self.skb_id = len(self.cf.skybox_sets) - 1
        else:
            self.skb_id -= 1
        self.create_skybox_faces()

    def get_skybox_path(self) -> str:
        """
        Returns the image path of the current active Skybox id

        """
        path = self.cf.skybox_sets[self.skb_id]
        self.paint_skybox = True if path else False
        return path + "/" if path else path

    def create_skybox_faces(self):
        """
        Gets the six faces of the Skybox from the image path and adds them to the faces array.

        :param path: path where the 6 images for the current skybox are located.
        :type path: ``str``
        """
        path = self.get_skybox_path()

        if path:

            self.faces = []
            face_order = ["right", "left", "top", "bottom", "back", "front"]
            for i, face in enumerate(face_order):
                img = Image.open(path + face + ".png")
                img_data = img.convert("RGBA").tobytes()
                face = self.Face_texture(i, face, "png", img.width, img.height, path,
                                         path + face + ".png", img_data)
                self.faces.append(face)
            self.shader.load_texture_skybox(self.faces)

    def draw(self):
        """
        Draws the current Skybox

        """
        if self.paint_skybox:
            self.model.draw(self)
