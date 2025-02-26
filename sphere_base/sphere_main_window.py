# -*- coding: utf-8 -*-

import os.path
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QApplication
from PyQt6.QtCore import QSettings, QPoint, QSize

from sphere_base.sphere_main_menu import SphereMenu
from sphere_base.sphere_universe.map_widget import MapWidget
from sphere_base.utils.utils import dump_exception
from sphere_base.utils.file_handler import FileHandler


class SphereMainWindow(QMainWindow):
    Menu_class = SphereMenu
    Uv_Widget_class = MapWidget

    def __init__(self):
        super().__init__()

        self.name_company = 'rboltze'
        self.name_product = 'sphere_base'
        self.version = '0.2.0.121 Beta 03/05/2025'

        self._file_name = None
        self.file_handler = FileHandler()
        self.skybox_id, self.random_skybox = None, True
        self.selected_sphere, self.selected_sphere_item = None, None

        self.title = "Sphere "

        self.selected_sphere_items = []

        self._set_win_properties()
        self._read_settings()

        self.map_widget = self.Uv_Widget_class(self)

        self.setCentralWidget(self.map_widget)
        self.setWindowTitle("Sphere")
        self.create_status_bar()

        # delayed initialization waiting for OpenGL initialization
        self.map_widget.add_to_delayed_init(self._delayed_init)

        self.show()
        self.map_widget.map.add_modified_listener(self.set_title)
        self.set_title()
        self.set_skybox()

        self.menu = self.__class__.Menu_class(self)

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = os.path.basename(value)
        self.set_title()

    def create_status_bar(self):
        """Create Status bar """
        self.statusBar().showMessage("Ready")

    def set_title(self, title=None, file_name=None):
        title = title if title else self.title
        if file_name:
            self._file_name = file_name
        self.setWindowTitle(title + self.get_friendly_filename(self._file_name))

    def set_skybox(self):
        self.map_widget.map.skybox.get_skybox_set(skybox_id=self.skybox_id, random=self.random_skybox)

    def _set_win_properties(self):
        # set default window properties
        self.setGeometry(200, 200, 800, 600)

    def get_friendly_filename(self, file_name):
        # Get user-friendly filename. Used in the window title
        name = os.path.basename(file_name) if self._file_name else "New Graph"
        return name + ("*" if self.has_been_modified() else "")

    def _delayed_init(self):
        # cannot be initialized in the constructor, needs to be delayed until after openGL is initialized !!!!
        self.map_widget.map.add_selection_changed_listener(self.on_selection_changed)

        file = "../examples/default.json"

        try:
            if os.path.exists(file):
                self.map_widget.load_from_file(file)
                self._file_name = os.path.basename(file)
            else:
                self.map_widget.uv_new()

        except Exception as e:
            dump_exception(e)
            self.map_widget.uv_new()

    def on_selection_changed(self, sphere, items):
        """
        Each time selection in on a sphere changes, these variables get updated. Each sphere item needs a unique
        detail node editor. Even when the detail node editor is being reused we need a unique detail node editor id
        binding the detail node editor nodes to the sphere_base node.
        """

        self.selected_sphere = self.map_widget.map.target_sphere
        self.selected_sphere_items = self.map_widget.map.target_sphere.items_selected

        if len(self.selected_sphere_items) == 0:
            # no items _selected
            self.selected_sphere_item = None
        elif len(self.selected_sphere_items) > 1:
            # more than 1 item _selected: use default blank, not editable detail node-editor
            self.selected_sphere_item = None
        elif self.selected_sphere_items[0] == self.selected_sphere_item:
            # the selection has not changed. Do nothing
            return
        elif self.selected_sphere_items[0].type == 'socket':
            # A socket has been _selected. Do nothing in the detail window
            return
        else:
            # a new item has been _selected
            self.selected_sphere_item = self.selected_sphere_items[0]

    def has_been_modified(self):
        return self.map_widget.map.is_modified()

    def on_about(self):
        msg = QMessageBox()
        msg.setWindowTitle("About Sphere Base")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("<b>Sphere Base</b> is a Python program to visualize a sphere with a number of connected nodes "
                    "on its surface. Written by: Richard Boltze, email: <a>rboltze@protonmail.com")
        msg.setInformativeText("version: " + self.version)
        msg.exec()

    def on_file_new(self):
        self._file_name = ""
        self.map_widget.uv_new()
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
                    self.map_widget.load_from_file(file_name)
                    self.reset_modified()
                    self.set_title(file_name=file_name)

        except Exception as e:
            dump_exception(e)

    def on_file_save(self):
        """Handle File Save operation"""

        if not self.file_name:
            return self.on_file_save_as()

        self.file_save(self.file_name)
        self.statusBar().showMessage("Successfully saved %s" % self._file_name, 5000)
        return True

    def on_file_save_as(self):
        """Handle File Save As operation"""

        file_name, _filter = QFileDialog.getSaveFileName(self, 'Save graph to file', self.get_file_dialog_directory(),
                                                         self.get_file_dialog_filter())
        if file_name == '':
            return False

        self.file_save(file_name)
        self.statusBar().showMessage("Successfully saved as %s" % self.file_name, 5000)
        return True

    def file_save(self, filename=None):
        if filename is not None:
            self._file_name = filename

        self.map_widget.save_to_file(self._file_name)
        QApplication.restoreOverrideCursor()

        self.reset_modified()
        self.set_title()
        return True

    def may_be_saved(self) -> bool:
        """
        If any sphere_item in the sphere_iot is modified, show dialog to save the changes.
        Used before closing window.
        """
        if not self.has_been_modified():
            return True

        result = QMessageBox.warning(self, "About to loose your work?",
                                     "The document has been modified.\n Do you want to save your changes?",
                                     QMessageBox.StandardButton.Save |
                                     QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                                     )

        if result == QMessageBox.StandardButton.Save:
            return self.on_file_save()
        elif result == QMessageBox.StandardButton.Cancel:
            return False

        return True

    def reset_modified(self):
        # resetting the modified flag
        self.map_widget.map.reset_has_been_modified()
        self.on_selection_changed(None, None)

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
