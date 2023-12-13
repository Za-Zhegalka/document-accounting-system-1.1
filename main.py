import sys
from PyQt6.QtWidgets import QApplication
from authorization_window import AuthorizationWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    auth_window = AuthorizationWindow()
    auth_window.show()
    sys.exit(app.exec())