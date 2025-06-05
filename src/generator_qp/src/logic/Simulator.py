import numpy as np
from PyQt5.QtWidgets import QApplication
# from ui.MainWindowUI import MainWindowUI

class Simulator:
    def __init__(self, count_N, dt, noise_percent, time_constant):
        # Исходные данные
        # window = MainWindowUI("Generator QP")
        
        self.count_N = count_N
        self.dt = dt
        self.noise_percent = noise_percent
        self.time_constant = time_constant
        self.T = time_constant
        # window.show()

        self.reference_jump_values = np.array([0, 10, 20, 10, 30, 10, 60, 10, 100, 110, 
                                             100, 120, 100, 150, 100, 200, 210, 200, 
                                             220, 200, 250, 200, 300, 320, 300, 10, 0])
        self.generate_signal()
        
    def generate_signal(self):

        self.jump_times = np.linspace(0, self.count_N, len(self.reference_jump_values), endpoint=False)

        noise_std = (self.noise_percent / 100) * np.max(self.reference_jump_values)
        
        # Временная ось
        self.time_sim = np.arange(0, self.count_N, self.dt)
        self.real_position = np.zeros_like(self.time_sim)
        self.aim_position = 0

        # Моделирование
        ref_idx = 0
        for i, t in enumerate(self.time_sim):
            if ref_idx < len(self.jump_times) and t >= self.jump_times[ref_idx]:
                self.aim_position = self.reference_jump_values[ref_idx]
                ref_idx += 1
            if i > 0:
                self.real_position[i] = self.real_position[i-1] + (self.dt / self.T) * (self.aim_position - self.real_position[i-1])
            
            self.real_position[i] += np.random.normal(0, noise_std)

        try:
            if self.dt <= 0:
                raise ValueError("Шаг дискретизации должен быть > 0")
            if self.count_N <= 0:
                raise ValueError("Время моделирования должно быть > 0")

            # simulator.plot(time_sim, real_position, T, dt, noise_percent)
            
        except ValueError as e:
            print(e)
            # window.dialog_box(f"Ошибка ввода: {str(e)}")

    def get_data(self):
        return self.time_sim, self.real_position, self.aim_position


if __name__ == "__main__":
    app = QApplication([])
    
    simulator = Simulator(10, 0.05, 0.01, 1)

    print(simulator.get_data())

    app.exec()