# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal


class LineEdit(QLineEdit):
    focus_out_event = pyqtSignal(name='focus_out_event')

    def init(self, parent):
        super().__init__(parent)

    def focusOutEvent(self, a0):
        super().focusOutEvent(a0)
        self.focus_out_event.emit()
