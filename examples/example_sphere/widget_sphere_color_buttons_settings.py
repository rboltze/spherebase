from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from os import path


class WidgetSphereColorButtonSettings(QWidget):
    color_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._init_Values()
        self._setup_ui()

    def _init_Values(self):
        self.groupBox = QGroupBox("Default sphere colors")
        self.layout = QGridLayout()

    def _setup_ui(self):
        self._setup_buttons()

        self.groupBox.setLayout(self.layout)

        v_box = QVBoxLayout()
        v_box.addWidget(self.groupBox)
        self.setLayout(v_box)

    def _setup_buttons(self):

        btn_white = QPushButton("White", self)
        btn_white.clicked.connect(lambda: self.on_click_change('white'))
        btn_white.setToolTip("Default white sphere")

        btn_red = QPushButton("Red", self)
        btn_red.clicked.connect(lambda: self.on_click_change('red'))
        btn_red.setToolTip("Default red sphere")

        btn_green = QPushButton("Green", self)
        btn_green.clicked.connect(lambda: self.on_click_change('green'))
        btn_green.setToolTip("Default green sphere")

        btn_blue = QPushButton("Blue", self)
        btn_blue.clicked.connect(lambda: self.on_click_change('blue'))
        btn_blue.setToolTip("Default blue sphere")

        btn_yellow = QPushButton("yellow", self)
        btn_yellow.clicked.connect(lambda: self.on_click_change('yellow'))
        btn_yellow.setToolTip("Default yellow sphere")

        self.layout.addWidget(btn_white, 1, 1)
        self.layout.addWidget(btn_red, 2, 1)
        self.layout.addWidget(btn_green, 3, 1)
        self.layout.addWidget(btn_blue, 4, 1)
        self.layout.addWidget(btn_yellow, 5, 1)

        # self.groupBox.setLayout(self.layout)
        # v_box = QVBoxLayout()
        # v_box.addWidget(self.groupBox)
        # self.setLayout(v_box)

    def on_click_change(self, color=None):
        self.color_changed.emit()

