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
        for index, item in enumerate(self.uv.config.all_textures.values()):
            if item['type'] == "sphere_texture":
                self.texture_list_box.insertItem(index, os.path.basename(item['file_name']))

        self.texture_list_box.itemSelectionChanged.connect(self.on_current_row_changed)
        self.layout.addWidget(self.texture_list_box)

    def on_current_row_changed(self, qmodelindex=None):
        if self.sphere.texture_id != self.texture_list_box.currentRow():
            self.sphere.texture_id = self.texture_list_box.currentRow()
            for item in self.texture_list_box.selectedItems():
                for index, _item in enumerate(self.uv.config.all_textures.values()):
                    if _item['file_name'] == item.text():
                        print(_item['texture_id'])
                        self.uv.target_sphere.texture_id = _item['texture_id']
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



