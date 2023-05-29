# -*- coding: utf-8 -*-

"""
Module UV_Widget. The layer on top of the universe.

"""

from PyQt5.QtOpenGL import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QCursor

import json

from OpenGL.GL import *
from sphere_base.sphere_universe.universe import Universe
from sphere_base.constants import *
from sphere_base.utils import dump_exception


class UniverseWidget(QOpenGLWidget):

    """
    This class represents the ``Universe Widget class`` it is a pyqt5 wrapper around the OpenGL widget.

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

        self.view_width, self.view_height = self.width(), self.height()

        self.setFocusPolicy(Qt.StrongFocus)

        self._delayed_init_listeners = []
        super().setMouseTracking(True)

        self.left, self.right, self.forward, self.back, self._shift = False, False, False, False, False
        self.up, self.down, self.arrow_left, self.arrow_right = False, False, False, False
        self._left_mouse_button_down, self._right_mouse_button_down = False, False
        self._middle_mouse_button_down, self._mouse_button_down = False, False
        self._is_initialized = False
        self._first_mouse = False  # Is true ones after each mouse button press
        self.pybullet_key = None
        self._clicked_on_item = None
        self.mouse_ray_collision_point = None
        self.mouse_x, self.mouse_y = None, None
        self.uv = None
        self.is_dragging = None
        self.mouse_last_x, self.mouse_last_y = None, None

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

    def contextMenuEvent(self, event):
        """

        :param event: xy-mouse position
        :type event: 'event'
        :return:

        """
        _x, _y = event.x(), event.y()
        self._clicked_on_item, self.mouse_ray_collision_point = self.uv.mouse_ray.check_mouse_ray(_x, _y)

        if self._clicked_on_item == self.uv.target_sphere.id:
            self.handle_context_menu(event)
        return super().contextMenuEvent(event)

    def get_mouse_pos(self):
        """
        Helper function to get the object that the mouse is pointing at and to return the mouse ray collision
        point coordinates.

        """
        self._clicked_on_item, self.mouse_ray_collision_point = self.uv.mouse_ray.check_mouse_ray(self.mouse_x,
                                                                                                  self.mouse_y)
        return self._clicked_on_item, self.mouse_ray_collision_point, self.mouse_x, self.mouse_y

    def mousePressEvent(self, event):
        """
        Handles mouse press event

        :param event: contains the x and y mouse position
        :type event: 'event'

        """

        self.mouse_x, self.mouse_y = event.x(), event.y()
        self.get_mouse_pos()

        if event.button() == Qt.LeftButton:
            self._first_mouse = True
            self._left_mouse_button_down = True

            if not self._clicked_on_item:
                return

            if self._clicked_on_item == self.uv.target_sphere.id:

                # on_current_row_changed on the target sphere (background). Release selection
                self.uv.target_sphere.selected_item = None
                self.uv.target_sphere.select_item(None)
                return

            is_sphere = self.uv.set_target_sphere(self._clicked_on_item)

            if not is_sphere:
                # if it is not a sphere then get the _selected item, set selected sphere item
                self.uv.target_sphere.get_selected_item(self._clicked_on_item, self._shift)

        if event.button() == Qt.RightButton:
            self._first_mouse = True
            self._right_mouse_button_down = True

            if not self._clicked_on_item:
                return

        if event.button() == Qt.MiddleButton:
            self._first_mouse = True
            self._middle_mouse_button_down = True
            self.uv.target_sphere.last_collision_point = self.mouse_ray_collision_point

    def _reset_mouse(self):
        """
        Reset the mouse flags

        """
        self._middle_mouse_button_down = False
        self._clicked_on_item = None
        self._left_mouse_button_down = False
        self._right_mouse_button_down = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseReleaseEvent(self, event):
        """
        Handles mouse release event

        :param event: contains the x and y mouse position
        :type event: 'event'

        """

        selection = self.uv.rubber_band_box.get_selection()

        # if self.uv.target_sphere.dragging:
        if self.is_dragging:

            self.is_dragging = False
            for item in self.uv.target_sphere.items_selected:
                # Update the affected collision objects
                item.update_collision_object()
                item.is_dragging(False)
            self.uv.target_sphere.history.store_history("node moved", set_modified=True)

        if selection:
            self.uv.target_sphere.batch_selected_items(selection)

        if self.uv.target_sphere.edge_drag.dragging:
            try:
                self.get_mouse_pos()
                self.uv.target_sphere.edge_drag.drag(None, False, None)

                is_sphere = self.uv.set_target_sphere(self._clicked_on_item)

                # if it is not a sphere then get the _selected item
                if not is_sphere:
                    item = self.uv.target_sphere.get_selected_item(self._clicked_on_item, self._shift)
                    if item and item.type == "socket":
                        # if edge does not already exist, create it
                        self.uv.target_sphere.create_edge(item)
                    elif item and item.type == "sphere_node":
                        # if edge does not already exist, create it
                        self.uv.target_sphere.create_edge(item.socket)
            except Exception as e:
                dump_exception(e)

        if self._middle_mouse_button_down:
            # update all the collision objects on the sphere
            self.uv.target_sphere.update_item_collision_objects()
            self.uv.target_sphere.has_been_modified = True

        self._reset_mouse()

    def mouseMoveEvent(self, event):
        """
        Handles mouse release event

        :param event: contains the x and y mouse position
        :type event: 'event'

        """

        self.mouse_x, self.mouse_y = event.x(), event.y()
        self.get_mouse_pos()

        if self.uv.target_sphere and self.uv.cam.distance_to_target < HOVER_MIN_DISTANCE:
            hovered_item = self.uv.target_sphere.check_for_hover(self.mouse_x, self.mouse_y)
            if hovered_item:
                self.setCursor(QCursor(Qt.PointingHandCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))

        if self._left_mouse_button_down:

            if self._clicked_on_item and self.uv.target_sphere.selected_item:
                # dragging _selected items
                self.is_dragging = True
                self.setCursor(QCursor(Qt.ClosedHandCursor))
                # we are only looking at the first object in the selected objects.
                # If it is node or edge then try to drag the whole selected group of items.
                if self.uv.target_sphere.selected_item.type in ("sphere_node", "edge"):
                    self.uv.target_sphere.drag_items(self.mouse_ray_collision_point)
                elif self.uv.target_sphere.selected_item.type == "socket":
                    # drag edge from socket to the mouse_ray collision point
                    start_socket = self.uv.target_sphere.selected_item
                    self.uv.target_sphere.start_socket = start_socket
                    self.uv.target_sphere.edge_drag.drag(start_socket, True,
                                                         mouse_ray_collision_point=self.mouse_ray_collision_point)

            elif self._clicked_on_item and self._clicked_on_item == self.uv.target_sphere.id:

                if self.uv.rubber_band_box.dragging:
                    # if already dragging a rubber_band_box keep dragging
                    self.uv.rubber_band_box.drag(start=False, mouse_x=self.mouse_x, mouse_y=self.mouse_y)
                else:
                    # start a new rubber_band_box and drag its size
                    self.uv.rubber_band_box.drag(start=True, mouse_x=self.mouse_x, mouse_y=self.mouse_y)

        elif self._middle_mouse_button_down:

            x_offset, y_offset = self.get_mouse_position_offset(self.mouse_x, self.mouse_y)

            if self._clicked_on_item and self._clicked_on_item == self.uv.target_sphere.id:
                self.setCursor(QCursor(Qt.ClosedHandCursor))

                # only rotate the sphere_base over the y-axis
                self.uv.rotate_target_sphere_with_mouse(x_offset, self.mouse_ray_collision_point)

                # rotation over the x-axis are done through moving the camera
                self.uv.cam.process_mouse_movement(self.uv.target_sphere, 0, -y_offset)

    def wheelEvent(self, event):
        """
        Handles mouse wheel event.

        :param event: contains mouse wheel rotation

        """
        step = 1 if event.angleDelta().y() > 0 else -1
        radius = .05 * -step

        self.uv.cam.process_movement(self.uv.target_sphere, radius=radius)
        self.uv.target_sphere.has_been_modified = True

    def keyPressEvent(self, event):
        """
        Handles key press event

        :param event: contains the key that is pressed

        """
        if event.key() == Qt.Key_W:
            self.forward = True
        elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            # UNDO
            self.on_edit_undo()
        elif event.key() == Qt.Key_Z and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            # REDO
            self.on_edit_redo()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            # copy to clipboard
            self.on_edit_copy()
        elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
            # cut to clip board
            self.on_edit_cut()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # paste from clipboard
            self.on_edit_paste()
        elif event.key() == Qt.Key_S:
            self.back = True
        elif event.key() == Qt.Key_A:
            self.right = True
        elif event.key() == Qt.Key_Left:
            self.arrow_left = True
        elif event.key() == Qt.Key_D:
            self.left = True
        elif event.key() == Qt.Key_Right:
            self.arrow_right = True
        elif event.key() == Qt.Key_Up:
            self.up = True
        elif event.key() == Qt.Key_Down:
            self.down = True
        elif event.key() == Qt.Key_T:
            self.uv.cam.get_cam_collision_point()
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
            self.right = False
        elif event.key() == Qt.Key_Left:
            self.arrow_left = False
        elif event.key() == Qt.Key_D:
            self.left = False
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

    def handle_context_menu(self, event):
        """
        Handles context menu

        :param event: Handles context menu
        :type event: 'event

        """

        menu_style = (
            "QMenu::item{"
            "background-color: lightGrey;"
            "color: black;"
            "}"
            "QMenu::item:selected{"
            "background-color: darkGrey;"
            "color: rgb(255, 255, 255, 255);"
            "}"
        )

        context_menu = QMenu(self)
        context_menu.setStyleSheet(menu_style)
        context_menu.setGraphicsEffect(QGraphicsOpacityEffect(opacity=.8))
        create_person_node = context_menu.addAction("Person node")  # 1
        create_item_node = context_menu.addAction("Item node")  # 2

        # create_entity_node = context_menu.addAction("Entity node")  # 3
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == create_person_node:
            self.uv.target_sphere.create_new_node(1, self.mouse_ray_collision_point)
        elif action == create_item_node:
            self.uv.target_sphere.create_new_node(2, self.mouse_ray_collision_point)
        # elif action == create_entity_node:
        #     self.uv.target_sphere.create_new_node(1, self.mouse_ray_collision_point)

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
            self.uv.target_sphere.history.store_initial_history_stamp()

    def uv_new(self):
        """
        re-create the universe
        """
        self.uv.uv_new()

    def on_edit_undo(self):
        self.uv.target_sphere.on_edit_undo()

    def on_edit_redo(self):
        self.uv.target_sphere.on_edit_redo()

    def on_edit_delete(self):
        self.uv.target_sphere.on_edit_delete()

    def on_edit_cut(self):
        # cut to clip board
        self.uv.target_sphere.on_edit_cut()

    def on_edit_copy(self):
        self.uv.target_sphere.on_edit_copy()

    def on_edit_paste(self):
        # TODO: finding the center of the screen for pasting the node from the edit menu
        self.uv.target_sphere.on_edit_paste()

    def paintGL(self):
        """
        The main loop for rendering all objects

        """

        # checking if the camera is moved with the keyboard
        self.uv.do_camera_movement()

        # checking if the target sphere is rotated with the keyboard
        self.uv.rotate_target_sphere()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        self.uv.cam.draw()
        self.uv.skybox.draw()

        self.uv.draw()

        if self.uv.rubber_band_box:
            self.uv.rubber_band_box.draw()

        self.update()
