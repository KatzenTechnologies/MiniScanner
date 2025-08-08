from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QProgressBar,
    QWidget, QCheckBox, QLabel
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
            except Exception:
                self.logapi.logger.log(
                    "MiniScanner",
                    self.logapi.chosen_language.translate(
                        "threats_table_error_of_plugin",
                        plugin_name=plugin.name,
                        error=__import__("traceback").format_exc()
                    ),
                    self.logapi.LOGTYPE.ERROR
                )
            self.progress_update.emit(int((index + 1) / total * 100))


class VirusScanWindow(QDialog):
    add_threat_signal = Signal(str, str, object, object, bool)

    def __init__(self, plugins: list, api):
        super().__init__()
        self.api = api
        self.plugins = plugins
        self.threat_rows = []
        self.delete_threads = []

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

        api.add_threat = self.add_threat
        api.prerun()

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

    def add_threat(self, filename: str, threat_name: str, plugin, extra_buttons=None, enable_quarantine_button: bool = False):
        if extra_buttons is None:
            extra_buttons = []
        self.add_threat_signal.emit(filename, threat_name, plugin, extra_buttons, enable_quarantine_button)

    def _add_threat_impl(self, filename: str, threat_name: str, plugin, extra_buttons: list, enable_quarantine_button: bool):
        row = self.table.rowCount()
        self.table.insertRow(row)

        label = QLabel(filename)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label.setMargin(3)
        label.setToolTip(filename)
        self.table.setCellWidget(row, 0, label)
        self.table.resizeRowToContents(row)

        self.table.setItem(row, 1, QTableWidgetItem(threat_name))
        plugin_name = getattr(plugin, "name", self.api.chosen_language.translate("threats_table_unknown_plugin"))
        self.table.setItem(row, 2, QTableWidgetItem(plugin_name))

        delete_button = QPushButton(self.api.chosen_language.translate("threats_table_remove"))
        ignore_button = QPushButton(self.api.chosen_language.translate("threats_table_ignore"))

        delete_button.setMinimumHeight(22)
        ignore_button.setMinimumHeight(22)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(delete_button)
        btn_layout.addWidget(ignore_button)

        quarantine_button = None
        if enable_quarantine_button:
            quarantine_button = QPushButton(self.api.chosen_language.translate("threats_table_quarantine"))
            quarantine_button.setMinimumHeight(22)
            btn_layout.addWidget(quarantine_button)

        custom_buttons = []
        for label_btn, func, remove_row_after in extra_buttons:
            custom_btn = QPushButton(label_btn)
            custom_btn.setMinimumHeight(22)
            btn_layout.addWidget(custom_btn)
            custom_buttons.append((custom_btn, func, remove_row_after))

        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        self.table.setCellWidget(row, 3, btn_widget)

        self.threat_rows.append((filename, threat_name, plugin, delete_button, btn_widget))

        def disable_all_buttons():
            delete_button.setEnabled(False)
            ignore_button.setEnabled(False)
            if quarantine_button:
                quarantine_button.setEnabled(False)
            for btn, _, _ in custom_buttons:
                btn.setEnabled(False)

        def enable_all_buttons():
            delete_button.setEnabled(True)
            ignore_button.setEnabled(True)
            if quarantine_button:
                quarantine_button.setEnabled(True)
            for btn, _, _ in custom_buttons:
                btn.setEnabled(True)

        def remove_row():
            for row_idx in range(self.table.rowCount()):
                if self.table.cellWidget(row_idx, 3) is btn_widget:
                    self.table.removeRow(row_idx)
                    self.threat_rows = [
                        r for r in self.threat_rows if r[4] is not btn_widget
                    ]
                    break

        def run_in_thread(func, callback):
            class ActionThread(QThread):
                finished_signal = Signal(bool, str)
                def run(self_inner):
                    try:
                        func()
                        self_inner.finished_signal.emit(True, "")
                    except Exception as e:
                        import traceback
                        tb = traceback.format_exc()
                        self_inner.finished_signal.emit(False, f"{e}\n{tb}")

            action_thread = ActionThread()
            self.delete_threads.append(action_thread)

            def on_finished(success, error):
                callback(success, error)
                action_thread.quit()
                action_thread.wait()
                action_thread.deleteLater()
                if action_thread in self.delete_threads:
                    self.delete_threads.remove(action_thread)

            action_thread.finished_signal.connect(on_finished)
            action_thread.start()

        def delete_action():
            disable_all_buttons()

            if not self.auto_delete_checkbox.isChecked():
                confirm = QMessageBox.question(
                    self,
                    self.api.chosen_language.translate("threats_table_confirmation"),
                    self.api.chosen_language.translate("threats_table_remove_file", filename=filename),
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm != QMessageBox.Yes:
                    enable_all_buttons()
                    return

            def do_delete():
                plugin.delete(filename)

            def on_delete_finished(success, error):
                if success:
                    remove_row()
                else:
                    self.api.logger.log(
                        "MiniScanner",
                        self.api.chosen_language.translate("threats_table_error_of_remove", error=error),
                        self.api.LOGTYPE.ERROR
                    )
                    QMessageBox.critical(
                        self,
                        self.api.chosen_language.translate("threats_table_error"),
                        self.api.chosen_language.translate("threats_table_error_of_remove", error=error)
                    )
                    enable_all_buttons()

            run_in_thread(do_delete, on_delete_finished)

        def ignore_action():
            disable_all_buttons()
            remove_row()

        def quarantine_action():
            disable_all_buttons()

            def do_quarantine():
                plugin.quarantine(filename)

            def on_quarantine_finished(success, error):
                if success:
                    remove_row()
                else:
                    self.api.logger.log(
                        "MiniScanner",
                        self.api.chosen_language.translate("threats_table_error_of_quarantine", error=error),
                        self.api.LOGTYPE.ERROR
                    )
                    QMessageBox.critical(
                        self,
                        self.api.chosen_language.translate("threats_table_error"),
                        self.api.chosen_language.translate("threats_table_error_of_quarantine", error=error)
                    )
                    enable_all_buttons()

            run_in_thread(do_quarantine, on_quarantine_finished)

        delete_button.clicked.connect(delete_action)
        ignore_button.clicked.connect(ignore_action)
        if quarantine_button:
            quarantine_button.clicked.connect(quarantine_action)

        for btn, func, remove_row_after in custom_buttons:
            def make_custom_action(b=btn, f=func, r=remove_row_after):
                def handler():
                    disable_all_buttons()
                    def do_custom():
                        f(filename)
                    def on_custom_finished(success, error):
                        if success:
                            if r:
                                remove_row()
                        else:
                            self.api.logger.log(
                                "MiniScanner",
                                self.api.chosen_language.translate("custom_action_failed", error=error),
                                self.api.LOGTYPE.ERROR
                            )
                            QMessageBox.critical(
                                self,
                                self.api.chosen_language.translate("threats_table_error"),
                                self.api.chosen_language.translate("custom_action_failed", error=error)
                            )
                            enable_all_buttons()
                    run_in_thread(do_custom, on_custom_finished)
                return handler
            btn.clicked.connect(make_custom_action())

    def closeEvent(self, event):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        for thread in self.delete_threads[:]:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        super().closeEvent(event)
