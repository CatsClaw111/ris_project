from PyQt6.QtWidgets import (QVBoxLayout, QPushButton, QLabel,
                             QDialog, QSpinBox, QLineEdit,QMessageBox,
                             )
from PyQt6.QtCore import QDate
import sqlite3

class AddTaskPlanDialog(QDialog):
    def __init__(self, day, current_date, user_id, parent=None):
        super().__init__(parent)
        self.day = day
        self.current_date = current_date
        self.user_id = user_id

        self.setWindowTitle("Добавить задачу/план")
        self.setFixedSize(300, 400)

        self.layout = QVBoxLayout(self)
        self.title_input = QLineEdit(self)
        self.description_input = QLineEdit(self)
        self.priority_input = QSpinBox(self)
        self.priority_input.setRange(1, 10)

        save_button = QPushButton("Сохранить", self)
        save_button.clicked.connect(self.add_task)

        self.layout.addWidget(QLabel("Название задачи:", self))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(QLabel("Описание задачи:", self))
        self.layout.addWidget(self.description_input)
        self.layout.addWidget(QLabel("Приоритет:", self))
        self.layout.addWidget(self.priority_input)
        self.layout.addWidget(save_button)

    def add_task(self):
        """Сохраняет задачу в базу данных."""
        title = self.title_input.text().strip()
        description = self.description_input.text().strip()
        priority = self.priority_input.value()

        # Создание строки даты
        date = QDate(self.current_date.year(), self.current_date.month(), self.day).toString("yyyy-MM-dd")

        # Проверка на пустое название
        if not title:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return

        # Сохранение задачи в базу данных
        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO tasks (title, description, status, priority, date, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, 0, priority, date, self.user_id))
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить задачу: {e}")
        finally:
            conn.close()

        # Закрыть окно после сохранения
        self.accept()

        # Обновить задачи и календарь в родительском окне
        if hasattr(self.parent(), 'update_task_list') and hasattr(self.parent(), 'update_calendar'):
            self.parent().update_task_list()
            self.parent().update_calendar()

