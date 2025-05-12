import os
import sys
from PyQt5.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTableWidget,
    QAbstractItemView,
    QLabel,
    QComboBox,
    QGridLayout,
    QLineEdit,
    QMessageBox
)
from typing import Dict, Callable, Union

# Добавляем корневую папку проекта (src) в sys.path для возможности корректного импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.config.config import AxeName


class MainWindowUI(QMainWindow):
    def __init__(self, version: str):
        super().__init__()
        self.setup_ui(version)

    def setup_ui(self, version):
        self.setWindowTitle(version)

        # Добавляем новые элементы для параметров
        self.count_N = QLabel("Кол-во данных (N):")
        self.input_N = QLineEdit("10000")
        self.label_T = QLabel("Постоянная времени (T):")
        self.input_T = QLineEdit("0.05")
        self.label_dt = QLabel("Шаг дискретизации (dt):")
        self.input_dt = QLineEdit("0.01")
        self.label_noise = QLabel("Уровень шума (%):")
        self.input_noise = QLineEdit("1")
        self.button_update = QPushButton("Генерировать QP график")
        
        # Создаем layout для новых элементов
        params_layout = QGridLayout()
        params_layout.addWidget(self.count_N, 0, 0)
        params_layout.addWidget(self.input_N, 0, 1)
        params_layout.addWidget(self.label_T, 1, 0)
        params_layout.addWidget(self.input_T, 1, 1)
        params_layout.addWidget(self.label_dt, 2, 0)
        params_layout.addWidget(self.input_dt, 2, 1)
        params_layout.addWidget(self.label_noise, 3, 0)
        params_layout.addWidget(self.input_noise, 3, 1)
        params_layout.addWidget(self.button_update, 4, 0, 1, 2)

        params_group = QGroupBox("Параметры модели")
        params_group.setLayout(params_layout)

        # main_layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(params_group)  # Добавляем новую группу с параметрами


        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(main_layout)

    def dialog_box(self, text: str) -> None:
        QMessageBox.information(self, 'TG_info', text, QMessageBox.StandardButton.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindowUI("Generator QP")
    
    def test(text):
       print(text + "  some text")
    
    main_window.show()

    app.exec()
