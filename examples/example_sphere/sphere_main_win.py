# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from examples.example_sphere.sphere_win_menu import SphereMenu
from examples.example_sphere.sphere_widget import SphereWidget
from examples.example_sphere.sphere_uv_widget import UVWidget  # detail spheres


class MainWindow(QMainWindow):
    Menu_class = SphereMenu
    sphere_widget_class = SphereWidget
    Uv_Widget_class = UVWidget

    def __init__(self):
        super().__init__()

        self.name_company = 'rboltze'
        self.name_product = 'sphere_base'
        self.version = '0.1.0 Beta 16/04/2023'

        self.filename = None
        self._set_win_properties()
        self._read_settings()
        self.sphere_widget = self.__class__.sphere_widget_class(self)
        self.setCentralWidget(self.sphere_widget.uv_widget)
        self.menu = self.__class__.Menu_class(self)
        self.setWindowTitle("Sphere")
        self.show()
        self.sphere_widget.uv_widget.uv.skybox.get_skybox_set(skybox_id=self.skybox_id, random=self.random_skybox)

    def _set_win_properties(self):
        # set default window properties
        self.setGeometry(200, 200, 800, 600)

    def set_title(self, title=None):
        title = title if title else self.sphere_widget.title
        self.setWindowTitle(title + self.get_friendly_filename(self.filename))

    def may_be_saved(self) -> bool:
        """
        If any sphere_item in the sphere_iot is modified, show dialog to save the changes.
        Used before closing window.
        """
        if not self.sphere_widget.has_been_modified():
            return True

        result = QMessageBox.warning(self, "About to loose your work?",
                                     "The document has been modified.\n Do you want to save your changes?",
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                                     )

        if result == QMessageBox.Save:
            return self.menu.on_file_save()
        elif result == QMessageBox.Cancel:
            return False

        return True

    def get_friendly_filename(self, file_name):
        """
        Get user friendly filename. Used in the window title
        """
        name = os.path.basename(file_name) if self.filename else "New Graph"
        return name + ("*" if self.sphere_widget.has_been_modified() else "")

    def on_about(self):
        msg = QMessageBox()
        msg.setWindowTitle("About Sphere Base")
        msg.setIcon(QMessageBox.Information)
        msg.setText("<b>Sphere Base</b> is a Python program to visualize a sphere with a number of connected nodes "
                    "on its surface. Written by: Richard Boltze, email: <a>rboltze@protonmail.com")
        msg.setInformativeText("version: " + self.version)
        msg.exec_()

    def closeEvent(self, event):
        """
        Handle close event. Ask before we loose work
        """
        if self.may_be_saved():
            event.accept()
            self.write_settings()
            # # Save the window size and position before exiting
            # self.settings.setValue("geometry", self.saveGeometry())
            # self.settings.setValue("windowState", self.saveState())
            QMainWindow.closeEvent(self, event)
        else:
            event.ignore()

    def _read_settings(self):
        """Read the permanent profile settings for this app"""
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))

        self.move(pos)
        self.resize(size)
        self.skybox_id = settings.value('skybox_id', 0)
        txt = settings.value('random_skybox', 'True')
        self.random_skybox = True if txt == 'True' else False

    def write_settings(self):
        """Write the permanent profile settings for this app"""
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
