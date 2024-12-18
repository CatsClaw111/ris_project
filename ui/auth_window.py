import json
import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from ui.calendar import CalendarWindow

# Функция для подключения к базе данных SQLite
def create_connection():
    conn = sqlite3.connect('database/database.db')
    return conn

# Проверка наличия пользователя в базе данных
def check_user_credentials(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_new_user(username, password):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        # Сообщение об успехе только после успешной вставки
        QMessageBox.information(None, "Успех", "Регистрация прошла успешно!")
    except sqlite3.IntegrityError:
        # Выводим сообщение об ошибке при дублирующемся логине
        QMessageBox.warning(None, "Ошибка", "Пользователь с таким именем уже существует!")

# Функция для загрузки данных из session.json
def load_session():
    try:
        with open('session.json', 'r') as f:
            session_data = json.load(f)
            return session_data.get('user_id')
    except FileNotFoundError:
        return None

# Функция для сохранения ID пользователя в session.json
def save_session(user_id):
    with open('session.json', 'w') as f:
        json.dump({"user_id": user_id}, f)


# Окно авторизации
class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(400, 200, 300, 200)

        # Создание элементов
        self.layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти", self)
        self.register_button = QPushButton("Зарегистрироваться", self)

        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

        # Подключение кнопок
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def login(self):
        """Проверяет логин пользователя, сохраняет ID в сессии и открывает календарь."""
        username = self.username_input.text()
        password = self.password_input.text()

        if self.check_credentials(username, password):  # Вызов метода проверки
            print("Успешный вход")

            # Получение ID пользователя
            conn = sqlite3.connect("database/database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = cursor.fetchone()[0]
            conn.close()

            with open("session.json", "w") as f:
                json.dump({"id": user_id}, f)

            self.close()

            # Открывается окно календаря
            self.calendar_window = CalendarWindow(user_id)  # ! Передаём ID пользователя
            self.calendar_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль.")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя и пароль не могут быть пустыми!")
            return

        add_new_user(username, password)
        self.username_input.clear()
        self.password_input.clear()

    def check_credentials(self, username, password):
        """Проверяет, есть ли пользователь с таким логином и паролем в базе данных."""
        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()

        # Проверяем, есть ли пользователь с указанными данными
        cursor.execute("""
            SELECT password FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()
        conn.close()

        if result is None:
            return False
        stored_password = result[0]

        return stored_password == password
