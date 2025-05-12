# src\generator_qp\src\main.py
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication
from ui.MainWindowUI import MainWindowUI

class ValveSimulator:
    def __init__(self):
        # Исходные данные
        self.reference_jump_values = np.array([0, 10, 20, 10, 30, 10, 60, 10, 100, 110, 
                                             100, 120, 100, 150, 100, 200, 210, 200, 
                                             220, 200, 250, 200, 300, 320, 300, 10, 0])
        self.jump_times = np.linspace(0, 10, len(self.reference_jump_values), endpoint=False)
        
    def simulate(self, T, dt, noise_percent):
        noise_std = (noise_percent / 100) * np.max(self.reference_jump_values)
        
        # Временная ось
        time_sim = np.arange(0, 10 + dt, dt)
        real_position = np.zeros_like(time_sim)
        current_ref = 0

        # Моделирование
        ref_idx = 0
        for i, t in enumerate(time_sim):
            if ref_idx < len(self.jump_times) and t >= self.jump_times[ref_idx]:
                current_ref = self.reference_jump_values[ref_idx]
                ref_idx += 1
            
            if i > 0:
                real_position[i] = real_position[i-1] + (dt / T) * (current_ref - real_position[i-1])
            
            real_position[i] += np.random.normal(0, noise_std)
        
        return time_sim, real_position

    def plot(self, time_sim, real_position):
        plt.figure(figsize=(12, 6))
        plt.step(self.jump_times, self.reference_jump_values, 'r-', 
                label='Задание (идеальное)', where='post')
        plt.plot(time_sim, real_position, 'b-', label='Реальное положение')
        plt.xlabel('Время (сек)')
        plt.ylabel('Положение клапана')
        plt.legend()
        plt.grid(True)
        plt.title('Моделирование работы ГСМ с инерционностью')
        plt.show()

if __name__ == "__main__":
    app = QApplication([])
    
    simulator = ValveSimulator()
    window = MainWindowUI("Generator QP")
    
    def update_plot():
        try:
            T = float(window.input_T.text())
            dt = float(window.input_dt.text())
            noise_percent = float(window.input_noise.text())
            
            time_sim, real_position = simulator.simulate(T, dt, noise_percent)
            simulator.plot(time_sim, real_position)
            
        except ValueError as e:
            window.dialog_box(f"Ошибка ввода: {str(e)}")
    
    window.button_update.clicked.connect(update_plot)
    window.show()
    app.exec()