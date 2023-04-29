# -*- coding: utf-8 -*-

"""
A module containing the Main Window menu class
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from examples.example_sphere.widget.widget_settings import Settings
import pyperclip
import json


class SphereMenu(QMenu):
    def __init__(self, main_win):
        super().__init__()

        self.main_win = main_win
        self.uv_widget = self.main_win.sphere_widget.uv_widget
        self.action_new, self.action_open, self.action_save, self.action_copy = None, None, None, None
        self.action_save_as, self.action_exit, self.action_undo, self.action_paste = None, None, None, None
        self.action_redo, self.action_cut, self.action_copy, self.action_delete = None, None, None, None
        self.action_delete, self.action_separator, self.action_about, self.window_settings = None, None, None, None
        self.window_menu, self.file_menu, self.edit_menu, self.help_menu = None, None, None, None
        self.action_settings, self.status_mouse_pos = None, None

        self._init_menus()

    def _init_menus(self):
        self.create_actions()
        self.create_menus()
        self.update_edit_menu()

    def create_menus(self):
        """Create Menus for `File` and `Edit`"""
        self.create_file_menu()
        self.create_edit_menu()
        self.create_window_menu()
        self.create_help_menu()
        self.edit_menu.aboutToShow.connect(self.update_edit_menu)

    # noinspection PyUnresolvedReferences
    def create_actions(self):
        self.action_new = QAction('&New', self)
        self.action_new.setShortcuts(QKeySequence.New)
        self.action_new.setStatusTip('Create new graph')
        self.action_new.triggered.connect(self.main_win.on_file_new)

        self.action_open = QAction('&Open', self)
        self.action_open.setShortcuts(QKeySequence.Open)
        self.action_open.setStatusTip('Open file')
        self.action_open.triggered.connect(self.main_win.on_file_open)

        self.action_save = QAction('&Save', self)
        self.action_save.setShortcuts(QKeySequence.Save)
        self.action_save.setStatusTip('Save file')
        self.action_save.triggered.connect(self.main_win.on_file_save)

        self.action_save_as = QAction('Save &As...', self)
        self.action_save_as.setShortcuts(QKeySequence.SaveAs)
        self.action_save_as.setStatusTip('Save file as...')
        self.action_save_as.triggered.connect(self.main_win.on_file_save_as)

        self.action_exit = QAction('E&xit', self)
        self.action_exit.setShortcuts(QKeySequence.Close)
        self.action_exit.setStatusTip('Exit application')
        self.action_exit.triggered.connect(self.main_win.close)

        self.action_undo = QAction('&Undo', self)
        self.action_undo.setShortcuts(QKeySequence.Undo)
        self.action_undo.setStatusTip('Undo last operation')
        self.action_undo.triggered.connect(self.uv_widget.on_edit_undo)

        self.action_redo = QAction('&Redo', self)
        self.action_redo.setShortcuts(QKeySequence.Redo)
        self.action_redo.setStatusTip('Redo last operation')
        self.action_redo.triggered.connect(self.uv_widget.on_edit_redo)

        self.action_cut = QAction('Cu&t', self)
        self.action_cut.setShortcuts(QKeySequence.Cut)
        self.action_cut.setStatusTip('Cut to clipboard')
        self.action_cut.triggered.connect(self.uv_widget.on_edit_cut)

        self.action_copy = QAction('&Copy', self)
        self.action_copy.setShortcuts(QKeySequence.Copy)
        self.action_copy.setStatusTip('Copy to clipboard')
        self.action_copy.triggered.connect(self.uv_widget.on_edit_copy)

        self.action_paste = QAction('&Paste', self)
        self.action_paste.setShortcuts(QKeySequence.Paste)
        self.action_paste.setStatusTip('Paste from clipboard')
        self.action_paste.triggered.connect(self.uv_widget.on_edit_paste)

        self.action_delete = QAction('&Delete', self)
        self.action_delete.setShortcuts(QKeySequence.Delete)
        self.action_delete.setStatusTip('Delete _selected items')
        self.action_delete.triggered.connect(self.uv_widget.on_edit_paste)

        self.action_separator = QAction(self)
        self.action_separator.setSeparator(True)

        self.action_about = QAction('&About', self)
        self.action_about.setStatusTip('Show the "About" box')
        self.action_about.triggered.connect(self.main_win.on_about)

        self.action_settings = QAction('&Settings', self)
        self.action_settings.setStatusTip('Application settings')
        self.action_settings.triggered.connect(self.open_settings_window)

        self.update_edit_menu()

    def open_settings_window(self):
        self.window_settings = Settings(self.main_win)
        self.window_settings.setGeometry(QRect(400, 400, 500, 575))
        self.window_settings.setWindowFlags(self.windowFlags() | Qt.Dialog)
        self.window_settings.show()

    def create_file_menu(self):
        menu_bar = self.main_win.menuBar()
        self.file_menu = menu_bar.addMenu('&File')
        self.file_menu.addAction(self.action_new)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)

    def create_edit_menu(self):
        menu_bar = self.main_win.menuBar()
        self.edit_menu = menu_bar.addMenu('&Edit')
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addAction(self.action_redo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_delete)

    def create_window_menu(self):
        self.main_win.menuBar().addSeparator()
        self.window_menu = self.main_win.menuBar().addMenu("&Window")
        self.window_menu.addAction(self.action_settings)

    def create_help_menu(self):
        self.main_win.menuBar().addSeparator()
        self.help_menu = self.main_win.menuBar().addMenu("&Help")
        self.help_menu.addAction(self.action_about)

    def update_edit_menu(self):
        self.action_paste.setEnabled(False)
        self.action_cut.setEnabled(False)
        self.action_copy.setEnabled(False)
        self.action_delete.setEnabled(False)
        self.action_undo.setEnabled(False)
        self.action_redo.setEnabled(False)

        if self.main_win.sphere_widget.uv_widget.uv:
            active_sphere = True if self.get_sphere() else False
            active = True if len(self.get_sphere().items_selected) > 0 else False
            self.action_paste.setEnabled(active_sphere)
            self.action_cut.setEnabled(active)
            self.action_copy.setEnabled(active)
            try:
                # checking for valid json code before enabling menu
                raw_data = pyperclip.paste()
                data = json.loads(raw_data)
                if data:
                    self.action_paste.setEnabled(active)
            except ValueError:
                self.action_paste.setEnabled(False)

            self.action_delete.setEnabled(active)
            self.action_undo.setEnabled(self.get_sphere().history.can_undo())
            self.action_redo.setEnabled(self.get_sphere().history.can_redo())

    def get_sphere(self):
        # helper function to get the active target sphere_base from the sphere_iot
        return self.main_win.sphere_widget.uv_widget.uv.target_sphere

