# -*- coding: utf-8 -*-

"""
Module UV_Widget. The layer on top of the universe.

"""

from PyQt5.QtOpenGL import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json

from OpenGL.GL import *
from sphere_base.sphere_universe_base.suv_universe import Universe
from sphere_base.constants import *


class UV_Widget(QGLWidget):
    """
    This class represents the ``Universe Widget class`` its a pyqt5 wrapper around the OpenGL widget.

    """

    Universe_class = Universe
    keyPressed = pyqtSignal(int)

    def __init__(self, parent):
        """
        Constructor of the ``UV_Widget`` class

        :param parent: reference to the parent class.

        :Instance Variables:

            - **view_width** - width of the view screen.
            - **view_height** - height of the view screen.

        """
        super().__init__(parent)
        self.setMinimumSize(640, 480)

        self._init_flags()

        self.view_width, self.view_height = self.width(), self.height()
        self._init_variables()

        self.setFocusPolicy(Qt.StrongFocus)
        self._delayed_init_listeners = []
        super().setMouseTracking(True)

    def _init_variables(self):
        self.pybullet_key = None

    def _init_flags(self):
        self._is_initialized = False
        self._clicked_on_item = None
        self._left_mouse_button_down = False
        self._right_mouse_button_down = False
        self._middle_mouse_button_down = False
        self._shift = False
        self._mouse_button_down = False
        self._first_mouse = False  # Is true ones after each mouse button press

        self.left, self.right, self.forward, self.back = False, False, False, False
        self.up, self.down, self.arrow_left, self.arrow_right = False, False, False, False

    def add_to_delayed_init(self, callback: 'function'):
        """
        Register callback for 'delayed init' event.

        :param callback: callback function

        """
        self._delayed_init_listeners.append(callback)

    def initializeGL(self):
        """
        Initialize PyQt5 OpenGl. After initializing continue with initializing any of the
        delayed initializations.

        """
        self.uv = self.__class__.Universe_class(self, pybullet_key=self.pybullet_key)

        if not self._is_initialized:

            # after GL is initialized
            for callback in self._delayed_init_listeners:
                if callback:
                    callback()

        self._is_initialized = True

    def resizeGL(self, width, height):
        """

        Resize the screen

        :param width: New width size
        :type width: ``float``
        :param height: New height size
        :type height: ``float``

        """

        self.view_width = width
        self.view_height = height
        glViewport(0, 0, width, height)

        self.uv.shader.set_window_size()
        self.uv.config.on_win_size_changed()
        self.uv.view_width = width
        self.uv.view_height = height

    def contextMenuEvent(self, event: 'event') -> 'event':
        """

        :param event: xy-mouse position
        :type event: 'event'
        :return:

        """
        x, y = event.x(), event.y()
        self._clicked_on_item, self.clicked_on_item_pos = self.uv.mouse_ray.check_mouse_ray(x, y)

        if self._clicked_on_item == self.uv.target_sphere.id:
            self.handle_context_menu(event)
        return super().contextMenuEvent(event)

    def handle_context_menu(self, event: 'event'):
        """
        Handles context menu

        :param event: Handles context menu
        :type event: 'event

        """
        x, y = event.x(), event.y()
        context_menu = QMenu(self)
        create_person_node = context_menu.addAction("Person node")  # 1
        create_item_node = context_menu.addAction("Item node")  # 2
        create_entity_node = context_menu.addAction("Entity node")  # 3
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == create_person_node:
            self.uv.target_sphere.create_new_node(1, x, y, self.clicked_on_item_pos)
        elif action == create_item_node:
            self.uv.target_sphere.create_new_node(2, x, y, self.clicked_on_item_pos)
        elif action == create_entity_node:
            self.uv.target_sphere.create_new_node(1, x, y, self.clicked_on_item_pos)

    def mousePressEvent(self, event: 'event'):
        """
        Handles mouse press event

        :param event: contains the x and y mouse position
        :type event: 'event'

        """

        x, y = event.x(), event.y()

        if event.button() == Qt.LeftButton:
            self._first_mouse = True
            self._left_mouse_button_down = True
            self._clicked_on_item, self.clicked_on_item_pos = self.uv.mouse_ray.check_mouse_ray(x, y)

            if not self._clicked_on_item:
                return

            if self._clicked_on_item == self.uv.target_sphere.id:

                # on_current_row_changed on the target sphere_base (background). Release selection
                self.uv.target_sphere.selected_item = None
                self.uv.target_sphere.select_item(None)
                return

            is_sphere = self.uv.set_target_sphere(self._clicked_on_item)

            # if it is not a sphere_base then get the _selected item

            if not is_sphere:
                # set selected sphere_base item
                self.uv.target_sphere.get_selected_item(self._clicked_on_item, self._shift)

        if event.button() == Qt.RightButton:
            self._first_mouse = True
            self._right_mouse_button_down = True
            self._clicked_on_item, self.clicked_on_item_pos = self.uv.mouse_ray.check_mouse_ray(x, y)

            if not self._clicked_on_item:
                return

        if event.button() == Qt.MiddleButton:
            self._first_mouse = True
            self._middle_mouse_button_down = True
            self._clicked_on_item, self.clicked_on_item_pos = self.uv.mouse_ray.check_mouse_ray(x, y)

    def _reset_mouse(self):
        """
        Reset the mouse flags

        """
        self._middle_mouse_button_down = False
        self._clicked_on_item = None
        self._left_mouse_button_down = False
        self._right_mouse_button_down = False

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release event

        :param event: contains the x and y mouse position
        :type event: 'event'

        """
        self._reset_mouse()

        if self.uv.target_sphere.dragging:
            for item in self.uv.target_sphere.items_selected:
                self.is_dragging = item.is_dragging(False)

        selection = self.uv.rubber_band_box.get_selection()

        if selection:
            self.uv.target_sphere.batch_selected_items(selection)
        if self.uv.target_sphere.edge_drag.dragging:
            self._clicked_on_item, self.clicked_on_item_pos = self.uv.mouse_ray.check_mouse_ray(self.mouse_x,
                                                                                                self.mouse_y)
            # self.target_sphere.edge_dragging.dragging = False
            self.uv.target_sphere.edge_drag.drag(None, None, None, False)

            is_sphere = self.uv.set_target_sphere(self._clicked_on_item)

            # if it is not a sphere_base then get the _selected item
            if not is_sphere:
                item = self.uv.target_sphere.get_selected_item(self._clicked_on_item, self._shift)
                if item and item.type == "socket":
                    # if edge does not already exist, create it
                    self.uv.target_sphere.create_edge(item)
                elif item and item.type == "node":
                    # if edge does not already exist, create it
                    self.uv.target_sphere.create_edge(item.socket)

    def mouseMoveEvent(self, event: 'event'):
        """
        Handles mouse release event

        :param event: contains the x and y mouse position
        :type event: 'event'

        """
        x, y = event.x(), event.y()
        self.mouse_x = x
        self.mouse_y = y

        if self.uv.target_sphere and self.uv.cam.distance_to_target < HOVER_MIN_DISTANCE:
            self.uv.target_sphere.check_for_hover(x, y)

        if self._left_mouse_button_down:

            if self._clicked_on_item and self.uv.target_sphere.selected_item:

                x_offset, y_offset = self.get_mouse_position_offset(x, y)

                # dragging _selected items
                if self.uv.target_sphere.selected_item.type == "node":
                    self.uv.target_sphere.drag_items(x_offset, y_offset)
                elif self.uv.target_sphere.selected_item.type == "socket":
                    # drag edge from socket
                    start_socket = self.uv.target_sphere.selected_item
                    self.uv.target_sphere.drag_edge(start_socket, x_offset, y_offset)

            elif self._clicked_on_item and self._clicked_on_item == self.uv.target_sphere.id:

                if self.uv.rubber_band_box.dragging:
                    # if already dragging a rubber_band_box keep dragging
                    self.uv.rubber_band_box.drag(start=False, mouse_x=x, mouse_y=y)
                else:
                    # start a new rubber_band_box and drag its size
                    self.uv.rubber_band_box.drag(start=True, mouse_x=x, mouse_y=y)

        elif self._middle_mouse_button_down:

            x_offset, y_offset = self.get_mouse_position_offset(x, y)

            if self._clicked_on_item and self._clicked_on_item == self.uv.target_sphere.id:
                # only rotate the sphere_base over the y axis
                self.uv.rotate_target_sphere_with_mouse(x_offset)

                # rotation over the x axis are done through moving the camera
                self.uv.cam.process_mouse_movement(self.uv.target_sphere, 0, -y_offset)
            else:
                self.uv.cam.process_mouse_movement(self.uv.target_sphere, x_offset, -y_offset)

    def wheelEvent(self, event: 'event'):
        """
        Handles mouse wheel event.

        :param event: contains mouse wheel rotation

        """
        step = 1 if event.angleDelta().y() > 0 else -1
        radius = .05 * -step

        self.uv.cam.process_movement(self.uv.target_sphere, radius=radius)

    def keyPressEvent(self, event):
        """
        Handles key press event

        :param event: contains the key that is pressed

        """
        if event.key() == Qt.Key_W:
            self.forward = True
        elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            # UNDO
            self.uv.target_sphere.history.undo()
        elif event.key() == Qt.Key_Z and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            # REDO
            self.uv.target_sphere.history.redo()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            # copy to clipboard
            self.uv.target_sphere.edit_copy()
        elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
            # cut to clip board
            self.uv.target_sphere.edit_cut()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # paste from clipboard
            self.uv.target_sphere.edit_paste()
        elif event.key() == Qt.Key_S:
            self.back = True
        elif event.key() == Qt.Key_A:
            self.left = True
        elif event.key() == Qt.Key_Left:
            self.arrow_left = True
        elif event.key() == Qt.Key_D:
            self.right = True
        elif event.key() == Qt.Key_Right:
            self.arrow_right = True
        elif event.key() == Qt.Key_Up:
            self.up = True
        elif event.key() == Qt.Key_Down:
            self.down = True
        elif event.key() == Qt.Key_P:
            self.uv.skybox.get_next_set()
        elif event.key() == Qt.Key_O:
            self.uv.skybox.get_former_set()
        elif event.key() == Qt.Key_Delete:
            self.uv.target_sphere.delete_selected_items()
        elif event.key() == Qt.Key_Shift:
            self._shift = True

    def keyReleaseEvent(self, event):
        """
        Handles key release event

        :param event: contains the key that is released

        """
        if event.key() == Qt.Key_W:
            self.forward = False
        elif event.key() == Qt.Key_S:
            self.back = False
        elif event.key() == Qt.Key_A:
            self.left = False
        elif event.key() == Qt.Key_Left:
            self.arrow_left = False
        elif event.key() == Qt.Key_D:
            self.right = False
        elif event.key() == Qt.Key_Right:
            self.arrow_right = False
        elif event.key() == Qt.Key_Up:
            self.up = False
        elif event.key() == Qt.Key_Down:
            self.down = False
        elif event.key() == Qt.Key_Shift:
            self._shift = False

    def get_mouse_position_offset(self, x_pos, y_pos):
        """
        Get difference between last stored location of the mouse on the screen
        and the current mouse position.

        :param x_pos: x position of the mouse pointer
        :param y_pos: y position of the mouse pointer
        :returns: (``float``, ``float``) x_offset, y_offset

        """

        # Offset between the current mouse pointer position and the last
        if self._first_mouse:
            # When a mouse button is pressed get the initial position
            self.mouse_last_x = x_pos
            self.mouse_last_y = y_pos
            self._first_mouse = False

        # calculate offset between the new mouse position with the last mouse position
        x_offset = x_pos - self.mouse_last_x
        y_offset = self.mouse_last_y - y_pos

        # store the new mouse position as the last mouse position
        self.mouse_last_x = x_pos
        self.mouse_last_y = y_pos

        return x_offset, y_offset

    def save_to_file(self, file_name: str):
        """
        Save json to file

        :param file_name: path and name of the file to write to
        :type file_name: str
        :return:

        """
        with open(file_name, "w") as file:
            file.write(json.dumps(self.uv.serialize(), indent=4))

    def load_from_file(self, file_name):
        """
        Load json from file

        :param file_name: path and name of the file to load from
        :type file_name: str

        """

        with open(file_name, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf-8')
            self.uv.deserialize(data)

    def uv_new(self):
        """
        re-create the sphere_iot

        """

        self.uv.uv_new()

    def paintGL(self):
        """
        The main loop for rendering all objects

        """

        self.uv.do_camera_movement()
        self.uv.rotate_target_sphere()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        self.uv.cam.draw()
        self.uv.skybox.draw()

        self.uv.draw()

        if self.uv.rubber_band_box:
            self.uv.rubber_band_box.draw()

        self.update()
