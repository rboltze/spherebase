# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import os


class WidgetSkyboxSettings(QWidget):
    skybox_startup_changed = pyqtSignal()

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.uv = main_win.map_widget.map

        self._init_Values()
        self._setup_ui()

    def _init_Values(self):
        self._read_settings()
        self.skybox_list_box = QListWidget()

        self.groupBox = QGroupBox("Skybox settings")
        self.layout = QGridLayout()

    def _setup_ui(self):
        self._setup_skybox_list_box()
        self._setup_skybox_random_startup()
        self.groupBox.setLayout(self.layout)

        v_box = QVBoxLayout()
        v_box.addWidget(self.groupBox)
        self.setLayout(v_box)

    def _setup_skybox_random_startup(self):
        # setting up the check box for a random skybox at startup
        self.show_skybox_random_box = QCheckBox("Random skybox on startup")
        self.show_skybox_random_box.stateChanged.connect(self.on_click_box_skybox_startup)

        self.show_skybox_random_box.setChecked(self.skybox_random_startup)
        self.show_skybox_random_box.setToolTip("Chooses a random skybox at startup")
        self.layout.addWidget(self.show_skybox_random_box, 0, 4)

    def _setup_skybox_list_box(self):
        # setting up the listbox for choosing the skybox
        for index, txt in enumerate(self.uv.config.skybox_sets):
            if txt:
                self.skybox_list_box.insertItem(index, os.path.basename(txt))
            else:
                self.skybox_list_box.insertItem(index, 'None')

        self.skybox_list_box.setCurrentRow(self.skybox_id)
        self.skybox_list_box.itemSelectionChanged.connect(self.on_current_row_changed)
        self.layout.addWidget(self.skybox_list_box)

    def on_current_row_changed(self, qmodelindex=None):
        if self.skybox_id != self.skybox_list_box.currentRow():
            self.skybox_id = self.skybox_list_box.currentRow()
            self.uv.skybox.get_skybox_set(skybox_id=self.skybox_id)
            self._write_settings()

    def on_click_box_skybox_startup(self, state):
        self.skybox_random_startup = True if state == 2 else False
        self.skybox_startup_changed.emit()
        self._write_settings()

    def _read_settings(self):
        """Read the permanent profile settings for this app"""
        settings = QSettings(self.main_win.name_company, self.main_win.name_product)

        txt = settings.value('random_skybox', 'True')
        self.skybox_random_startup = True if txt == 'True' else False
        self.skybox_id = settings.value('skybox_id', 0)

    def _write_settings(self):
        """Write the settings"""
        settings = QSettings(self.main_win.name_company, self.main_win.name_product)
        txt = 'True' if self.skybox_random_startup else 'False'
        settings.setValue('random_skybox', txt)
        settings.setValue('skybox_id', self.skybox_id)



