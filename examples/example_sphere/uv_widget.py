# -*- coding: utf-8 -*-

"""

Using the universe for the detail sphere_base. This universe will only contain a single sphere_base at the time

"""

from examples.example_sphere.sphere_overlay.sov_sphere import OverlaySphere
from sphere_base.sphere_universe.universe import Universe
from sphere_base.sphere_universe.universe_widget import UniverseWidget

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
        if self.target_sphere:
            self.target_sphere.draw()


class UVWidget(UniverseWidget):
    Universe_class = SphereUniverse

    def __init__(self, parent):
        super().__init__(parent)

    def _init_variables(self):
        self.pybullet_key = KEY
