import numpy as np
from PyQt5.QtWidgets import QApplication
from ui.MainWindowUI import MainWindowUI

class ValveSimulator:
    def __init__(self):
        # Исходные данные
        window = MainWindowUI("Generator QP")
        
        count_N = int(window.input_N.text())
        dt = float(window.input_dt.text())
        noise_percent = float(window.input_noise.text())
        time_constant = float(window.input_T.text())
        T = time_constant
        window.show()

        self.reference_jump_values = np.array([0, 10, 20, 10, 30, 10, 60, 10, 100, 110, 
                                             100, 120, 100, 150, 100, 200, 210, 200, 
                                             220, 200, 250, 200, 300, 320, 300, 10, 0])
        
        self.jump_times = np.linspace(0, count_N, len(self.reference_jump_values), endpoint=False)

        noise_std = (noise_percent / 100) * np.max(self.reference_jump_values)
        
        # Временная ось
        self.time_sim = np.arange(0, count_N, dt)
        self.real_position = np.zeros_like(self.time_sim)
        self.aim_position = 0

        # Моделирование
        ref_idx = 0
        for i, t in enumerate(self.time_sim):
            if ref_idx < len(self.jump_times) and t >= self.jump_times[ref_idx]:
                self.aim_position = self.reference_jump_values[ref_idx]
                ref_idx += 1
            if i > 0:
                self.real_position[i] = self.real_position[i-1] + (dt / T) * (self.aim_position - self.real_position[i-1])
            
            self.real_position[i] += np.random.normal(0, noise_std)

        try:
            if dt <= 0:
                raise ValueError("Шаг дискретизации должен быть > 0")
            if count_N <= 0:
                raise ValueError("Время моделирования должно быть > 0")

            # simulator.plot(time_sim, real_position, T, dt, noise_percent)
            
        except ValueError as e:
            window.dialog_box(f"Ошибка ввода: {str(e)}")

    def get_data(self):
        return self.time_sim, self.real_position, self.aim_position


if __name__ == "__main__":
    app = QApplication([])
    
    simulator = ValveSimulator()
    
    app.exec()