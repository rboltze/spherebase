# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *

from examples.example_sphere.sphere_uv_widget import UVWidget  # detail spheres
import os.path
from sphere_base.utils import dump_exception

TAB_NAMES = {0: "Node editor", 1: "Description"}


class SphereWidget(QWidget):
    Uv_Widget_class = UVWidget

    def __init__(self, parent):
        super().__init__()
        self.main_win = parent
        self.selected_sphere_items = []
        self.selected_sphere = None
        self.selected_sphere_item = None
        self.uv_widget = self.Uv_Widget_class(self.main_win)

        # delayed initialization waiting for OpenGL initialization
        self.uv_widget.add_to_delayed_init(self._delayed_init)
        self.title = "Sphere "

    def _delayed_init(self):
        # cannot be initialized in the constructor, needs to be delayed until after openGL is initialized !!!!
        self.uv_widget.uv.add_selection_changed_listener(self.on_selection_changed)

        file = "../examples/default.json"

        try:
            if os.path.exists(file):
                self.uv_widget.load_from_file(file)
                self.main_win.filename = os.path.basename(file)
                self.main_win.set_title()
        except Exception as e:
            dump_exception(e)
            self.uv_widget.uv_new()

    def on_modified(self):
        pass
        # self.set_title()

    def on_selection_changed(self, sphere, items):
        """
        Each time selection in on a sphere changes, these variables get updated. Each sphere item needs a unique
        detail node editor. Even when the detail node editor is being reused we need a unique detail node editor id
        binding the detail node editor nodes to the sphere_base node.
        """

        self.selected_sphere = self.uv_widget.uv.target_sphere
        self.selected_sphere_items = self.uv_widget.uv.target_sphere.items_selected

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
        return self.uv_widget.uv.is_modified()

    def set_title(self, title=None):
        title = title if title else self.title
        self.setWindowTitle(title)
