import sqlite3
import sys

from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableView,
                             QVBoxLayout, QWidget, QHeaderView)


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Каталог кофе")
        self.setGeometry(100, 100, 800, 600)
        self.create_database()
        self.init_db()
        self.init_ui()

    def create_database(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS coffee (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, roast_level TEXT, ground_or_beans TEXT, taste_description TEXT, price REAL, package_volume REAL)')
        cursor.execute("SELECT COUNT(*) FROM coffee")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                               INSERT INTO coffee (name, roast_level, ground_or_beans, taste_description, price,
                                                   package_volume)
                               VALUES (?, ?, ?, ?, ?, ?)
                               ''', [
                                   ('Эфиопия Иргачефф', 'Средняя', 'Зерна', 'Цветочные ноты с цитрусовым послевкусием',
                                    1200, 250),
                                   ('Колумбия Супремо', 'Темная', 'Молотый', 'Шоколадные ноты с карамельным оттенком',
                                    950, 200),
                                   ('Бразилия Сантос', 'Светлая', 'Зерна', 'Ореховый вкус с мягкой кислинкой', 850, 300)
                               ])
        conn.commit()
        conn.close()

    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("coffee.sqlite")
        self.db.open()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        self.table = QTableView()
        self.model = QSqlTableModel()
        self.model.setTable("coffee")
        self.model.select()
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        central_widget.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
