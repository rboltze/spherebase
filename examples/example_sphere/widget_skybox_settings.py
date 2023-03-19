# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

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
        self.layout.addWidget(self.show_skybox_random_box, 0, 4)

    def _setup_skybox_list(self):
        self.listwidget = QListWidget()

        for index, txt in enumerate(self.uv.config.skybox_sets):
            if txt:
                self.listwidget.insertItem(index, os.path.basename(txt))
            else:
                self.listwidget.insertItem(index, 'None')

        # self.listwidget.clicked.connect(self.clicked)
        self.listwidget.currentRowChanged.connect(self.clicked)
        self.layout.addWidget(self.listwidget)

    def clicked(self, qmodelindex):
        # txt = self.listwidget.currentItem().text()
        index = self.listwidget.currentRow()
        self.uv.skybox.get_skybox_set(skybox_id=index)

    def on_click_box_skybox_startup(self, state):
        # Shows background when disable_show_background = True
        # self.show_background = True if state == 2 else False
        self.Skybox_random_startup = True if state == 2 else False
        if self.may_update:
            self.skybox_startup_changed.emit()


