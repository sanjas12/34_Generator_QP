import os
import sys
from PyQt5.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QGridLayout,
    QLineEdit,
    QMessageBox,
)
import matplotlib.pyplot as plt

from logic.Simulator import Simulator


class MainWindowUI(QMainWindow):
    def __init__(self, version: str):
        super().__init__()
        self.jump_times = []
        self.sim = None
        self.setup_ui(version)

    def setup_ui(self, version):
        self.setWindowTitle(version)

        # Добавляем новые элементы для параметров
        self.count_N = QLabel("Кол-во данных (N)*100:")
        self.input_N = QLineEdit("10")
        self.label_T = QLabel("Постоянная времени (T):")
        self.input_T = QLineEdit("0.05")
        self.label_dt = QLabel("Шаг дискретизации (dt):")
        self.input_dt = QLineEdit("0.01")
        self.label_noise = QLabel("Уровень шума (%):")
        self.input_noise = QLineEdit("1")
        self.button_update = QPushButton("Генерировать QP и график")
        self.button_update.clicked.connect(self.generate_QP)

        self.button_save = QPushButton("Сохранить QP")
        self.button_save.setEnabled(False)
        self.button_save.clicked.connect(self.save_QP)

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
        params_layout.addWidget(self.button_save, 5, 0, 1, 2)

        params_group = QGroupBox("Параметры модели")
        params_group.setLayout(params_layout)

        # main_layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(params_group)  # Добавляем новую группу с параметрами

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(main_layout)

    def dialog_box(self, text: str) -> None:
        QMessageBox.information(self, "Gen_QP", text, QMessageBox.StandardButton.Ok)

    def generate_QP(self):
        """Слот кнопки генерации QP: читает параметры, запускает симулятор и строит график."""
        try:
            count_N = int(self.input_N.text())
            T = float(self.input_T.text())
            dt = float(self.input_dt.text())
            noise_percent = float(self.input_noise.text())
        except ValueError:
            self.dialog_box("Некорректные параметры. Проверьте ввод чисел.")
            return

        # Создаём и запускаем симуляцию
        self.sim = Simulator(count_N, dt, noise_percent, T)

        # Построение графика
        plt.figure(figsize=(12, 6))
        plt.step(
            self.sim.jump_times,
            self.sim.reference_jump_values,
            "r-",
            label="Задание (идеальное) ГСМ",
            where="post",
        )
        plt.plot(self.sim.time_sim, self.sim.real_position, "b-", label="Реальное положение")
        plt.xlabel("Время (сек)")
        plt.ylabel("Положение клапана")
        plt.legend()
        plt.grid(True)
        plt.title(
            f"Моделирование работы ГСМ: T={self.sim.T}, dt={self.sim.dt}, шум={self.sim.noise_percent}%, точек={len(self.sim.time_sim)}"
        )
        plt.show()

        # Разрешаем сохранение после успешной генерации
        self.button_save.setEnabled(True)

    def save_QP(self):
        if self.sim is None:
            self.dialog_box("Сначала сгенерируйте данные.")
            return

        # Сохраняем данные симуляции в CSV используя логику симулятора
        try:
            filepath = self.sim.save_to_csv()
        except Exception as e:
            self.dialog_box(f"Ошибка сохранения: {e}")
            return

        self.dialog_box(f"Файл сохранён: {filepath}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindowUI("Generator QP")
    main_window.show()

    app.exec_()
