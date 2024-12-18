import json
import os
import sys
from PyQt6.QtWidgets import QApplication
from ui.auth_window import AuthWindow
from ui.calendar import CalendarWindow

def load_session():
    # Загружает ID текущей сессии из session.json
    session_file = "session.json"
    if os.path.exists(session_file):
        with open(session_file, "r") as f:
            data = json.load(f)
            return data.get("id")
    return None

def main():
    app = QApplication(sys.argv)
    user_id = load_session()
    if user_id:
        print(f"Сессия активна, пользователь ID: {user_id}")
        window = CalendarWindow(user_id)
    else:
        print("Сессия неактивна, требуется авторизация")
        window = AuthWindow()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    load_session()
    main()
