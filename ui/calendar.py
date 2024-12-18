from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QPushButton,
                             QComboBox, QLabel, QDialog, QSpinBox, QLineEdit,
                             QHBoxLayout, QMessageBox, QListWidgetItem, QListWidget,
                             QSizePolicy,
                             )
from PyQt6.QtCore import QDate, Qt, QLocale
from PyQt6.QtGui import QColor, QBrush
from datetime import datetime


import sqlite3

from ui.add_task import AddTaskPlanDialog
from ui.month import MonthYearPicker
from ui.edit_task import EditTaskDialog


class CalendarWindow(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("РИС")
        self.setFixedSize(800, 600)
        QLocale.setDefault(QLocale(QLocale.Language.Russian, QLocale.Country.Russia))

        
        # Устанавливаем текущую дату
        self.current_date = QDate.currentDate()

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        self.calendar_layout = QVBoxLayout()
        self.main_layout.addLayout(self.calendar_layout)

        self.top_panel = QHBoxLayout()
        self.calendar_layout.addLayout(self.top_panel)

        self.date_button = QPushButton(self.current_date.toString("LLLL yyyy"), self)  # "LLLL" для локализованных названий месяцев
        self.date_button.clicked.connect(self.show_month_year_picker)
        self.top_panel.addWidget(self.date_button)

        self.logout_button = QPushButton("Выйти", self)
        self.logout_button.clicked.connect(self.logout)
        self.top_panel.addWidget(self.logout_button)

        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("<", self)
        self.prev_button.clicked.connect(self.prev_month)
        self.nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton(">", self)
        self.next_button.clicked.connect(self.next_month)
        self.nav_layout.addWidget(self.next_button)
        self.calendar_layout.addLayout(self.nav_layout)

        self.calendar_grid = QGridLayout()
        self.calendar_layout.addLayout(self.calendar_grid)

        self.task_panel = QVBoxLayout()
        self.task_list = QListWidget(self)
        self.task_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.task_panel.addWidget(QLabel("Ближайшие задачи:", self))
        self.task_panel.addWidget(self.task_list)
        self.main_layout.addLayout(self.task_panel)
        self.task_list.itemDoubleClicked.connect(self.edit_task)

        self.update_calendar()
        self.update_task_list()


    def show_month_year_picker(self):
        # Создаем диалог выбора месяца и года
        picker = MonthYearPicker(self.current_date, self)
        if picker.exec():
            selected_year, selected_month = picker.get_selected_date()
            self.current_date.setDate(selected_year, selected_month, 1)
            self.update_calendar()

    def logout(self):
        # Закрывает сессию и удаляет ID из session.json
        session_file = "session.json"

        try:
            with open(session_file, "w") as f:
                f.write("{}")
            print("Сессия завершена. ID пользователя удалён.")
        except FileNotFoundError:
            print("Файл session.json не найден. Нечего удалять.")

        self.close()

    

    def update_calendar(self):
        # Очистить старую сетку
        for i in reversed(range(self.calendar_grid.count())):
            widget = self.calendar_grid.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Первый день месяца
        first_day_of_month = QDate(self.current_date.year(), self.current_date.month(), 1)
        first_day_weekday = first_day_of_month.dayOfWeek()  # Номер дня недели (1 - понедельник, 7 - воскресенье)
        days_in_month = self.current_date.daysInMonth()  # Количество дней в месяце
        
        # Создание заголовков для дней недели
        weekday_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for col, name in enumerate(weekday_names):
            label = QLabel(name, self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(40, 40)  # Фиксированный размер заголовков
            self.calendar_grid.addWidget(label, 0, col)

        # Добавляем пустые кнопки перед первым днём месяца
        day_counter = 1
        row = 1
        for col in range(7):
            if col < first_day_weekday - 1:
                placeholder = QLabel("", self)  # Пустая ячейка
                placeholder.setFixedSize(40, 40)
                self.calendar_grid.addWidget(placeholder, row, col)
            else:
                break

        # Добавление дней месяца
        for col in range(first_day_weekday - 1, 7):
            day_button = self.create_day_button(day_counter)
            self.calendar_grid.addWidget(day_button, row, col)
            day_counter += 1

        # Заполнение остальных недель
        row += 1
        while day_counter <= days_in_month:
            for col in range(7):
                if day_counter > days_in_month:
                    # Пустые кнопки после последнего дня месяца
                    placeholder = QLabel("", self)
                    placeholder.setFixedSize(40, 40)
                    self.calendar_grid.addWidget(placeholder, row, col)
                else:
                    day_button = self.create_day_button(day_counter)
                    self.calendar_grid.addWidget(day_button, row, col)
                day_counter += 1
            row += 1

        while row <= 6:
            for col in range(7):
                placeholder = QLabel("", self)
                placeholder.setFixedSize(40, 40)
                self.calendar_grid.addWidget(placeholder, row, col)
            row += 1

        # Устанавливаем текст кнопки с месяцем на русском языке
        from PyQt6.QtCore import QLocale

        locale = QLocale(QLocale.Language.Russian)  # Установка локали на русский
        month_name = locale.monthName(self.current_date.month(), QLocale.FormatType.LongFormat)
        self.date_button.setText(f"{month_name.capitalize()} {self.current_date.year()}")



    def create_day_button(self, day):
        """Создает кнопку для конкретного дня с проверкой задач и планов текущего пользователя."""
        day_button = QPushButton(str(day), self)
        day_button.setFixedSize(40, 40)

        # Установка обработчика нажатия на день
        day_button.clicked.connect(lambda: self.on_day_click(day))

        # Генерация строки даты для проверки задач
        selected_date = QDate(self.current_date.year(), self.current_date.month(), day)
        date_str = selected_date.toString("yyyy-MM-dd")

        # Подключение к базе данных 
        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()

        # Проверка невыполненных задач для текущего пользователя на выбранную дату
        cursor.execute(
            """
            SELECT COUNT(*) FROM tasks
            WHERE date = ? AND status = 0 AND user_id = ?
            """,
            (date_str, self.user_id)
        )
        has_tasks = cursor.fetchone()[0] > 0

        # Проверяем планы для текущего пользователя на выбранную дату
        cursor.execute(
            """
            SELECT COUNT(*) FROM plans
            WHERE start_time <= ? AND end_time >= ? AND user_id = ?
            """,
            (date_str, date_str, self.user_id)
        )
        has_plans = cursor.fetchone()[0] > 0

        conn.close()

        # Устанавливаем подсветку кнопки в зависимости от состояния
        if has_tasks and has_plans:
            day_button.setStyleSheet("background-color: purple;")
        elif has_tasks:
            day_button.setStyleSheet("background-color: lightblue;")
        elif has_plans:
            day_button.setStyleSheet("background-color: lightgreen;")

        return day_button

    def has_tasks(self, date_str):
        # Проверка наличия невыполненных задач на заданную дату, включая прошедшие
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE date = ? AND status = 0
        """, (date_str,))
        task_count = cursor.fetchone()[0]
        conn.close()
        return task_count > 0

    def has_plans(self, date_str):
        # Проверка наличия планов на заданную дату
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM plans 
            WHERE start_time <= ? AND end_time >= ?
        """, (date_str, date_str))
        plan_count = cursor.fetchone()[0]
        conn.close()
        return plan_count > 0

    def on_day_click(self, day):
        """Обрабатывает клик на день и открывает окно для добавления задачи или плана."""
        dialog = AddTaskPlanDialog(day, self.current_date, self.user_id, self)
        dialog.exec()
        self.update_task_list()
        self.update_calendar()
    
    def prev_month(self):
        # Переход на предыдущий месяц
        self.current_date = self.current_date.addMonths(-1)
        self.update_calendar()

    def next_month(self):
        # Переход на следующий месяц
        self.current_date = self.current_date.addMonths(1)
        self.update_calendar()

    def complete_task(self, task_id):
        # Пометка задачи, как выполненной
        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        self.update_task_list()
        self.update_calendar()

    def edit_task(self, item):
        # Открытие окна редактирования задачи
        task_id = item.data(Qt.ItemDataRole.UserRole)
        dialog = EditTaskDialog(task_id, self.user_id, self)
        dialog.exec()
        self.update_task_list()
        self.update_calendar()

    def update_task_list(self):
        # Обновление списка ближайших задач с кнопками 'Выполнить', возможностью редактирования и всплывающими подсказками.

        self.task_list.clear()

        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()

        # Запрос ближайших задач
        query = """
        SELECT id, title, description, date, priority FROM tasks
        WHERE user_id = ? AND status = 0
        ORDER BY date ASC
        LIMIT 10
        """
        today = QDate.currentDate().toString("yyyy-MM-dd")
        cursor.execute(query, (self.user_id,))
        tasks = cursor.fetchall()
        conn.close()

        for task_id, title, description, date, priority in tasks:
            # Преобразование даты в европейский формат
            european_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")

            # Создаём виджет для задачи
            task_widget = QWidget(self)
            task_layout = QHBoxLayout(task_widget)

            # Текст задачи
            task_label = QLabel(f"[{european_date}] {title} (Приоритет: {priority})", self)
            if priority >= 8:
                task_label.setStyleSheet("color: red; font-weight: bold;")
            task_layout.addWidget(task_label)

            # Устанавливаем подсказку с подробной информацией
            tooltip_text = f"""
            Название: {title}
            Описание: {description}
            Дата: {european_date}
            Приоритет: {priority}
            """
            task_label.setToolTip(tooltip_text.strip())  

            complete_button = QPushButton("Выполнить", self)
            complete_button.setFixedSize(80, 30)
            complete_button.clicked.connect(lambda _, t_id=task_id: self.complete_task(t_id))
            task_layout.addWidget(complete_button)

            task_widget.setLayout(task_layout)
            item = QListWidgetItem(self.task_list)
            item.setSizeHint(task_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, task_id)
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, task_widget)