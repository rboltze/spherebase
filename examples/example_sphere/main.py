import os
import sys
from PyQt5.QtWidgets import *
from examples.example_sphere.sphere_main_win import MainWindow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    wnd = MainWindow()
    wnd.show()

    sys.exit(app.exec_())
