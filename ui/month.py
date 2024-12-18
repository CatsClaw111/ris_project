from PyQt6.QtWidgets import (QVBoxLayout, QPushButton,
                             QComboBox, QDialog, QSpinBox, QHBoxLayout
                             )
from PyQt6.QtCore import QDate

from PyQt6.QtCore import QLocale, QTranslator, QLibraryInfo

QLocale.setDefault(QLocale(QLocale.Language.Russian, QLocale.Country.Russia))


class MonthYearPicker(QDialog):
    def __init__(self, current_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор месяца и года")
        self.setFixedSize(300, 200)

        self.layout = QVBoxLayout(self)

        # Выбор месяца
        self.month_selector = QComboBox(self)
        self.month_selector.addItems([QLocale().monthName(i) for i in range(1, 13)])
        self.layout.addWidget(self.month_selector)

        # Выбор года
        self.year_selector = QSpinBox(self)
        self.year_selector.setRange(1900, 2100)
        self.year_selector.setValue(current_date.year())
        self.layout.addWidget(self.year_selector)

        # Кнопки подтверждения
        self.button_box = QHBoxLayout()
        self.ok_button = QPushButton("ОК", self)
        self.ok_button.clicked.connect(self.accept)
        self.button_box.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.clicked.connect(self.reject)
        self.button_box.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_box)

    def get_selected_date(self):
        return self.year_selector.value(), self.month_selector.currentIndex() + 1

