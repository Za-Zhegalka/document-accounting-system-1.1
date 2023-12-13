import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QHeaderView, QFileDialog, \
    QInputDialog, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, QDateTime
import sqlite3

class Tab1(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Создание таблицы
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Имя файла", "Отправитель", "Время загрузки", "Прочитано", "Статус"]
        )
        layout.addWidget(self.table)

        # Создание кнопок
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.upload_button = QPushButton("Загрузить файл")
        self.delete_button = QPushButton("Удалить файл")
        self.download_button = QPushButton("Скачать файл")
        self.change_status_button = QPushButton("Изменить статус")

        button_layout.addStretch()
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.change_status_button)

        # Выравнивание кнопок по левому краю
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Установка пружинной размерной политики для расширения таблицы
        layout.addStretch()

        # Отключение редактирования ячеек таблицы
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Скрытие сетки таблицы
        self.table.setShowGrid(False)

        # Создаем стиль для выравнивания содержимого ячеек
        style = "::item { padding-right: 20px }"

        # Устанавливаем стиль для таблицы
        self.table.setStyleSheet(style)

        # Установка всплывающих подсказок для кнопок
        self.upload_button.setToolTip("Загрузить выбранный файл")
        self.delete_button.setToolTip("Удалить выбранный файл")
        self.download_button.setToolTip("Скачать выбранный файл")
        self.change_status_button.setToolTip("Изменить статус выбранного файла")

        # Подключение к базе данных
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        # Обработчики событий для кнопок
        self.upload_button.clicked.connect(self.upload_file)
        self.delete_button.clicked.connect(self.delete_file)
        self.download_button.clicked.connect(self.download_file)
        self.change_status_button.clicked.connect(self.change_status)

        # Заполняем таблицу данными из базы данных
        self.refresh_table()

    def refresh_table(self):
        self.table.clearContents()
        self.cursor.execute("SELECT name, sender, time, is_downloaded, status FROM files")
        files = self.cursor.fetchall()
        self.table.setRowCount(len(files))
        for row, file in enumerate(files):
            for col, data in enumerate(file):
                if col == 3:
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                    item.setCheckState(Qt.CheckState.Checked if data else Qt.CheckState.Unchecked)
                    self.table.setItem(row, col, item)
                else:
                    item = QTableWidgetItem(str(data))
                    self.table.setItem(row, col, item)
        for col in range(self.table.columnCount()):
            self.table.resizeColumnToContents(col)

    def upload_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Documents (*.pdf *.docx *.xlsx)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            files = file_dialog.selectedFiles()
            for file in files:
                filename = os.path.basename(file)
                sender = "Внешний пользователь"  # Заменить на имя текущего пользователя
                time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                status = "Прием документа"
                self.cursor.execute("INSERT INTO files (name, sender, time, is_downloaded, status) VALUES (?, ?, ?, ?, ?)",
                                    (filename, sender, time, 0, status))
            self.connection.commit()
            self.refresh_table()

    def delete_file(self):
        access_level = "Внешний пользователь"  # Получаем уровень доступа пользователя

        if access_level == "Администратор":
            selected_rows = self.table.selectedItems()
            if selected_rows:
                reply = QMessageBox.question(self, "Подтверждение удаления", "Вы уверены, что хотите удалить выбранные файлы?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    for item in selected_rows:
                        row = item.row()
                        file_id = self.table.item(row, 0).text()
                        self.cursor.execute("DELETE FROM files WHERE name = ?", (file_id,))
                    self.connection.commit()
                    self.refresh_table()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Недостаточно прав для удаления файла')

    def download_file(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            file_name = self.table.item(selected_row, 0).text()
            project_folder = os.path.dirname(os.path.dirname(__file__))  # Получаем папку проекта
            files_folder = os.path.join(project_folder, "Файлы")  # Создаем путь к папке Файлы
            customer_folder = os.path.join(files_folder, "Заказчик")  # Создаем путь к папке Заказчик
            # Проверяем наличие папок и создаем их, если они не существуют
            for folder in [files_folder, customer_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            file_path = os.path.join(customer_folder, file_name)  # Составляем путь для сохранения файла
            with open(file_path, 'w') as file:
                file.write("Пример содержимого файла")

            QMessageBox.information(self, 'Скачивание файла', f'Файл "{file_name}" был сохранен в папке Заказчик.')
            self.refresh_table()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите файл для скачивания')

    def change_status(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            file_id = self.table.item(selected_row, 0).text()
            current_status = self.table.item(selected_row, 4).text()
            available_statuses = ["Прием документа", "Рассмотрение документа", "Регистрация документа", "Документ принят", "Документ отклонен"]
            selected_status, ok = QInputDialog.getItem(self, "Изменить статус", "Выберите новый статус:", available_statuses, 0, False)
            if ok:
                self.cursor.execute("UPDATE files SET status = ? WHERE name = ?", (selected_status, file_id))
                self.connection.commit()
                self.refresh_table()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберите файл для изменения статуса')