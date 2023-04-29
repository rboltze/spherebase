# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from examples.example_sphere.sphere_win_menu import SphereMenu
from examples.example_sphere.sphere_widget import SphereWidget
from examples.example_sphere.sphere_uv_widget import UVWidget  # detail spheres
from sphere_base.utils import dump_exception


class MainWindow(QMainWindow):
    Menu_class = SphereMenu
    sphere_widget_class = SphereWidget
    Uv_Widget_class = UVWidget

    def __init__(self):
        super().__init__()

        self.name_company = 'rboltze'
        self.name_product = 'sphere_base'
        self.version = '0.1.14 Beta 27/04/2023'

        self.skybox_id, self.random_skybox = None, True
        self._filename = None

        try:
            self._set_win_properties()
            self._read_settings()
            self.sphere_widget = self.__class__.sphere_widget_class(self)
            self.setCentralWidget(self.sphere_widget.uv_widget)
            self.menu = self.__class__.Menu_class(self)
            self.setWindowTitle("Sphere")
            self.create_status_bar()
            self.show()

            self.sphere_widget.uv_widget.uv.add_modified_listener(self.set_title)
            self.set_skybox(self.skybox_id, self.random_skybox)

        except Exception as e:
            dump_exception(e)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = os.path.basename(value)
        self.set_title()

    def create_status_bar(self):
        """Create Status bar """
        self.statusBar().showMessage("Ready")

    def set_skybox(self, skybox_id, random_skybox=True):
        self.sphere_widget.uv_widget.uv.skybox.get_skybox_set(skybox_id=self.skybox_id, random=self.random_skybox)

    def _set_win_properties(self):
        # set default window properties
        self.setGeometry(200, 200, 800, 600)

    def set_title(self, title=None, file_name=None):
        title = title if title else self.sphere_widget.title
        if file_name:
            self._filename = file_name
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
            return self.on_file_save()
        elif result == QMessageBox.Cancel:
            return False

        return True

    def get_friendly_filename(self, file_name):
        """
        Get user-friendly filename. Used in the window title
        """
        name = os.path.basename(file_name) if self._filename else "New Graph"
        return name + ("*" if self.sphere_widget.has_been_modified() else "")

    def on_about(self):
        msg = QMessageBox()
        msg.setWindowTitle("About Sphere Base")
        msg.setIcon(QMessageBox.Information)
        msg.setText("<b>Sphere Base</b> is a Python program to visualize a sphere with a number of connected nodes "
                    "on its surface. Written by: Richard Boltze, email: <a>rboltze@protonmail.com")
        msg.setInformativeText("version: " + self.version)
        msg.exec_()

    def on_file_new(self):
        self._filename = ""
        self.sphere_widget.uv_widget.uv_new()
        self.reset_modified()
        self.set_title()

    def on_file_open(self, file_names=None):
        if not file_names:
            file_names, _filter = QFileDialog.getOpenFileNames(self, 'Open graph from file',
                                                               self.get_file_dialog_directory(),
                                                               self.get_file_dialog_filter())
        try:
            for file_name in file_names:
                if file_name:
                    self.sphere_widget.uv_widget.load_from_file(file_name)
                    self.reset_modified()
                    self.set_title(file_name=file_name)

        except Exception as e:
            dump_exception(e)

    def on_file_save(self):
        """Handle File Save operation"""

        if not self.filename:
            return self.on_file_save_as()

        self.file_save(self.filename)
        self.statusBar().showMessage("Successfully saved %s" % self._filename, 5000)
        return True

    def on_file_save_as(self):
        """Handle File Save As operation"""

        file_name, _filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.get_file_dialog_directory(),
                                                         self.get_file_dialog_filter())
        if file_name == '':
            return False

        self.file_save(file_name)
        self.statusBar().showMessage("Successfully saved as %s" % self.filename, 5000)
        return True

    def file_save(self, filename=None):
        if filename is not None:
            self._filename = filename

        self.sphere_widget.uv_widget.save_to_file(self._filename)
        QApplication.restoreOverrideCursor()

        self.reset_modified()
        self.set_title()
        return True

    def reset_modified(self):
        # resetting the modified flag
        self.sphere_widget.uv_widget.uv.reset_has_been_modified()
        self.sphere_widget.on_selection_changed(None, None)

    @staticmethod
    def get_file_dialog_directory():
        """Returns starting directory for ``QFileDialog`` file open/save"""
        return ''

    @staticmethod
    def get_file_dialog_filter():
        """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
        return 'Graph (*.json);;All files (*)'

    def closeEvent(self, event):
        """
        Handle close event. Ask before we loose work
        """
        if self.may_be_saved():
            event.accept()
            self.write_settings()
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
