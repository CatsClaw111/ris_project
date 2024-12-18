from PyQt6.QtWidgets import (QVBoxLayout, QPushButton,
                             QLabel, QDialog, QSpinBox, QLineEdit,
                             )

import sqlite3


class EditTaskDialog(QDialog):
    def __init__(self, task_id, user_id, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.user_id = user_id
        self.setWindowTitle("Редактирование задачи")
        self.setFixedSize(300, 200)

        # Получаем данные задачи
        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, description, priority FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        conn.close()

        # Поля для редактирования
        self.layout = QVBoxLayout(self)
        self.title_input = QLineEdit(task[0], self)
        self.description_input = QLineEdit(task[1], self)
        self.priority_input = QSpinBox(self)
        self.priority_input.setRange(1, 10)
        self.priority_input.setValue(task[2])

        # Кнопка "Сохранить"
        save_button = QPushButton("Сохранить", self)
        save_button.clicked.connect(self.save_task)

        # Компоновка
        self.layout.addWidget(QLabel("Название задачи:", self))
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(QLabel("Описание задачи:", self))
        self.layout.addWidget(self.description_input)
        self.layout.addWidget(QLabel("Приоритет задачи:", self))
        self.layout.addWidget(self.priority_input)
        self.layout.addWidget(save_button)

    def save_task(self):
        """Сохраняет изменения задачи."""
        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET title = ?, description = ?, priority = ?
            WHERE id = ?
        """, (self.title_input.text(), self.description_input.text(),
              self.priority_input.value(), self.task_id))
        conn.commit()
        conn.close()
        self.accept()
