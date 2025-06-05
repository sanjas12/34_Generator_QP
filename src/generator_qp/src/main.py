import os
import sys
from PyQt5.QtWidgets import QApplication
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.ui.MainWindowUI import MainWindowUI
from src.logic.Simulator import Simulator


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindowUI("Generator QP")
    
    sim = Simulator(10, 0.05, 0.01, 1)

    main_window.show()



    app.exec()
 