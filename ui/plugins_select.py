from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class PluginSelectorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MiniScanner | Выбор плагинов")
        self.setMinimumSize(400, 400)
        self.plugins = {}

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        warning_label = QLabel(
            "⚠️ ВНИМАНИЕ: Плагины могут содержать вредоносный код.\n"
            "Запускайте только те, которые получены из доверенных источников.\n"
            "Если плагин не помечен как подозрительный, это не означает, что он безопасен."
        )
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning_label)

        self.run_button = QPushButton("Запустить выбранные плагины")
        self.run_button.clicked.connect(self.on_run_clicked)
        layout.addWidget(self.run_button)

        self.selected_plugins = []

    def add_plugin(self, name: str, suspicious: bool = False):
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        if suspicious:
            item.setIcon(QIcon.fromTheme("dialog-warning"))
            item.setText(f"{name} [SUSPICIOUS]")
        self.list_widget.addItem(item)
        self.plugins[name] = {"item": item, "suspicious": suspicious}

    def on_run_clicked(self):
        self.selected_plugins = self.get_selected_plugins()
        if not self.selected_plugins:
            QMessageBox.information(self, "Нет выбора", "Выберите хотя бы один плагин.")
            return
        self.accept()

    def get_selected_plugins(self):
        selected = []
        for name, data in self.plugins.items():
            if data["item"].checkState() == Qt.Checked:
                selected.append(name)
        return selected

    def get_result(self):
        return self.selected_plugins
