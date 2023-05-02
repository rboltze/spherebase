from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os


class WidgetTextureSettings(QWidget):
    texture_changed = pyqtSignal()

    def __init__(self, main_win):
        super().__init__()
        self.main_win = main_win
        self.uv = main_win.uv_widget.uv
        self.sphere = self.uv.target_sphere

        self.texture_list_box = QListWidget()
        self.groupBox = QGroupBox("Sphere textures")
        self.layout = QGridLayout()
        self._setup_ui()

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

        self.texture_list_box.setCurrentRow(self.uv.target_sphere.texture_id)
        self.texture_list_box.itemSelectionChanged.connect(self.on_current_row_changed)
        self.layout.addWidget(self.texture_list_box)

    def on_current_row_changed(self, qmodelindex=None):
        if self.sphere.texture_id != self.texture_list_box.currentRow():
            self.sphere.texture_id = self.texture_list_box.currentRow()
            for item in self.texture_list_box.selectedItems():
                for index, _item in enumerate(self.uv.config.all_textures.values()):
                    if _item['file_name'] == item.text():
                        self.uv.target_sphere.texture_id = _item['img_id']
