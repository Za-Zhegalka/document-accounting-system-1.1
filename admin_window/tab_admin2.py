import sqlite3
import xlsxwriter as xlsxwriter
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class TabAdmin2(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Создание таблицы
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Действие", "Пользователь", "Время"])
        self.layout.addWidget(self.table_widget)

        # Подключение к базе данных
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        # Заполнение таблицы данными
        self.refresh_table()

        # Создание кнопок
        self.clear_button = QPushButton(QIcon("clear.png"), "Очистить историю")
        self.export_button = QPushButton(QIcon("export.png"), "Загрузить отчет")

        # Добавление кнопок в область с кнопками
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.clear_button)
        self.buttons_layout.addWidget(self.export_button)
        self.layout.addLayout(self.buttons_layout)

        # Добавление обработчика события для кнопок
        self.clear_button.clicked.connect(self.clear_history)
        self.export_button.clicked.connect(self.export_report)

    def refresh_table(self):
        self.table_widget.clearContents()

        # Получение данных из базы данных
        query = "SELECT action, user, time FROM actions"
        self.cursor.execute(query)
        actions = self.cursor.fetchall()

        # Установка размеров таблицы
        self.table_widget.setRowCount(len(actions))

        # Заполнение таблицы данными
        for row, action in enumerate(actions):
            for col, value in enumerate(action):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, col, item)

    def clear_history(self):
        # Очистка таблицы и базы данных
        clear_table_query = "DELETE FROM actions"
        self.cursor.execute(clear_table_query)
        self.connection.commit()

        # Обновление таблицы
        self.refresh_table()

    def export_report(self):
        # Экспорт данных таблицы в файл Excel
        filename = "report.xlsx"

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        # Запись заголовков столбцов
        headers = ["Действие", "Пользователь", "Время"]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # Запись данных из таблицы
        query = "SELECT action, user, time FROM actions"
        self.cursor.execute(query)
        actions = self.cursor.fetchall()
        for row, action in enumerate(actions):
            for col, value in enumerate(action):
                worksheet.write(row + 1, col, str(value))

        workbook.close()

        QMessageBox.information(self, "Экспорт отчета", f"Отчет успешно сохранен в файле {filename}")