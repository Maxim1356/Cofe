import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableView, QVBoxLayout,
                             QWidget, QHeaderView, QPushButton, QHBoxLayout,
                             QMessageBox)
from PyQT6 import QDialog
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi
import sqlite3


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

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS coffee
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           NOT
                           NULL,
                           roast_level
                           TEXT,
                           ground_or_beans
                           TEXT,
                           taste_description
                           TEXT,
                           price
                           REAL,
                           package_volume
                           REAL
                       )''')

        if not cursor.execute("SELECT COUNT(*) FROM coffee").fetchone()[0]:
            cursor.executemany('''
                               INSERT INTO coffee
                               VALUES (NULL, ?, ?, ?, ?, ?, ?)''', [
                                   ('Эфиопия Иргачефф', 'Средняя', 'Зерна', 'Цветочные ноты', 1200, 250),
                                   ('Колумбия Супремо', 'Темная', 'Молотый', 'Шоколадные ноты', 950, 200),
                                   ('Бразилия Сантос', 'Светлая', 'Зерна', 'Ореховый вкус', 850, 300)
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

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")

        self.add_btn.clicked.connect(self.add_coffee)
        self.edit_btn.clicked.connect(self.edit_coffee)
        self.delete_btn.clicked.connect(self.delete_coffee)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)

        # Таблица с данными
        self.table = QTableView()
        self.model = QSqlTableModel()
        self.model.setTable("coffee")
        self.model.select()
        self.table.setModel(self.model)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        central_widget.setLayout(layout)

    def add_coffee(self):
        form = CoffeeForm(self)
        if form.exec():
            self.model.select()

    def edit_coffee(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return

        form = CoffeeForm(self, selected[0].row())
        if form.exec():
            self.model.select()

    def delete_coffee(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return

        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Удалить выбранную запись?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.model.removeRow(selected[0].row())
            self.model.submitAll()
            self.model.select()


class CoffeeForm(QDialog):
    def __init__(self, parent=None, row_id=None):
        super().__init__(parent)
        loadUi('addEditCoffeeForm.ui', self)
        self.row_id = row_id
        self.parent = parent

        if row_id is not None:
            self.load_data()

    def load_data(self):
        record = self.parent.model.record(self.row_id)
        self.nameEdit.setText(record.value("name"))
        self.roastCombo.setCurrentText(record.value("roast_level"))
        self.typeCombo.setCurrentText(record.value("ground_or_beans"))
        self.tasteEdit.setText(record.value("taste_description"))
        self.priceSpin.setValue(record.value("price"))
        self.volumeSpin.setValue(record.value("package_volume"))

    def accept(self):
        if not self.nameEdit.text():
            QMessageBox.warning(self, "Ошибка", "Введите название кофе")
            return

        record = self.parent.model.record()
        if self.row_id is not None:
            record = self.parent.model.record(self.row_id)

        record.setValue("name", self.nameEdit.text())
        record.setValue("roast_level", self.roastCombo.currentText())
        record.setValue("ground_or_beans", self.typeCombo.currentText())
        record.setValue("taste_description", self.tasteEdit.text())
        record.setValue("price", self.priceSpin.value())
        record.setValue("package_volume", self.volumeSpin.value())

        if self.row_id is None:
            self.parent.model.insertRecord(-1, record)
        else:
            self.parent.model.setRecord(self.row_id, record)

        self.parent.model.submitAll()
        super().accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
