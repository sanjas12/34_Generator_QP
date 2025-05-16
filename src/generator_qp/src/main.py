import os
import sys
from PyQt5.QtWidgets import QApplication
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ui.MainWindowUI import MainWindowUI


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindowUI("Generator QP")
    main_window.show()

    app.exec()
 