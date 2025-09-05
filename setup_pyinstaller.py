# Альтернативный setup.py для PyInstaller
import PyInstaller.__main__
import os

# Путь к основному файлу
main_file = "generator_qp/src/main.py"

# Опции для PyInstaller
options = [
    main_file,
    '--onefile',  # Создать один исполняемый файл
    '--windowed',  # Без консольного окна
    '--name=Generator_QP',  # Имя выходного файла
    '--add-data=generator_qp/src/Documentation;Documentation',  # Включить документацию
    '--hidden-import=numpy.core._methods',
    '--hidden-import=numpy.lib.format',
    '--hidden-import=numpy.random._pickle',
    '--hidden-import=matplotlib.backends.backend_qt5agg',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=PyQt5.QtGui',
    '--collect-all=numpy',
    '--collect-all=matplotlib',
    '--collect-all=pandas',
    '--collect-all=PyQt5',
]

# Запуск сборки
PyInstaller.__main__.run(options)

