# -*- coding: utf-8 -*-

"""
Using the universe for the detail sphere_base. This universe will only contain a single sphere_base at the time
"""

from sphere_universe_base.suv_widget import UV_Widget
from sphere_universe_base.suv_universe import Universe
from sphere_overlay.sov_sphere import SplitSphere

PYBULLET_KEY_ID = 2


class SplitUniverse(Universe):
    Sphere_class = SplitSphere

    def __init__(self, parent, pybullet_key):
        super().__init__(parent, pybullet_key=pybullet_key)

    def draw(self):
        # In the detail sphere_base window only draw the selected sphere_base
        self.target_sphere.draw()


class SplitUVWidget(UV_Widget):
    Universe_class = SplitUniverse

    def __init__(self, parent):
        super().__init__(parent)

    def _init_variables(self):
        self.pybullet_key = PYBULLET_KEY_ID