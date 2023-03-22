# -*- coding: utf-8 -*-

from examples.example_sphere.widget.widget_sphere_settings import *
from examples.example_sphere.widget.widget_skybox_settings import *
from examples.example_sphere.widget.widget_textures_settings import *
from examples.example_sphere.widget.widget_sphere_color_buttons_settings import *


class Settings(QWidget):

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.setWindowTitle("Settings")
        # TODO: settings windows does not stay on top
        self.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.uv = self.main_win.sphere_widget.uv_widget.uv
        self._init_Values()
        self._init_ui()
        self._setup_ui()

    def _init_Values(self):
        pass

    def _init_ui(self):
        self.group_box = QGroupBox()
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.group_box)

        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(5)
        self.group_box.setLayout(self.grid_layout)

        self.setLayout(layout)

    def _setup_ui(self):

        self.sphere_settings = WidgetSphereSettings(self.main_win)
        self.skybox_settings = WidgetSkyboxSettings(self.main_win)
        self.textures_settings = WidgetTextureSettings(self.main_win)
        self.sphere_color_buttons = WidgetSphereColorButtonSettings(self.main_win)
        self.grid_layout.addWidget(self.skybox_settings, 1, 1, 1, 2)
        self.grid_layout.addWidget(self.textures_settings, 1, 3, 1, 5)
        self.grid_layout.addWidget(self.sphere_settings, 2, 1, 1, 2)
        self.grid_layout.addWidget(self.sphere_color_buttons, 2, 3, 1, 5)

        self.sphere_color_buttons.color_changed.connect(self.on_change_color_buttons)

    def on_change_color_buttons(self):
        self.sphere_settings.color = self.sphere_color_buttons.color







