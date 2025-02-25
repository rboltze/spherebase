# -*- coding: utf-8 -*-

from PyQt6.QtCore import Qt


"""
This class deals with the navigation keys.

"""


class KeyHandler:

    def __init__(self, map_widget):
        self.map_widget = map_widget
        self.keys = map_widget.keys

    def on_key_press(self, event):
        if event.key() == Qt.Key.Key_W:
            self.keys['forward'] = True
        elif event.key() in (Qt.Key.Key_E, Qt.Key.Key_Up):
            self.keys['up'] = True
        elif event.key() in (Qt.Key.Key_Z, Qt.Key.Key_Down):
            self.keys['down'] = True
        elif event.key() == Qt.Key.Key_S:
            self.keys['back'] = True
        elif event.key() in (Qt.Key.Key_A, Qt.Key.Key_Left):
            self.keys['right'] = True
        elif event.key() in (Qt.Key.Key_D, Qt.Key.Key_Right):
            self.keys['left'] = True
        elif event.key() == Qt.Key.Key_P:
            self.map_widget.map.skybox.get_next_set()
        elif event.key() == Qt.Key.Key_F1:
            self.map_widget.map.camera_group.get_next_camera()
        elif event.key() == Qt.Key.Key_O:
            self.map_widget.map.skybox.get_former_set()
        elif event.key() == Qt.Key.Key_Shift:
            self.keys['_shift'] = True
        elif event.key() == Qt.Key.Key_Control:
            self.keys['_ctrl'] = True

    def on_key_release(self, event):
        if event.key() == Qt.Key.Key_W:
            self.keys['forward'] = False
        elif event.key() in (Qt.Key.Key_E, Qt.Key.Key_Up):
            self.keys['up'] = False
        elif event.key() in (Qt.Key.Key_Z, Qt.Key.Key_Down):
            self.keys['down'] = False
        elif event.key() == Qt.Key.Key_S:
            self.keys['back'] = False
        elif event.key() in (Qt.Key.Key_A, Qt.Key.Key_Left):
            self.keys['right'] = False
        elif event.key() in (Qt.Key.Key_D, Qt.Key.Key_Right):
            self.keys['left'] = False
        elif event.key() == Qt.Key.Key_Shift:
            self.keys['_shift'] = False
        elif event.key() == Qt.Key.Key_Control:
            self.keys['_ctrl'] = False
