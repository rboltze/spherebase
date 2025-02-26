# -*- coding: utf-8 -*-

"""

Using the map for the detail sphere_base. This map will only contain a single sphere_base at the time

"""

from examples.example_sphere.sphere_overlay.sov_sphere import OverlaySphere
from sphere_base.sphere_universe.map import Map
from sphere_base.sphere_universe.map_widget import MapWidget

# PYBULLET_KEY_ID
KEY = 2


class SphereMap(Map):
    Sphere_class = OverlaySphere

    def __init__(self, parent, pybullet_key):
        skybox_img_dir = "..//examples/resources/textures/skybox/"
        sphere_texture_dir = "..//examples/resources/sphere_textures/"
        sphere_icon_dir = "..//examples/resources/sphere_icons/"

        super().__init__(parent, skybox_img_dir=skybox_img_dir, sphere_texture_dir=sphere_texture_dir,
                         sphere_icon_dir=sphere_icon_dir, pybullet_key=pybullet_key)

    def draw(self):
        # In the detail sphere_base window only draw the selected sphere_base
        if self.target_sphere:
            self.target_sphere.draw()


class UVWidget(MapWidget):
    Map_class = SphereMap

    def __init__(self, parent):
        super().__init__(parent)

    def _init_variables(self):
        self.pybullet_key = KEY
