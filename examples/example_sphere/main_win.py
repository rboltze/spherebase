# -*- coding: utf-8 -*-

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QAction

from examples.example_sphere.uv_widget import UVWidget
from examples.example_sphere.widget.widget_settings import Settings
from sphere_base.sphere_main_window import SphereMainWindow


class MainWindow(SphereMainWindow):
    Uv_Widget_class = UVWidget

    def __init__(self):
        super().__init__()

        self.window_settings, self.action_settings = None, None
        self.create_actions()

    def create_actions(self):
        self.action_settings = QAction('&Settings', self)
        self.action_settings.setStatusTip('Application settings')

        # noinspection PyUnresolvedReferences
        self.action_settings.triggered.connect(self.open_settings_window)

    def open_settings_window(self):
        self.window_settings = Settings(self)
        self.window_settings.setGeometry(QRect(400, 400, 500, 575))
        self.window_settings.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.window_settings.show()
