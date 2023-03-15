# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from examples.example_sphere.sphere_win_menu import SphereMenu
from examples.example_sphere.sphere_widget import SphereWidget
from examples.example_sphere.sphere_uv_widget import UVWidget  # detail spheres

COMPANY = "company"
PRODUCT = "product"
TAB_NAMES = {0: "Node editor", 1: "Description"}


class MainWindow(QMainWindow):
    Menu_class = SphereMenu
    sphere_widget_class = SphereWidget
    Uv_Widget_class = UVWidget

    def __init__(self):
        super().__init__()

        self.filename = None
        self.sphere_widget = self.__class__.sphere_widget_class(self)
        self.setCentralWidget(self.sphere_widget.uv_widget)
        self._set_win_properties()
        self.menu = self.__class__.Menu_class(self)
        self.setWindowTitle("Sphere")

        self.show()

    def _set_win_properties(self):
        # set window properties
        self.setGeometry(200, 200, 800, 600)
        # restore window size and position.
        self.settings = QSettings(COMPANY, PRODUCT)
        if not self.settings.value("geometry") is None:
            self.restoreGeometry(self.settings.value("geometry"))
        if not self.settings.value("windowState") is None:
            self.restoreState(self.settings.value("windowState"))

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
        QMessageBox.about(self, "About the Sphere Node Editor",
                          "The <b>Sphere Node Editor</b> is a Python program to visualize and edit groups "
                          "of related entities in a logical and attractive way. Written by: Richard Boltze, "
                          "email: rboltze@protonmail.com</a>")

    def closeEvent(self, event):
        """
        Handle close event. Ask before we loose work
        """
        if self.may_be_saved():
            event.accept()
            # Save the window size and position before exiting
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("split_geometry", self.sphere_widget.saveGeometry())
            QMainWindow.closeEvent(self, event)
        else:
            event.ignore()
