import os
from pathlib import Path
import sys
from PyQt5.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from logic.Simulator import Simulator
from ui.MainWindowUI import MainWindowUI

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindowUI("Generator QP")
    
    sim = Simulator(10, 0.05, 0.01, 1)

    main_window.show()

    app.exec_()
 