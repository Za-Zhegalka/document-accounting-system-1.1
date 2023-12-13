from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QHeaderView
from PyQt6.QtCore import Qt

class TabUser1(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Создание таблицы
        table = QTableWidget()
        table.setRowCount(0)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            ["Имя файла", "Отправитель", "Время отправления", "Статус"]
        )
        layout.addWidget(table)

        # Создание кнопок
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        upload_button = QPushButton("Загрузить файл")
        delete_button = QPushButton("Удалить файл")
        download_button = QPushButton("Скачать файл")

        button_layout.addWidget(upload_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(download_button)

        # Выравнивание кнопок по левому краю
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Установка пружинной размерной политики для расширения таблицы
        layout.addStretch()

        # Установка размера последней колонки таблицы
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        # Отключение редактирования ячеек таблицы
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Скрытие сетки таблицы
        table.setShowGrid(False)

        # Создаем стиль для выравнивания содержимого ячеек
        style = "::item { padding-right: 20px }"

        # Устанавливаем стиль для таблицы
        table.setStyleSheet(style)

        # Установка всплывающих подсказок для кнопок
        upload_button.setToolTip("Загрузить выбранный файл")
        delete_button.setToolTip("Удалить выбранный файл")
        download_button.setToolTip("Скачать выбранный файл")