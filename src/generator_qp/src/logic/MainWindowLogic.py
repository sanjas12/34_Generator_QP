import logging
import os
import sys
from typing import Dict
import chardet
import gzip
import pandas as pd
import polars as pl
from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidgetItem, QGroupBox 

# Добавляем корневую папку проекта (src) в sys.path для возможности корректного импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import src.config.config as cfg
from src.ui.MainWindowUI import MainWindowUI, MyGroupBox
from src.ui.grath_matplot import WindowGrath


class MainWindow(MainWindowUI):
    def __init__(self, version: str):
        super().__init__(version)

        self.gb_signals.btn_first.clicked.connect(self.load_and_prepare_data)
        
        self.gb_base_axe.btn_first.clicked.connect(lambda: self.add_signal(self.gb_base_axe))
        self.gb_base_axe.btn_second.clicked.connect(lambda: self.remove_signal(self.gb_base_axe))
        
        self.gb_secondary_axe.btn_first.clicked.connect(lambda: self.add_signal(self.gb_secondary_axe))
        self.gb_secondary_axe.btn_second.clicked.connect(lambda: self.remove_signal(self.gb_secondary_axe))

    def load_and_prepare_data(self):
        """
        Загружает данные из файлов, анализирует их и подготавливает для отображения в интерфейсе.
        """
        try:
            self.clear_signals()
            self.open_files()

            if not self.files:
                return

            self.button_grath.setEnabled(True)
            self.parser_files(self.files[0])
            self.read_all_signals()
            self.update_signals_qtable(self.gb_signals)
            self.insert_time_to_x_axe()

        except EOFError:
            self.dialog_box(
                f"Ошибка в данных {self.files}. Файл испорчен. Попробуйте распаковать сторонним архиватором."
            )

    def clear_signals(self) -> None:
        """
        Clear All QTableWidgets (Список сигналов, Основная Ось, Вспомогательная, Ось X)
        и их словари
        """
        self.button_grath.setEnabled(False)

        for axe in (
            self.gb_base_axe,
            self.gb_secondary_axe,
            self.gb_x_axe,
            self.gb_signals,
        ):
            axe.dict_axe.clear()
            axe.qtable_axe.setRowCount(0)

        self.ql_info.setText(f"")
        self.is_kol_1_2 = False

    def open_files(self) -> None:
        """
        Создает список с открытыми файлами и их расширениями.
        """
        FILE_FILTERS = "GZ Files (*.gz);;CSV Files (*.csv);;TXT Files (*.txt)"
        self.files, self.extension = QFileDialog.getOpenFileNames(
            self, "Выбор данных:", filter=FILE_FILTERS
        )

        if not self.files:
            self.ql_info.setText("Файлы не выбраны.")
        else:
            # print(self.files)
            # logging.info(self.files)
            ...

    def parser_files(self, file: str = None, read_bytes: int = 20000) -> None:
        """
        Detect encoding, delimiter, decimal in opened files by first file

        :param file: Путь к файлу для анализа.
        :param read_bytes: Количество байт для чтения из файла (по умолчанию 20,000).

        """

        if not file or not os.path.isfile(file):
            self.dialog_box(f"Файл не указан или недоступен: {file}")
            return

        try:
            if file.endswith(".gz"):  # если файлы архивы
                with gzip.open(self.files[0], "rb") as f:  # type: ignore
                    data_raw = f.read(read_bytes)
                    f.seek(0)
                    second_row_raw = f.readlines()[1]  # вторая строка быстрых
            else:
                with open(self.files[0], "rb") as f:  # type: ignore
                    data_raw = f.read(read_bytes)
                    f.seek(0)
                    second_row_raw = f.readlines()[1]

            # Encoding detection
            self.encoding = chardet.detect(data_raw).get("encoding")

            if self.encoding:
                data_str = data_raw[:200].decode(self.encoding, errors="ignore")
                # Detection Koлский архив 1,2 блок
                if data_str.startswith("Count="):
                    self.is_kol_1_2 = True

                # Delimiter detection
                if data_str.count(";") > data_str.count("\t"):
                    self.delimiter = ";"
                else:
                    self.delimiter = "\t"

                # Decimal detection
                second_row_str = second_row_raw.decode(self.encoding)
                if second_row_str.count(".") > second_row_str.count(","):
                    self.decimal = "."
                else:
                    self.decimal = ","

                self.ql_info.setText(
                    f"Исходные файлы: encoding: {self.encoding} delimiter: {repr(self.delimiter)} "
                    f"decimal: {self.decimal} Кольский САРЗ 1,2 блок:{self.is_kol_1_2}"
                )
            else:
                raise ValueError("Encoding could not be detected")

        except Exception as e:
            text = (
                f"Не удалось определить параметры файла: {str(e)}\n"
                f"Не удалось определить кодировку, попробуйте разархивировать файл {file}"
            )
            self.dialog_box(text)

    def read_all_signals(self) -> None:
        """
        Считывает все сигналы из первого файла и проверяет наличие времени и миллисекунд.

        Метод выполняет следующие действия:
        1. Инициализирует флаги `is_time` и `is_ms` как `False`.
        2. Если кодировка файла не определена, выводит предупреждение и завершает выполнение.
        3. Считывает заголовки столбцов из первого файла.
        4. Удаляет лишние колонки (если есть).
        5. Создает словарь сигналов в `self.gb_signals.dict_axe`.
        6. Проверяет наличие столбцов с временем и миллисекундами, используя константы из конфигурации.
        7. Если оба столбца (время и миллисекунды) найдены, добавляет объединенное время в словарь сигналов.

        Attributes:
            is_time (bool): Флаг, указывающий на наличие столбца с временем.
            is_ms (bool): Флаг, указывающий на наличие столбца с миллисекундами.
            gb_signals.dict_axe (Dict[str, int]): Словарь, содержащий названия сигналов и их порядковые номера.

        Raises:
            FileNotFoundError: Если файл не найден.
            pd.errors.EmptyDataError: Если файл пуст.
            Exception: Если произошла ошибка при чтении файла.
        """
        self.is_time = False
        self.is_ms = False

        if not self.encoding:
            logging.warning("Кодировка файла не определена.")
            return

        # Считывание названия всех сигналов из первого файла
        if self.is_kol_1_2:
            df_all_signals = pd.read_csv(
                self.files[0],
                encoding=self.encoding,
                delimiter=self.delimiter,
                skiprows=1,
                nrows=0,
            )
        else:
            df_all_signals = pd.read_csv(self.files[0], encoding=self.encoding, delimiter=self.delimiter, nrows=0)

        # удаляем лишние колонки
        df_all_signals = df_all_signals.loc[:, ~df_all_signals.columns.str.contains("^Unnamed")]
        self.gb_signals.dict_axe = {signal: i for i, signal in enumerate(df_all_signals.columns, start=1)}

        if cfg.DEFAULT_TIME in self.gb_signals.dict_axe.keys():
            self.is_time = True
            print("дефолтное время/дата найдено")
        else:
            print("дефолтное время/дата не найдено")

        if cfg.DEFAULT_MS in self.gb_signals.dict_axe.keys():
            self.is_ms = True
            print("миллисекунды найдены")
        else:
            print("миллисекунды не найдены")

        if self.is_time and self.is_ms:
            self.gb_signals.dict_axe[cfg.COMMON_TIME] = (len(self.gb_signals.dict_axe.keys()) + 1)

    def update_signals_qtable(self, gb: MyGroupBox) -> None:
        gb.qtable_axe.setRowCount(0)
        for signal, i in sorted(gb.dict_axe.items(), key=lambda item: item[1]):
            row_position = gb.qtable_axe.rowCount()
            gb.qtable_axe.insertRow(row_position)
            
            item_signal = QTableWidgetItem(signal)
            item_signal.setToolTip(f"Название сигнала: {signal}")
            
            self.gb_signals.qtable_axe.setItem(row_position, 0, QTableWidgetItem(str(i)))
            self.gb_signals.qtable_axe.setItem(row_position, 1, item_signal)

    def insert_time_to_x_axe(self) -> None:
        self.gb_x_axe.dict_axe.clear()
        if self.is_time and self.is_ms:
            last_row_index = self.gb_signals.qtable_axe.rowCount() - 1
            print(last_row_index)
            self.gb_signals.qtable_axe.selectRow(last_row_index)
            self.add_signal(self.gb_x_axe)
        elif self.is_time:
            self.gb_signals.qtable_axe.selectRow(0)
            self.add_signal(self.gb_x_axe)
        else:
            self.dialog_box("Данные для времени не найдены")
        
        self.gb_signals.qtable_axe.selectRow(0)

    def add_signal(self,  gb: MyGroupBox) -> None:
        """
        Remove signal from Qtable(Список сигналов) and append his to qtable(переданного GroubBox) and dict_axe
        """
        print(self.gb_signals.dict_axe)
        if self.gb_signals.qtable_axe.rowCount() and self.gb_signals.qtable_axe.currentRow() > -1:
            row = self.gb_signals.qtable_axe.currentRow()
            print({row})
            index_signal = self.gb_signals.qtable_axe.item(row, 0).text() # type: ignore
            signal = self.gb_signals.qtable_axe.item(row, 1).text() # type: ignore
            gb.dict_axe.setdefault(signal, int(index_signal))
            print(gb.dict_axe)
            self.gb_signals.qtable_axe.removeRow(row)
            self.gb_signals.dict_axe.pop(signal) 
            print(self.gb_signals.dict_axe)
            
            self.update_signals_qtable(gb)
            # self.update_signals_qtable(self.gb_signals)
        else:
            self.dialog_box(f"Don't open files.\nDon't select signal.\nAll signals are already selected.")
        
    def remove_signal(self, gb: MyGroupBox) -> None:
        """
        Remove signal from Qtable(given Qtable) and append his to Qtable(Список сигналов) and dict_axe
        """
        if gb.qtable_axe.rowCount() and gb.qtable_axe.currentRow() > -1:
            row = gb.qtable_axe.currentRow()
            index_signal = gb.qtable_axe.item(row, 0).text()  # type: ignore
            signal = gb.qtable_axe.item(row, 1).text()  # type: ignore
            self.gb_signals.dict_axe.setdefault(signal, int(index_signal))
            gb.qtable_axe.removeRow(row)
            gb.dict_axe.pop(signal)

            self.update_signals_qtable(self.gb_signals)
        else:
            self.dialog_box("don't select signals for removing")

    def load_data_for_plot(self) -> None:
        """Загружает данные из файлов для построения графика"""
        self.df = None
        self.base_signals = self.selected_signals(
            self.gb_base_axe.qtable_axe, cfg.AxeName.BASE_AXE.value
        )
        self.secondary_signals = self.selected_signals(
            self.gb_secondary_axe.qtable_axe, cfg.AxeName.SECONDARY_AXE.value
        )
        self.x_axe = self.selected_signals(
            self.gb_x_axe.qtable_axe, cfg.AxeName.X_AXE.value
        )

        # Очистка состояния
        self.ready_plot = False
        self.base_signals.clear()
        self.secondary_signals.clear()

        if not self.files or not (self.base_signals or self.secondary_signals):
            self.dialog_box("Не выбраны сигналы")
            return

        usecols = self.base_signals + self.secondary_signals + self.x_axe
        if self.is_time and self.is_ms:
            usecols.extend([cfg.DEFAULT_TIME, cfg.DEFAULT_MS])

        # Используем polars для ускорения загрузки
        try:
            self.df = pl.concat(
                [
                    pl.read_csv(
                        file,
                        encoding=self.encoding,
                        separator=self.delimiter,
                        columns=usecols,
                        dtypes={col: pl.Float64 for col in usecols},
                        skip_rows=1 if self.is_kol_1_2 else 0,
                    )
                    for file in self.files
                ]
            ).to_pandas()
        except Exception as e:
            self.dialog_box(f"Ошибка при загрузке данных: {e}")
            return

        # Если нужны объединённые временные метки
        if self.is_time and self.is_ms:
            self.df[cfg.COMMON_TIME] = (
                self.df[cfg.DEFAULT_TIME].astype(str)
                + ","
                + self.df[cfg.DEFAULT_MS].astype(str)
            )

        self.number_raw_point.setText(str(len(self.df.index)))
        self.ready_plot = True

        def plot_grath(self) -> None:
            self.load_data_for_plot()

            if self.ready_plot:
                self.number_plot_point.setText(
                    str(int(len(self.df.index) / int(self.combobox_dot.currentText())))
                )
                self.grath = WindowGrath(
                    self.df,
                    self.base_signals,
                    self.secondary_signals,
                    *self.x_axe,
                    step=self.combobox_dot.currentText(),
                    filename=self.files[0],
                )
                self.grath.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    font_size = cfg.FONT_SIZE
    style = f"""
        * {{
        font-size: {font_size}pt;
        font-family: Arial;
        }}
    """
    app.setStyleSheet(style)

    main_window = MainWindow("Test")
    main_window.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Ошибка при выполнении приложения: {e}")
    finally:
        logging.info("Приложение завершено.")
