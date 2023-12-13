from PyQt6.QtWidgets import QMainWindow, QTabWidget, QPushButton
import sqlite3
from external_window.tab1 import Tab1
from admin_window.tab_admin2 import TabAdmin2
from datetime import datetime

class ExternalWindow(QMainWindow):
    def __init__(self, username, access_level, auth_window):
        super().__init__()

        self.setWindowTitle(f'Привет, {username}')
        self.setGeometry(0, 0, 800, 600)

        self.tab_widget = QTabWidget(self)

        # Создаем пустые вкладки
        self.tab1 = Tab1()
        self.tab3 = TabAdmin2(username)

        self.tab_widget.addTab(self.tab1, 'Документы')

        self.setCentralWidget(self.tab_widget)

        self.statusBar()
        self.closeEvent = self.closeEvent

        # Создаем кнопки
        self.change_user_button = QPushButton('Сменить пользователя')
        self.exit_button = QPushButton('Выйти')

        # Добавляем обработчик события для кнопки "Выйти"
        self.exit_button.clicked.connect(self.close_application)
        self.change_user_button.clicked.connect(self.change_user)

        # Сохраняем ссылку на окно авторизации
        self.auth_window = auth_window

        # Добавляем кнопки в нижнюю часть окна
        self.statusBar().addPermanentWidget(self.change_user_button)
        self.statusBar().addPermanentWidget(self.exit_button)

        # Подключение к базе данных
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        # Добавление записи о входе в историю
        self.add_action(username, "Вход в программу")

    def closeEvent(self, event):
        # Добавление записи о выходе в историю
        username = self.tab3.username
        self.add_action(username, "Выход из программы")
        event.accept()

    def close_application(self):
        self.close()

    def change_user(self):
        self.close()
        self.auth_window.refresh_user_combo()
        self.auth_window.show()

    def add_action(self, username, action):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO actions (action, user, time) VALUES (?, ?, ?)"
        self.cursor.execute(query, (action, username, current_time))
        self.connection.commit()