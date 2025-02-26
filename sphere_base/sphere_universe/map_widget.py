# -*- coding: utf-8 -*-

"""
Module UV_Widget. The layer on top of the map.

"""

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import json

from OpenGL.GL import *
from sphere_base.sphere_universe.map import Map
from sphere_base.utils.key_handler import KeyHandler
from sphere_base.constants import *
from sphere_base.utils.utils import dump_exception


class MapWidget(QOpenGLWidget):
    """
    This class represents the ``Map Widget class`` it is a PyQt6 wrapper around the OpenGL widget.

    """

    Map_class = Map
    # keyPressed = pyqtSignal(int)
    keys = {'right': False, 'left': False, 'forward': False, 'back': False,
            'up': False, 'down': False, '_shift': False, '_ctrl': False}

    def __init__(self, parent):

        super().__init__(parent)
        super().setMouseTracking(True)

        self.left, self.right, self.forward, self.back, self._shift = False, False, False, False, False
        self.up, self.down, self.arrow_left, self.arrow_right = False, False, False, False
        self._left_mouse_button_down, self._right_mouse_button_down, self._mouse_button_down = False, False, False
        self._middle_mouse_button_down, self._is_initialized, self._first_mouse  = False, False, False
        self.pybullet_key, self._clicked_on_item, self.mouse_ray_collision_point = None, None, None
        self.mouse_x, self.mouse_y, self.map, self.is_dragging = None, None, None, None
        self.mouse_last_x, self.mouse_last_y = None, None
        self._delayed_init_listeners = []

        self.setMinimumSize(640, 480)
        self.view_width, self.view_height = self.width(), self.height()

        self.key_handler = KeyHandler(self)

        self.format = QSurfaceFormat()
        self.surface = QOffscreenSurface()

        self._init_ui()
        self._init_open_gl()

    def _init_ui(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _init_open_gl(self):
        # configuring QOpenGLWidget Opengl
        self.format.setDepthBufferSize(24)
        self.format.setStencilBufferSize(8)
        self.format.setSamples(4)
        self.format.setVersion(4, 2)
        QSurfaceFormat.setDefaultFormat(self.format)

        self.surface.create()
        # self.context = QOpenGLContext()
        # self.context.setFormat(self.format)
        # self.context.create()
        # QOpenGLContext.setShareContext(self.context, self.context)

    def add_to_delayed_init(self, callback: 'function'):
        # Register callback for 'delayed init' event.
        self._delayed_init_listeners.append(callback)

    def initializeGL(self):
        # Initialize PyQt6 OpenGl. After initializing continue with initializing any of the delayed initializations.
        print("here")
        self.map = self.__class__.Map_class(self, pybullet_key=self.pybullet_key)

        if not self._is_initialized:

            # after GL is initialized
            for callback in self._delayed_init_listeners:
                if callback:
                    callback()

        self._is_initialized = True

    def resizeGL(self, width, height):
        # Resize the screen

        self.view_width = width
        self.view_height = height
        glViewport(0, 0, width, height)

        self.map.shader.set_window_size()
        self.map.config.on_win_size_changed()
        self.map.view_width = width
        self.map.view_height = height

    def contextMenuEvent(self, event):
        _x, _y = event.x(), event.y()
        self._clicked_on_item, self.mouse_ray_collision_point = self.map.mouse_ray.check_mouse_ray(_x, _y)

        if self._clicked_on_item == self.map.target_sphere.id:
            self.handle_context_menu(event)
        return super().contextMenuEvent(event)

    def get_mouse_pos(self):
        # Helper function to get the object and to return the mouse ray collision point coordinates.

        self._clicked_on_item, self.mouse_ray_collision_point = self.map.mouse_ray.check_mouse_ray(self.mouse_x,
                                                                                                   self.mouse_y)
        return self._clicked_on_item, self.mouse_ray_collision_point, self.mouse_x, self.mouse_y

    def mousePressEvent(self, event):
        # overrides PyQt mousePressEvent
        self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
        self.get_mouse_pos()

        if event.button() == Qt.MouseButton.LeftButton:
            self._first_mouse = True
            self._left_mouse_button_down = True

            if not self._clicked_on_item:
                return

            if self._clicked_on_item == self.map.target_sphere.id:

                # on_current_row_changed on the target sphere (background). Release selection
                self.map.target_sphere.selected_item = None
                self.map.target_sphere.select_item(None)
                return

            is_sphere = self.map.set_target_sphere(self._clicked_on_item)

            if not is_sphere:
                # if it is not a sphere then get the _selected item, set selected sphere item
                self.map.target_sphere.get_selected_item(self._clicked_on_item, self._shift)

        if event.button() == Qt.MouseButton.RightButton:
            self._first_mouse = True
            self._right_mouse_button_down = True

            if not self._clicked_on_item:
                return

        if event.button() == Qt.MouseButton.MiddleButton:
            self._first_mouse = True
            self._middle_mouse_button_down = True
            self.map.target_sphere.last_collision_point = self.mouse_ray_collision_point

    def _reset_mouse(self):
        # reset the flags
        self._middle_mouse_button_down = False
        self._clicked_on_item = None
        self._left_mouse_button_down = False
        self._right_mouse_button_down = False
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseReleaseEvent(self, event):
        # overrides PyQt mouse release event

        selection = self.map.rubber_band_box.get_selection()

        # if self.map.target_sphere.dragging:
        if self.is_dragging:

            self.is_dragging = False
            for item in self.map.target_sphere.items_selected:
                # Update the affected collision objects
                item.update_collision_object()
                item.is_dragging(False)
            self.map.target_sphere.history.store_history("node moved", set_modified=True)

        if selection:
            self.map.target_sphere.batch_selected_items(selection)

        if self.map.target_sphere.edge_drag.dragging:
            try:
                self.get_mouse_pos()
                self.map.target_sphere.edge_drag.drag(None, False, None)

                is_sphere = self.map.set_target_sphere(self._clicked_on_item)

                # if it is not a sphere then get the _selected item
                if not is_sphere:
                    item = self.map.target_sphere.get_selected_item(self._clicked_on_item, self._shift)
                    if item and item.type == "socket":
                        # if edge does not already exist, create it
                        self.map.target_sphere.create_edge(item)
                    elif item and item.type == "sphere_node":
                        # if edge does not already exist, create it
                        self.map.target_sphere.create_edge(item.socket)
            except Exception as e:
                dump_exception(e)

        if self._middle_mouse_button_down:
            # update all the collision objects on the sphere
            self.map.target_sphere.update_item_collision_objects()
            self.map.target_sphere.has_been_modified = True

        self._reset_mouse()

    def mouseMoveEvent(self, event):
        # overrides PyQt mouseMoveEvent

        if not self.underMouse():
            # Do not react on movement outside the widget
            return

        self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
        self.get_mouse_pos()

        if self.map.target_sphere and self.map.cam.distance_to_target < HOVER_MIN_DISTANCE:
            hovered_item = self.map.target_sphere.check_for_hover(self.mouse_x, self.mouse_y)
            if hovered_item:
                self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if self._left_mouse_button_down:

            if self._clicked_on_item and self.map.target_sphere.selected_item:
                # dragging _selected items
                self.is_dragging = True
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                # we are only looking at the first object in the selected objects.
                # If it is node or edge then try to drag the whole selected group of items.
                if self.map.target_sphere.selected_item.type in ("sphere_node", "edge"):
                    self.map.target_sphere.drag_items(self.mouse_ray_collision_point)
                elif self.map.target_sphere.selected_item.type == "socket":
                    # drag edge from socket to the mouse_ray collision point
                    start_socket = self.map.target_sphere.selected_item
                    self.map.target_sphere.start_socket = start_socket
                    self.map.target_sphere.edge_drag.drag(start_socket, True,
                                                          mouse_ray_collision_point=self.mouse_ray_collision_point)

            elif self._clicked_on_item and self._clicked_on_item == self.map.target_sphere.id:

                if self.map.rubber_band_box.dragging:
                    # if already dragging a rubber_band_box keep dragging
                    self.map.rubber_band_box.drag(start=False, mouse_x=self.mouse_x, mouse_y=self.mouse_y)
                else:
                    # start a new rubber_band_box and drag its size
                    self.map.rubber_band_box.drag(start=True, mouse_x=self.mouse_x, mouse_y=self.mouse_y)

        elif self._middle_mouse_button_down:

            x_offset, y_offset = self.get_mouse_position_offset(self.mouse_x, self.mouse_y)

            if self._clicked_on_item and self._clicked_on_item == self.map.target_sphere.id:
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

                # only rotate the sphere_base over the y-axis
                self.map.rotate_target_sphere_with_mouse(x_offset, self.mouse_ray_collision_point)

                # rotation over the x-axis are done through moving the camera
                self.map.cam.process_mouse_movement(self.map.target_sphere, 0, -y_offset)

    def wheelEvent(self, event):
        step = 1 if event.angleDelta().y() > 0 else -1
        radius = .05 * -step

        self.map.cam.process_movement(self.map.target_sphere, radius=radius)
        self.map.target_sphere.has_been_modified = True

    def keyPressEvent(self, event):
        self.key_handler.on_key_press(event)
        # if event.key() == Qt.Key.Key_W:
        #     self.forward = True
        # elif event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     # UNDO
        #     self.on_edit_undo()
        # elif event.key() == Qt.Key.Key_Z and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
        #     # REDO
        #     self.on_edit_redo()
        # elif event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     # copy to clipboard
        #     self.on_edit_copy()
        # elif event.key() == Qt.Key.Key_X and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     # cut to clip board
        #     self.on_edit_cut()
        # elif event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        #     # paste from clipboard
        #     self.on_edit_paste()
        # elif event.key() == Qt.Key.Key_S:
        #     self.back = True
        # elif event.key() == Qt.Key.Key_A:
        #     self.right = True
        # elif event.key() == Qt.Key.Key_Left:
        #     self.arrow_left = True
        # elif event.key() == Qt.Key.Key_D:
        #     self.left = True
        # elif event.key() == Qt.Key.Key_Right:
        #     self.arrow_right = True
        # elif event.key() == Qt.Key.Key_Up:
        #     self.up = True
        # elif event.key() == Qt.Key.Key_Down:
        #     self.down = True
        # elif event.key() == Qt.Key.Key_T:
        #     self.map.cam.get_cam_collision_point()
        # elif event.key() == Qt.Key.Key_P:
        #     self.map.skybox.get_next_set()
        # elif event.key() == Qt.Key.Key_O:
        #     self.map.skybox.get_former_set()
        # elif event.key() == Qt.Key.Key_Delete:
        #     self.map.target_sphere.delete_selected_items()
        # elif event.key() == Qt.Key.Key_Shift:
        #     self._shift = True

    def keyReleaseEvent(self, event):
        self.key_handler.on_key_release(event)
        # if event.key() == Qt.Key.Key_W:
        #     self.forward = False
        # elif event.key() == Qt.Key.Key_S:
        #     self.back = False
        # elif event.key() == Qt.Key.Key_A:
        #     self.right = False
        # elif event.key() == Qt.Key.Key_Left:
        #     self.arrow_left = False
        # elif event.key() == Qt.Key.Key_D:
        #     self.left = False
        # elif event.key() == Qt.Key.Key_Right:
        #     self.arrow_right = False
        # elif event.key() == Qt.Key.Key_Up:
        #     self.up = False
        # elif event.key() == Qt.Key.Key_Down:
        #     self.down = False
        # elif event.key() == Qt.Key.Key_Shift:
        #     self._shift = False

    def get_mouse_position_offset(self, x_pos, y_pos):
        # Get difference between last stored location of the mouse on the screen
        # and the current mouse position.

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
        action = context_menu.exec(self.mapToGlobal(event.pos()))

        if action == create_person_node:
            self.map.target_sphere.create_new_node(1, self.mouse_ray_collision_point)
        elif action == create_item_node:
            self.map.target_sphere.create_new_node(2, self.mouse_ray_collision_point)
        # elif action == create_entity_node:
        #     self.map.target_sphere.create_new_node(1, self.mouse_ray_collision_point)

    def save_to_file(self, file_name: str):
        # Save json to file
        with open(file_name, "w") as file:
            file.write(json.dumps(self.map.serialize(), indent=4))

    def load_from_file(self, file_name):
        # Load json from file

        with open(file_name, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)

            self.map.deserialize(data)
            # self.map.target_sphere.history.store_initial_history_stamp()

    def uv_new(self):
        # re-create the map
        self.map.uv_new()

    def on_edit_undo(self):
        self.map.target_sphere.on_edit_undo()

    def on_edit_redo(self):
        self.map.target_sphere.on_edit_redo()

    def on_edit_delete(self):
        self.map.target_sphere.on_edit_delete()

    def on_edit_cut(self):
        # cut to clip board
        self.map.target_sphere.on_edit_cut()

    def on_edit_copy(self):
        self.map.target_sphere.on_edit_copy()

    def on_edit_paste(self):
        # TODO: finding the center of the screen for pasting the node from the edit menu
        self.map.target_sphere.on_edit_paste()

    def paintGL(self):
        """
        The main loop for rendering all objects

        """

        # checking if the camera is moved with the keyboard
        self.map.do_camera_movement()

        # checking if the target sphere is rotated with the keyboard
        self.map.rotate_target_sphere()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        self.map.cam.draw()
        self.map.skybox.draw()

        self.map.draw()

        if self.map.rubber_band_box:
            self.map.rubber_band_box.draw()

        self.update()
