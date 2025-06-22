from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QProgressBar, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal


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
            try:
                plugin.api = self.api
                plugin.scan()
            except Exception as e:
                import traceback
                self.logapi.logger.log(
                    "MiniScanner",
                    self.logapi.chosen_language.translate(
                        "threats_table_error_of_plugin",
                        plugin_name=getattr(plugin, "name", "Unknown"),
                        error=traceback.format_exc()
                    ),
                    self.logapi.LOGTYPE.ERROR
                )
            self.progress_update.emit(int((index + 1) / total * 100))


class VirusScanWindow(QDialog):
    add_threat_signal = Signal(str, str, object)

    def __init__(self, plugins: list, api):
        super().__init__()
        self.api = api
        self.setWindowTitle("MiniScanner | " + api.chosen_language.translate("threats_table_title"))
        self.resize(700, 420)

        self.plugins = plugins
        self.threat_plugin_map = []

        layout = QVBoxLayout(self)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            api.chosen_language.translate("threats_table_file"),
            api.chosen_language.translate("threats_table_threat"),
            api.chosen_language.translate("threats_table_plugin"),
            api.chosen_language.translate("threats_table_action")
        ])
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

        plugin_name = getattr(plugin, "name", self.api.chosen_language.translate("threats_table_unknown_plugin"))
        self.table.setItem(row, 2, QTableWidgetItem(plugin_name))

        self.threat_plugin_map.append((filename, threat_name, plugin))

        delete_button = QPushButton(self.api.chosen_language.translate("threats_table_remove"))
        ignore_button = QPushButton(self.api.chosen_language.translate("threats_table_ignore"))

        delete_button.setMinimumHeight(28)
        ignore_button.setMinimumHeight(28)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addWidget(delete_button)
        btn_layout.addWidget(ignore_button)

        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)

        self.table.setCellWidget(row, 3, btn_widget)

        delete_button.clicked.connect(lambda _, r=row: self._delete_row(r))
        ignore_button.clicked.connect(lambda _, r=row: self._ignore_row(r))

    def _delete_row(self, row: int):
        if not (0 <= row < len(self.threat_plugin_map)):
            return

        filename, _, plugin = self.threat_plugin_map[row]
        confirm = QMessageBox.question(
            self,
            self.api.chosen_language.translate("threats_table_confirmation"),
            self.api.chosen_language.translate("threats_table_remove_file", filename=filename),
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            plugin.delete(filename)
        except Exception as e:
            self.api.logger.log(
                "MiniScanner",
                self.api.chosen_language.translate("threats_table_error_of_remove", error=str(e)),
                self.api.LOGTYPE.ERROR
            )
            QMessageBox.critical(
                self,
                self.api.chosen_language.translate("threats_table_error"),
                self.api.chosen_language.translate("threats_table_error_of_remove", error=str(e))
            )
            return

        self.remove_row(row)

    def _ignore_row(self, row: int):
        self.remove_row(row)

    def remove_row(self, row: int):
        if 0 <= row < self.table.rowCount():
            self.table.removeRow(row)
        if 0 <= row < len(self.threat_plugin_map):
            self.threat_plugin_map.pop(row)

        for r in range(self.table.rowCount()):
            widget = self.table.cellWidget(r, 3)
            if widget:
                buttons = widget.findChildren(QPushButton)
                if len(buttons) == 2:
                    delete_button, ignore_button = buttons
                    delete_button.clicked.disconnect()
                    ignore_button.clicked.disconnect()
                    delete_button.clicked.connect(lambda _, row=r: self._delete_row(row))
                    ignore_button.clicked.connect(lambda _, row=r: self._ignore_row(row))
