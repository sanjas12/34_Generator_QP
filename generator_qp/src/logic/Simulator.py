import csv
from pathlib import Path
from typing import Optional, Tuple
import gzip
import shutil
import numpy as np
from PyQt5.QtWidgets import QApplication


BASE_DIR = Path(__file__).parent.parent.absolute()
OUT_DIR = BASE_DIR / "QP_out"
OUT_FILE = OUT_DIR / "out_merge.csv"
OUT_FILE_GZ = OUT_DIR / "out_merge.csv"


class Simulator:
    """Класс для моделирования сигнала с шумом и сохранения результатов."""

    def __init__(
        self, count_N: int, dt: float, noise_percent: float, time_constant: float
    ) -> None:
        if dt <= 0:
            raise ValueError("Шаг дискретизации (dt) должен быть > 0")
        if count_N <= 0:
            raise ValueError("Время моделирования (count_N) должно быть > 0")

        self.count_N = count_N
        self.dt = dt
        self.noise_percent = noise_percent
        self.time_constant = time_constant

        # Опорные значения
        self.reference_jump_values = np.array(
            [
                0,
                10,
                20,
                10,
                30,
                10,
                60,
                10,
                100,
                110,
                100,
                120,
                100,
                150,
                100,
                200,
                210,
                200,
                220,
                200,
                250,
                200,
                300,
                320,
                300,
                10,
                0,
            ]
        )

        self.time_sim: np.ndarray
        self.real_position: np.ndarray
        self.aim_position: np.ndarray
        self.jump_times: np.ndarray

        self.generate_signal()

    def generate_signal(self) -> None:
        """Генерация сигнала с шумом."""
        self.jump_times = np.linspace(
            0, self.count_N, len(self.reference_jump_values), endpoint=False
        )
        noise_std = (self.noise_percent / 100) * np.max(self.reference_jump_values)

        # Временная ось
        self.time_sim = np.arange(0, self.count_N, self.dt)

        # Инициализация массивов
        self.real_position = np.zeros_like(self.time_sim)
        self.aim_position = np.zeros_like(self.time_sim)

        # Переменные состояния
        aim_position_current = 0.0
        ref_idx = 0

        for i, t in enumerate(self.time_sim):
            if ref_idx < len(self.jump_times) and t >= self.jump_times[ref_idx]:
                aim_position_current = float(self.reference_jump_values[ref_idx])
                ref_idx += 1

            if i > 0:
                delta = (self.dt / self.time_constant) * (
                    aim_position_current - self.real_position[i - 1]
                )
                self.real_position[i] = self.real_position[i - 1] + delta

            # Добавляем шум
            self.real_position[i] += np.random.normal(0, noise_std)

            # Сохраняем текущее значение задания
            self.aim_position[i] = aim_position_current

    def get_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Возвращает данные симуляции (время, задание, реальное положение)."""
        return self.time_sim, self.real_position, self.aim_position

    def save_to_csv(self, filename: Optional[str] = None) -> str:
        """Сохранение результатов симуляции в CSV файл."""
        if filename is None:
            file_path = OUT_FILE
        else:
            file_path = OUT_DIR / filename

        OUT_DIR.mkdir(parents=True, exist_ok=True)

        # Объединение данных
        data = np.column_stack((self.time_sim, self.aim_position, self.real_position))

        COMMON_TIME = 'Время'
        ANALYS_AIM = "Значение развертки. Положение ГСМ"
        GSM_A_CUR = "ГСМ-А.Текущее положение"

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([COMMON_TIME, ANALYS_AIM, GSM_A_CUR])
            writer.writerows(data)

        # self.save_to_gz(OUT_FILE)

        return str(file_path)

    def save_to_gz(self, filename: Optional[str] = None) -> str:
        """Сохранение результатов симуляции в CSV файл."""
        
        if filename is None:
            file_path = OUT_FILE_GZ
        else:
            file_path = OUT_DIR / filename
        
        OUT_DIR.mkdir(parents=True, exist_ok=True)

        gz_path = file_path.with_suffix(file_path.suffix + ".gz")

        # Открываем исходный файл и пишем в gzip
        with open(file_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        return str(gz_path)


if __name__ == "__main__":
    app = QApplication([])

    simulator = Simulator(count_N=10, dt=0.05, noise_percent=0.01, time_constant=1)
    print(simulator.get_data())
    print(f"Saved to: {simulator.save_to_csv()}")

    app.exec_()
