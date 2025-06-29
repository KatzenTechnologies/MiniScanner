from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QProgressBar,
    QWidget, QCheckBox
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
                plugin.scan()
            except Exception as e:
                self.logapi.logger.log(
                    "MiniScanner",
                    self.logapi.chosen_language.translate("threats_table_error_of_plugin",
                                                          plugin_name=plugin.name,
                                                          error=__import__("traceback").format_exc()),
                    self.logapi.LOGTYPE.ERROR
                )
            self.progress_update.emit(int((index + 1) / total * 100))


class VirusScanWindow(QDialog):
    add_threat_signal = Signal(str, str, object)

    def __init__(self, plugins: list, api):
        super().__init__()

        self.api = api
        self.plugins = plugins
        self.threat_rows = []  # [(filename, threat_name, plugin, delete_button)]

        self.setWindowTitle("MiniScanner | " + api.chosen_language.translate("threats_table_title"))
        self.resize(750, 480)

        layout = QVBoxLayout(self)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.auto_delete_checkbox = QCheckBox(self.api.chosen_language.translate("threats_table_auto_delete"))
        self.auto_delete_checkbox.stateChanged.connect(self._on_auto_delete_changed)
        layout.addWidget(self.auto_delete_checkbox)

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

    def _on_auto_delete_changed(self, state):
        if state == Qt.Checked:
            QMessageBox.warning(
                self,
                self.api.chosen_language.translate("threats_table_warning"),
                self.api.chosen_language.translate("threats_table_auto_delete_warning")
            )

    def add_threat(self, filename: str, threat_name: str, plugin):
        self.add_threat_signal.emit(filename, threat_name, plugin)

    def _add_threat_impl(self, filename: str, threat_name: str, plugin):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(filename))
        self.table.setItem(row, 1, QTableWidgetItem(threat_name))
        plugin_name = getattr(plugin, "name", self.api.chosen_language.translate("threats_table_unknown_plugin"))
        self.table.setItem(row, 2, QTableWidgetItem(plugin_name))

        delete_button = QPushButton(self.api.chosen_language.translate("threats_table_remove"))
        ignore_button = QPushButton(self.api.chosen_language.translate("threats_table_ignore"))

        delete_button.setMinimumHeight(22)
        ignore_button.setMinimumHeight(22)

        def delete_action():
            if not self.auto_delete_checkbox.isChecked():
                confirm = QMessageBox.question(
                    self,
                    self.api.chosen_language.translate("threats_table_confirmation"),
                    self.api.chosen_language.translate("threats_table_remove_file", filename=filename),
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm != QMessageBox.Yes:
                    return

            class DeleteThread(QThread):
                finished_signal = Signal(bool, str)

                def run(self_inner):
                    try:
                        plugin.delete(filename)
                        self_inner.finished_signal.emit(True, "")
                    except Exception as e:
                        self_inner.finished_signal.emit(False, str(e))

            delete_thread = DeleteThread()

            def on_finished(success, error):
                if success:
                    self.remove_row(delete_button)
                else:
                    self.api.logger.log("MiniScanner",
                                        self.api.chosen_language.translate("threats_table_error_of_remove", error=error),
                                        self.api.LOGTYPE.ERROR)
                    QMessageBox.critical(
                        self,
                        self.api.chosen_language.translate("threats_table_error"),
                        self.api.chosen_language.translate("threats_table_error_of_remove", error=error)
                    )
                delete_thread.deleteLater()

            delete_thread.finished_signal.connect(on_finished)
            delete_thread.start()

        def ignore_action():
            self.remove_row(delete_button)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(delete_button)
        btn_layout.addWidget(ignore_button)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        self.table.setCellWidget(row, 3, btn_widget)

        delete_button.clicked.connect(delete_action)
        ignore_button.clicked.connect(ignore_action)

        self.threat_rows.append((filename, threat_name, plugin, delete_button))

    def remove_row(self, delete_button: QPushButton):
        for i, (_, _, _, btn) in enumerate(self.threat_rows):
            if btn == delete_button:
                self.table.removeRow(i)
                self.threat_rows.pop(i)
                break
