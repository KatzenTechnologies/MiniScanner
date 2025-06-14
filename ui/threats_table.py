from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QProgressBar, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QObject


class VirusScanWorker(QThread):
    progress_update = Signal(int)

    def __init__(self, plugins, api, logapi):
        super().__init__()
        self.plugins = plugins
        self.api = api
        self.logapi = logapi

    def run(self):
        total = len(self.plugins)
        for index, plugin in enumerate(self.plugins):
            plugin.api = self.api
            try:
                plugin.scan()
            except Exception as e:
                self.logapi.logger.log("MiniScanner", f"Ошибка плагина {plugin.__class__.__name__}: {e}", self.logapi.LOGTYPE.ERROR)
            self.progress_update.emit(int((index + 1) / total * 100))


class VirusScanWindow(QDialog):
    add_threat_signal = Signal(str, str, object)

    def __init__(self, plugins: list, api):
        super().__init__()

        self.api = api

        self.setWindowTitle("MiniScanner | Проверка на вирусы")
        self.resize(640, 420)

        self.plugins = plugins
        self.threat_plugin_map = []

        layout = QVBoxLayout(self)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Файл", "Угроза", "Действие"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.add_threat_signal.connect(self._add_threat_impl)

        self.worker = VirusScanWorker(self.plugins, self, self.api)
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.start()

    def add_threat(self, filename: str, threat_name: str, plugin):
        self.add_threat_signal.emit(filename, threat_name, plugin)

    def _add_threat_impl(self, filename: str, threat_name: str, plugin):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(filename))
        self.table.setItem(row, 1, QTableWidgetItem(threat_name))
        self.threat_plugin_map.append((filename, threat_name, plugin))

        delete_button = QPushButton("Удалить")
        ignore_button = QPushButton("Игнорировать")

        button_height = 18
        delete_button.setMinimumHeight(button_height)
        ignore_button.setMinimumHeight(button_height)

        def delete_action():
            confirm = QMessageBox.question(
                self,
                "Подтверждение",
                f"Удалить файл {filename}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    plugin.delete(filename)
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
                    return
                self.remove_row(row)

        def ignore_action():
            self.remove_row(row)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(delete_button)
        btn_layout.addWidget(ignore_button)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        self.table.setCellWidget(row, 2, btn_widget)

        delete_button.clicked.connect(delete_action)
        ignore_button.clicked.connect(ignore_action)

    def remove_row(self, row):
        self.table.removeRow(row)
        if 0 <= row < len(self.threat_plugin_map):
            self.threat_plugin_map.pop(row)
