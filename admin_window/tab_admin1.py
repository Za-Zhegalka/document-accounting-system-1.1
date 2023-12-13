import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QHeaderView, QFileDialog, \
    QInputDialog, QTableWidgetItem
from PyQt6.QtCore import Qt, QDateTime
import sqlite3


class TabAdmin1(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Создание таблицы
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Имя файла", "Отправитель", "Время загрузки", "Статус"]
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

        # Установка размера последней колонки таблицы
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

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
        self.cursor.execute("SELECT name, sender, time, status FROM files")
        files = self.cursor.fetchall()
        self.table.setRowCount(len(files))
        for row, file in enumerate(files):
            for col, data in enumerate(file):
                item = QTableWidgetItem(str(data))
                self.table.setItem(row, col, item)

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
                self.cursor.execute("INSERT INTO files (name, sender, time, status) VALUES (?, ?, ?, ?)",
                                    (filename, sender, time, status))
            self.connection.commit()
            self.refresh_table()

    def delete_file(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            reply = QMessageBox.question(self, "Подтверждение удаления",
                                         "Вы уверены, что хотите удалить выбранные файлы?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                for index in selected_rows:
                    file_id = self.table.item(index.row(), 0).text()
                    self.cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
                self.connection.commit()
                self.refresh_table()

    def download_file(self):
        selected_row = self.table.selectionModel().selectedRows()
        if selected_row:
            file_id = self.table.item(selected_row[0].row(), 0).text()
            self.cursor.execute("SELECT name FROM files WHERE id = ?", (file_id,))
            filename = self.cursor.fetchone()[0]
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.FileMode.Directory)
            if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
                destination_path = file_dialog.selectedFiles()[0]
                self.cursor.execute("SELECT data FROM files WHERE id = ?", (file_id,))
                file_data = self.cursor.fetchone()[0]
                with open(os.path.join(destination_path, filename), "wb") as f:
                    f.write(file_data)

    def change_status(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            file_id = self.table.item(selected_rows[0].row(), 0).text()
            current_status = self.table.item(selected_rows[0].row(), 3).text()
            roles = {
                "Внешний пользователь": ["Прием документа"],
                "Пользователь": ["Прием документа", "Рассмотрение документа", "Документ отклонен"],
                "Оператор": ["Прием документа", "Рассмотрение документа", "Регистрация документа", "Документ отклонен"],
                "Администратор": ["Прием документа", "Рассмотрение документа", "Регистрация документа",
                                  "Документ принят", "Документ отклонен"]
            }
            available_statuses = roles.get("Внешний пользователь")
            if access_level == "Пользователь":
                available_statuses = roles.get("Пользователь")
            elif access_level == "Оператор":
                available_statuses = roles.get("Оператор")
            elif access_level == "Администратор":
                available_statuses = roles.get("Администратор")
            selected_status, ok = QInputDialog.getItem(self, "Изменить статус", "Выберите новый статус:",
                                                       available_statuses, current_status, False)
            if ok and selected_status != current_status:
                self.cursor.execute("UPDATE files SET status = ? WHERE id = ?", (selected_status, file_id))
                self.connection.commit()
                self.refresh_table()