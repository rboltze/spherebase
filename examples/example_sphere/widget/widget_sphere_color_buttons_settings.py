from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class WidgetSphereColorButtonSettings(QWidget):
    color_changed = pyqtSignal()

    def __init__(self, main_win):
        super().__init__()
        self.uv = main_win.sphere_widget.uv_widget.uv
        self.sphere = self.uv.target_sphere
        self._init_Values()
        self._setup_ui()

    def _init_Values(self):
        self.color = []
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

        btn_red = QPushButton("Grey", self)
        btn_red.clicked.connect(lambda: self.on_click_change('grey'))
        btn_red.setToolTip("Default grey sphere")

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

    def on_click_change(self, color=None):
        if color == 'white':
            self.color = [1, 1, 1, 0.8]
        elif color == 'grey':
            self.color = [0.68, 0.68, 0.68, 0.75]
        elif color == 'green':
            self.color = [0.68, 0.92, 0.32, 0.75]
        elif color == 'blue':
            self.color = [0.20, 0.57, 0.65, 0.75]
        elif color == 'yellow':
            self.color = [0.88, 0.7, 0.32, 0.8]
        self.uv.target_sphere.color = self.color
        self.color_changed.emit()

