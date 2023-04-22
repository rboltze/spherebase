# -*- coding: utf-8 -*-

"""

Using the universe for the detail sphere_base. This universe will only contain a single sphere_base at the time

"""

from sphere_base.sphere_universe_base.suv_widget import UVWidget
from sphere_base.sphere_universe_base.suv_universe import Universe
from sphere_base.sphere_overlay.sov_sphere import OverlaySphere

# PYBULLET_KEY_ID
KEY = 2


class SphereUniverse(Universe):
    Sphere_class = OverlaySphere

    def __init__(self, parent, pybullet_key):
        skybox_img_dir = "..//examples/resources/textures/skybox/"
        sphere_texture_dir = "..//examples/resources/sphere_textures/"
        sphere_icon_dir = "..//examples/resources/sphere_icons/"

        super().__init__(parent, skybox_img_dir=skybox_img_dir, sphere_texture_dir=sphere_texture_dir,
                         sphere_icon_dir=sphere_icon_dir, pybullet_key=pybullet_key)

    def draw(self):
        # In the detail sphere_base window only draw the selected sphere_base
        self.target_sphere.draw()


class UVWidget(UVWidget):
    Universe_class = SphereUniverse

    def __init__(self, parent):
        super().__init__(parent)

    def _init_variables(self):
        self.pybullet_key = KEY
