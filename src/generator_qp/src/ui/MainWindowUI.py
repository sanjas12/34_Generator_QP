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
        self.label_T = QLabel("Постоянная времени (T):")
        self.input_T = QLineEdit("0.05")
        self.label_dt = QLabel("Шаг дискретизации (dt):")
        self.input_dt = QLineEdit("0.01")
        self.label_noise = QLabel("Уровень шума (%):")
        self.input_noise = QLineEdit("1")
        self.button_update = QPushButton("Генерировать QP график")
        
        # Создаем layout для новых элементов
        params_layout = QGridLayout()
        params_layout.addWidget(self.label_T, 0, 0)
        params_layout.addWidget(self.input_T, 0, 1)
        params_layout.addWidget(self.label_dt, 1, 0)
        params_layout.addWidget(self.input_dt, 1, 1)
        params_layout.addWidget(self.label_noise, 2, 0)
        params_layout.addWidget(self.input_noise, 2, 1)
        params_layout.addWidget(self.button_update, 3, 0, 1, 2)

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

class MyGroupBox(QGroupBox):
    """
    Custom QGroupBox с кнопками добавления и удаления.

    Аргументы:
        title (str, optional): Заголовок группы. Defaults to None.
        name_first_button (str, optional): Текст первой кнопки. Defaults to "Add to Axe".
        name_second_button (str, optional): Текст второй кнопки. Defaults to "Remove from Axe".
        enable_first_btn (bool, optional): Включена ли первая кнопка. Defaults to True.
        enable_second_btn (bool, optional): Включена ли вторая кнопка. Defaults to True.
    """

    # Определяем тип для функции, которая может принимать 2 параметра или не принимать параметры
    FuncType = Union[Callable[[], None], Callable[[QTableWidget, Dict[str, int]], None]]

    def __init__(
        self,
        title: str = None,
        name_first_button: str = "Add to Axe",
        name_second_button: str = "Remove from Axe",
        enable_first_btn: bool = True,
        enable_second_btn: bool = True,
    ):
        super().__init__(title)

        self.dict_axe: Dict[str, int] = {}
        self.qtable_axe = CreateTable.create_table()

        self.btn_first = self._create_button(name_first_button, enable_first_btn)
        self.btn_second = self._create_button(name_second_button, enable_second_btn)

        self.lay = QVBoxLayout()
        self.lay.addWidget(self.qtable_axe)

        if enable_first_btn:
            self.lay.addWidget(self.btn_first)
        if enable_second_btn:
            self.lay.addWidget(self.btn_second)

        self.setLayout(self.lay)

    def _create_button(self, name: str, is_enabled: bool) -> QPushButton:
        """Создает кнопку с заданным текстом и состоянием."""
        btn = QPushButton(name)
        btn.setVisible(is_enabled)
        return btn

    def add_func_to_btn(self, btn: QPushButton, func: FuncType):
        """Добавляет функцию к кнопке, если она передана."""
        if func:
            btn.clicked.connect(lambda: func())
        else:
            btn.clicked.connect(lambda: print("Функция не определена"))

# для тестирования 3-x myGroupBox
class TestMyGroupBox(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        # self.layout = QVBoxLayout()
        # for _ in range(3):
        #     btn = QPushButton(str(_))
        #     self.layout.addWidget(btn)

        self.layout = QHBoxLayout()

        # self.my_group = MyGroupBox("test", "какая-то ось")
        # self.layout.addWidget(self.my_group)
        # for axe in AxeName:
        #     _ = MyGroupBox(title=axe.value)
        #     self.layout.addWidget(_)

        self.gb_base_axe = MyGroupBox("Base Axe")
        self.gb_secondary_axe = MyGroupBox("Secondary Axe")
        self.gb_x_axe = MyGroupBox("X Axe")

        for box in [self.gb_base_axe, self.gb_secondary_axe, self.gb_x_axe]:
            self.layout.addWidget(box)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def test(self, text):
        print(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # для тестирования 3-x myGroupBox создан класс TestMyGroupBox
    # window = TestMyGroupBox()    # для тестирования 3-x myGroupBox создан класс MainWindow
    # window.show()             # для тестирования 3-x myGroupBox

    # для тестирования одного myGroupBox
    # box = MyGroupBox(button_add_name="1 кнопка", title="заголовок", enable_btns=True)
    # box.add_func_to_btn(box.btn_first, lambda: test("add"))
    # box.add_func_to_btn(box.btn_second, lambda: test("remove"))
    # box.show()
    # def test(text):
    #    print(text + "  some text")

    # для тестирования главного окна
    main_window = MainWindowUI("Generator QP")
    # main_window.gb_base_axe.add_func_to_btn(main_window.gb_base_axe.btn_first, lambda: test("add to base axe"))
    # main_window.gb_base_axe.add_func_to_btn(main_window.gb_base_axe.btn_second, lambda: test("remove from base axe"))
    # main_window.gb_signals.add_func_to_btn(main_window.gb_signals.btn_first, lambda: test("add func to parser all sugnals"))
    
    def test(text):
       print(text + "  some text")
    
    main_window.show()

    app.exec()
