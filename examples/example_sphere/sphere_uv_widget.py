# -*- coding: utf-8 -*-

"""

Using the universe for the detail sphere_base. This universe will only contain a single sphere_base at the time

"""

from sphere_base.sphere_universe_base.suv_widget import UV_Widget
from sphere_base.sphere_universe_base.suv_universe import Universe
from sphere_base.sphere_overlay.sov_sphere import SplitSphere

# PYBULLET_KEY_ID
KEY = 2


class SphereUniverse(Universe):
    Sphere_class = SplitSphere

    def __init__(self, parent, pybullet_key):
        skybox_img_dir = "..//examples/resources/textures/skybox/"
        super().__init__(parent, skybox_img_directory=skybox_img_dir, pybullet_key=pybullet_key)

    def draw(self):
        # In the detail sphere_base window only draw the selected sphere_base
        self.target_sphere.draw()


class UVWidget(UV_Widget):
    Universe_class = SphereUniverse

    def __init__(self, parent):
        super().__init__(parent)

    def _init_variables(self):
        self.pybullet_key = KEY
