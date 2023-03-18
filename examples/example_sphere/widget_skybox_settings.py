from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegExpValidator
import sys

class WidgetSkyboxSettings(QWidget):
    color_changed = pyqtSignal()
    transparency_changed = pyqtSignal()
    skybox_startup_changed = pyqtSignal()

    def __init__(self, uv):
        super().__init__()
        self.uv = uv
        self._init_Values()
        self._setup_ui()

    def _init_Values(self):
        self._red = 0
        self._green = 0
        self._blue = 0
        self._transparency = 0
        self.may_update = True
        self.Skybox_random_startup = True
        self.groupBox = QGroupBox("Skybox settings")
        self.layout = QGridLayout()

    def _setup_ui(self):
        self._setup_skybox_list()
        self._setup_skybox_random_startup()

        self.groupBox.setLayout(self.layout)

        v_box = QVBoxLayout()
        v_box.addWidget(self.groupBox)
        self.setLayout(v_box)


    def _setup_skybox_random_startup(self):
        self.show_skybox_random_box = QCheckBox("Random skybox on startup")
        self.show_skybox_random_box.stateChanged.connect(self.on_click_box_skybox_startup)
        self.show_skybox_random_box.setChecked(True)
        self.show_skybox_random_box.setToolTip("Chooses a random skybox at startup")
        if self.show_background:
            self.layout.addWidget(self.show_skybox_random_box, 0, 4)

    def _setup_skybox_list(self):
        # print(self.uv.config.skybox_sets)
        self.listwidget = QListWidget()
        self.listwidget.insertItem(0, "Red")
        self.listwidget.insertItem(1, "Orange")
        self.listwidget.insertItem(2, "Blue")
        self.listwidget.insertItem(3, "White")
        self.listwidget.insertItem(4, "Green")
        self.listwidget.clicked.connect(self.clicked)
        self.layout.addWidget(self.listwidget)

    def clicked(self, qmodelindex):
        item = self.listwidget.currentItem()
        print(item.text())


    def on_click_box_skybox_startup(self, state):
        # Shows background when disable_show_background = True
        self.show_background = True if state == 2 else False
        if self.may_update:
            self.skybox_startup_changed.emit()


