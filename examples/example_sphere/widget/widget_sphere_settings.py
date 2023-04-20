from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

SPEED_CORRECTION = 50


class WidgetSphereSettings(QWidget):
    color_changed = pyqtSignal()
    transparency_changed = pyqtSignal()
    animation_changed = pyqtSignal()

    def __init__(self, main_win):
        super().__init__()
        self.uv = main_win.sphere_widget.uv_widget.uv
        self.sphere = self.uv.target_sphere
        self._color = self.uv.target_sphere.color * SPEED_CORRECTION
        self._red = int(self._color[0] * 100)
        self._green = int(self._color[1] * 100)
        self._blue = int(self._color[2] * 100)
        self._transparency = int(self._color[3] * 100)
        self._animation = self.uv.target_sphere.animation * SPEED_CORRECTION
        self.may_update = True
        self.Skybox_random_startup = True
        self.groupBox = QGroupBox("Sphere setting")
        self.layout = QGridLayout()
        self._setup_ui()

    def _setup_ui(self):
        self._setup_red_slider()
        self._setup_green_slider()
        self._setup_blue_slider()
        self._setup_transparency_slider()
        self._setup_animation_slider()
        self.update_sliders()

        self.groupBox.setLayout(self.layout)

        v_box = QVBoxLayout()
        v_box.addWidget(self.groupBox)
        self.setLayout(v_box)

    @property
    def color(self):
        """I'm the 'x' property."""
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._red = int(self._color[0] * 100)
        self._green = int(self._color[1] * 100)
        self._blue = int(self._color[2] * 100)
        self._transparency = int(self._color[3] * 100)

        self.update_sliders()

    def do_color_change(self):
        self._color = [self._red / 100, self._green / 100, self._blue / 100, self._transparency / 100]
        self.uv.target_sphere.color = self._color

    def update_sliders(self):
        # update the values of all sliders and spin boxes
        self.sl_red.setValue(self._red)
        self.spin_red.setValue(self._red)
        self.sl_green.setValue(self._green)
        self.spin_green.setValue(self._green)
        self.sl_blue.setValue(self._blue)
        self.spin_blue.setValue(self._blue)
        self.sl_transparency.setValue(self._transparency)
        self.spin_transparency.setValue(self._transparency)
        self.sl_animation.setValue(self._animation)
        self.spin_animation.setValue(self._animation)

    def _setup_red_slider(self):
        l_red = QLabel("red:")
        self.sl_red = QSlider(Qt.Horizontal)
        self.sl_red.setMinimum(0)
        self.sl_red.setMaximum(100)
        self.sl_red.setTickPosition(QSlider.TicksBelow)
        self.sl_red.setTickInterval(45)
        self.sl_red.valueChanged.connect(self.on_red_slider_change)
        self.sl_red.setToolTip("Red value")

        self.spin_red = QSpinBox()
        self.spin_red.setMinimum(0)
        self.spin_red.setMaximum(100)
        self.spin_red.setToolTip("Red value")
        self.spin_red.valueChanged.connect(self.on_red_spin_change)

        self.layout.addWidget(l_red, 1, 0)
        self.layout.addWidget(self.sl_red, 1, 1, 1, 2)
        self.layout.addWidget(self.spin_red, 1, 3)

    def _setup_green_slider(self):
        l_green = QLabel("green:")
        self.sl_green = QSlider(Qt.Horizontal)
        self.sl_green.setMinimum(0)
        self.sl_green.setMaximum(100)
        self.sl_green.setTickPosition(QSlider.TicksBelow)
        self.sl_green.setTickInterval(45)
        self.sl_green.valueChanged.connect(self.on_green_slider_change)
        self.sl_green.setToolTip("green value")

        self.spin_green = QSpinBox()
        self.spin_green.setMinimum(0)
        self.spin_green.setMaximum(100)
        self.spin_green.setValue(self._green)
        self.spin_green.valueChanged.connect(self.on_green_spin_change)

        self.layout.addWidget(l_green, 2, 0)
        self.layout.addWidget(self.sl_green, 2, 1, 1, 2)
        self.layout.addWidget(self.spin_green, 2, 3)

    def _setup_blue_slider(self):
        l_blue = QLabel("blue:")
        self.sl_blue = QSlider(Qt.Horizontal)
        self.sl_blue.setMinimum(0)
        self.sl_blue.setMaximum(100)
        self.sl_blue.setTickPosition(QSlider.TicksBelow)
        self.sl_blue.setTickInterval(45)
        self.sl_blue.valueChanged.connect(self.on_blue_slider_change)
        self.sl_blue.setToolTip("blue value")

        self.spin_blue = QSpinBox()
        self.spin_blue.setMinimum(0)
        self.spin_blue.setMaximum(100)
        self.spin_blue.setToolTip("blue value")
        self.spin_blue.valueChanged.connect(self.on_blue_spin_change)

        self.layout.addWidget(l_blue, 3, 0)
        self.layout.addWidget(self.sl_blue, 3, 1, 1, 2)
        self.layout.addWidget(self.spin_blue, 3, 3)

    def _setup_transparency_slider(self):
        l_transparency = QLabel("transparency:")
        self.sl_transparency = QSlider(Qt.Horizontal)
        self.sl_transparency.setMinimum(0)
        self.sl_transparency.setMaximum(100)
        self.sl_transparency.setTickPosition(QSlider.TicksBelow)
        self.sl_transparency.setTickInterval(45)
        self.sl_transparency.valueChanged.connect(self.on_transparency_slider_change)
        self.sl_transparency.setToolTip("transparency")

        self.spin_transparency = QSpinBox()
        self.spin_transparency.setMinimum(0)
        self.spin_transparency.setMaximum(100)
        self.spin_transparency.setToolTip("Red value")
        self.spin_transparency.valueChanged.connect(self.on_transparency_spin_change)

        self.layout.addWidget(l_transparency, 4, 0)
        self.layout.addWidget(self.sl_transparency, 4, 1, 1, 2)
        self.layout.addWidget(self.spin_transparency, 4, 3)

    def _setup_animation_slider(self):
        l_animation = QLabel("Animation:")
        self.sl_animation = QSlider(Qt.Horizontal)
        self.sl_animation.setMinimum(-100)
        self.sl_animation.setMaximum(100)
        self.sl_animation.setTickPosition(QSlider.TicksBelow)
        self.sl_animation.setTickInterval(45)
        self.sl_animation.valueChanged.connect(self.on_animation_slider_change)
        self.sl_animation.setToolTip("Animation speed")

        self.spin_animation = QSpinBox()
        self.spin_animation.setMinimum(-100)
        self.spin_animation.setMaximum(100)
        self.spin_animation.setToolTip("Animation speed")
        self.spin_animation.valueChanged.connect(self.on_animation_spin_change)

        self.layout.addWidget(l_animation, 5, 0)
        self.layout.addWidget(self.sl_animation, 5, 1, 1, 2)
        self.layout.addWidget(self.spin_animation, 5, 3)

    def on_red_slider_change(self, state):
        self._red = self.sl_red.value()
        self.spin_red.setValue(self._red)
        self.do_color_change()
        if self.may_update:
            self.color_changed.emit()

    def on_red_spin_change(self):
        self.sl_red.setValue(self.spin_red.value())

    def on_green_slider_change(self, state):
        self._green = self.sl_green.value()
        self.spin_green.setValue(self._green)
        self.do_color_change()
        if self.may_update:
            self.color_changed.emit()

    def on_green_spin_change(self):
        self.sl_green.setValue(self.spin_green.value())

    def on_blue_slider_change(self, state):
        self._blue = self.sl_blue.value()
        self.spin_blue.setValue(self._blue)
        self.do_color_change()
        if self.may_update:
            self.color_changed.emit()

    def on_blue_spin_change(self):
        self.sl_blue.setValue(self.spin_blue.value())

    def on_transparency_slider_change(self, state):
        self._transparency = self.sl_transparency.value()
        self.spin_transparency.setValue(self._transparency)
        self.do_color_change()
        if self.may_update:
            self.transparency_changed.emit()

    def on_transparency_spin_change(self):
        self.sl_transparency.setValue(self.spin_transparency.value())

    def on_animation_slider_change(self, state):
        self._animation = self.sl_animation.value()
        self.spin_animation.setValue(self._animation)
        self.uv.target_sphere.animation = self._animation / SPEED_CORRECTION  # arbitrary value to speed down animation
        if self.may_update:
            self.animation_changed.emit()

    def on_animation_spin_change(self):
        self.sl_animation.setValue(self.spin_animation.value())


