from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

class WidgetTextureSettings(QWidget):
    texture_changed = pyqtSignal()

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.uv = main_win.sphere_widget.uv_widget.uv
        self.sphere = self.uv.target_sphere

        self._init_Values()
        self._setup_ui()

    def _init_Values(self):
        self._read_settings()
        self.texture_list_box = QListWidget()

        self.groupBox = QGroupBox("Sphere textures")
        self.layout = QGridLayout()

    def _setup_ui(self):
        self._setup_texture_list_box()

        self.groupBox.setLayout(self.layout)

        v_box = QVBoxLayout()
        v_box.addWidget(self.groupBox)
        self.setLayout(v_box)

    def _setup_texture_list_box(self):
        # setting up the listbox for choosing sphere textures
        for index, txt in enumerate(self.uv.config.sphere_textures):
            if txt:
                self.texture_list_box.insertItem(index, os.path.basename(txt))
            else:
                self.texture_list_box.insertItem(index, 'None')

        # self.texture_list_box.setCurrentRow(self.skybox_id)
        self.texture_list_box.currentRowChanged.connect(self.on_current_row_changed)
        self.texture_list_box.clicked.connect(self.on_current_row_changed)

        self.layout.addWidget(self.texture_list_box)


    def on_current_row_changed(self, qmodelindex):
        self.sphere.texture_id = self.texture_list_box.currentRow()
        # self.uv.skybox.get_skybox_set(skybox_id=self.skybox_id)

        self._write_settings()

    def _read_settings(self):
        """Read the permanent profile settings for this app"""
        settings = QSettings(self.main_win.name_company, self.main_win.name_product)

        # txt = settings.value('random_skybox', 'True')
        # self.skybox_random_startup = True if txt == 'True' else False
        # self.skybox_id = settings.value('skybox_id', 0)

    def _write_settings(self):
        """Write the settings"""
        settings = QSettings(self.main_win.name_company, self.main_win.name_product)
        # txt = 'True' if self.skybox_random_startup else 'False'
        # settings.setValue('random_skybox', txt)
        # settings.setValue('skybox_id', self.skybox_id)



