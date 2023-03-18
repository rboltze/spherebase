from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QRegExpValidator
import sys

class WidgetTextureSettings(QWidget):
    color_changed = pyqtSignal()
    transparency_changed = pyqtSignal()
    skybox_startup_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # self.setGeometry(100, 100, 1400, 720)
        # self.setWindowTitle("Settings")

        self._init_Values()
        self._setup_ui()

    def _init_Values(self):
        self._red = 0
        self._green = 0
        self._blue = 0
        self._transparency = 0
        self.may_update = True
        self.Skybox_random_startup = True
        self.groupBox = QGroupBox("Textures")
        self.layout = QGridLayout()

    def _setup_ui(self):
        self._setup_texture_list()

        self.groupBox.setLayout(self.layout)

        v_box = QVBoxLayout()
        v_box.addWidget(self.groupBox)
        self.setLayout(v_box)


    def _setup_texture_list(self):

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



