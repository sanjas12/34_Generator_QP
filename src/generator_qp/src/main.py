import numpy as np
import matplotlib.pyplot as plt

# Исходные данные
reference_jump_values = np.array([0, 10, 20, 10, 30, 10, 60, 10, 100, 110, 100, 120, 100, 150, 100, 200, 210, 
                                200, 220, 200, 250, 200, 300, 320, 300, 10, 0])
jump_times = np.linspace(0, 10, len(reference_jump_values), endpoint=False)

# Параметры модели
T = 0.05  # Постоянная времени (сек) - точность выхода на задание (по умолчанию 0.05)
dt = 0.01  # Шаг дискретизации (сек) (по умолчанию 0.01)
noise_std = 0.01 * np.max(reference_jump_values)  # Уровень шума (1%) (по умолчанию 0.01)


# Временная ось (более частая, чем jump_times)
time_sim = np.arange(0, 10 + dt, dt) # 1001 значений
# print(len(time_sim))

# Инициализация
real_position = np.zeros_like(time_sim)
current_ref = 0

# Моделирование
ref_idx = 0
for i, t in enumerate(time_sim):
    # Обновление задания, если наступил момент скачка
    if ref_idx < len(jump_times) and t >= jump_times[ref_idx]:
        current_ref = reference_jump_values[ref_idx]
        ref_idx += 1
    
    # Динамика системы (разностное уравнение)
    if i > 0:
        real_position[i] = real_position[i-1] + (dt / T) * (current_ref - real_position[i-1])
    
    # Добавление шума
    real_position[i] += np.random.normal(0, noise_std)

# Построение графиков
plt.figure(figsize=(12, 6))
plt.step(jump_times, reference_jump_values, 'r-', label='Задание (идеальное)', where='post')
plt.plot(time_sim, real_position, 'b-', label='Реальное положение')
plt.xlabel('Время (сек)')
plt.ylabel('Положение клапана')
plt.legend()
plt.grid(True)
plt.title('Моделирование работы клапана с инерционностью')
plt.show()