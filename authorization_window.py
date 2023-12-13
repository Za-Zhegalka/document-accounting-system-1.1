import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox, QMessageBox, QInputDialog
from admin_window.admin_window import AdminWindow
from operator_window.operator_window import OperatorWindow
from user_window.user_window import UserWindow
from external_window.external_window import ExternalWindow

class AuthorizationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Выпадающий список существующих пользователей
        self.user_combo_box = QComboBox()
        self.layout.addWidget(self.user_combo_box)

        # Поле для ввода пароля
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_field)

        # Кнопка войти в систему
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        # Кнопка выйти
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

        # Кнопка создать нового пользователя
        self.create_user_button = QPushButton("Создать пользователя")
        self.create_user_button.clicked.connect(self.create_user)
        self.layout.addWidget(self.create_user_button)

        # Подключение к базе данных
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

        # Создание таблицы пользователей, если она не существует
        create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                )
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()

        # Вставка начальных пользователей, если таблица пустая
        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]
        if count == 0:
            initial_users = [
                ("Главный менеджер", "admin_password", "Администратор"),
                ("Специалист отделения", "operator_password", "Оператор"),
                ("Секретарь", "user_password", "Пользователь"),
                ("Заказчик", "guest_password", "Внешний пользователь")
            ]
            insert_query = """
                    INSERT INTO users (username, password, role) VALUES (?, ?, ?)
                """
            self.cursor.executemany(insert_query, initial_users)
            self.connection.commit()

        # Заполнение выпадающего списка существующих пользователей
        self.refresh_user_combo()

    def refresh_user_combo(self):
        self.user_combo_box.clear()
        self.cursor.execute("SELECT username FROM users")
        users = self.cursor.fetchall()
        self.user_combo_box.addItems([user[0] for user in users])

    def login(self):
        username = self.user_combo_box.currentText()
        password = self.password_field.text()

        if not password:
            QMessageBox.warning(self, "Ошибка авторизации", "Пароль не введен")
            return

        # Проверка авторизации
        login_query = """
            SELECT COUNT(*)
            FROM users
            WHERE username = ? AND password = ?
        """
        self.cursor.execute(login_query, (username, password))
        count = self.cursor.fetchone()[0]

        if count == 1:
            role_query = """
                SELECT role
                FROM users
                WHERE username = ?
            """
            self.cursor.execute(role_query, (username,))
            role = self.cursor.fetchone()[0]

            if role == "Администратор":
                QMessageBox.information(self, "Успешная авторизация", f"Вы успешно авторизовались под \"{username}\" с правом доступа \"{role}\"")
                self.close()
                admin_window = AdminWindow(username, role, self)
                admin_window.show()
            elif role == "Оператор":
                QMessageBox.information(self, "Успешная авторизация", f"Вы успешно авторизовались под \"{username}\" с правом доступа \"{role}\"")
                self.close()
                operator_window = OperatorWindow(username, role, self)
                operator_window.show()
            elif role == "Пользователь":
                QMessageBox.information(self, "Успешная авторизация", f"Вы успешно авторизовались под \"{username}\" с правом доступа \"{role}\"")
                self.close()
                user_window = UserWindow(username, role, self)
                user_window.show()
            elif role == "Внешний пользователь":
                QMessageBox.information(self, "Успешная авторизация", f"Вы успешно авторизовались под \"{username}\" с правом доступа \"{role}\"")
                self.close()
                external_actor_window = ExternalWindow(username, role, self)
                external_actor_window.show()
            else:
                QMessageBox.warning(self, "Ошибка авторизации", "Неопределенная роль")
        else:
            QMessageBox.warning(self, "Ошибка авторизации", "Неверно введен пароль")

    def logout(self):
        QApplication.quit()

    def create_user(self):
        username, ok = QInputDialog.getText(self, "Создание пользователя", "Введите имя пользователя:")
        if ok:
            password, ok = QInputDialog.getText(self, "Создание пользователя", "Введите пароль:")
            if ok:
                try:
                    create_user_query = """
                        INSERT INTO users (username, password, role) VALUES (?, ?, "Внешний пользователь")
                    """
                    self.cursor.execute(create_user_query, (username, password))
                    self.connection.commit()
                    self.refresh_user_combo()
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Ошибка создания пользователя",
                                        "Пользователь с таким именем уже существует")