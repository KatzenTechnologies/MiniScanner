from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar,
    QPushButton, QDialogButtonBox
)
from PySide6.QtCore import QThread, Signal
import time

class LoaderThread(QThread):
    progress = Signal(int)
    log = Signal(str)
    done = Signal()

    def __init__(self, modules, api):
        super().__init__()
        self.modules = modules
        self.api = api
        self.loaded_instances = []

    def run(self):
        total = len(self.modules)
        for i, module in enumerate(self.modules, 1):
            try:
                self.log.emit(self.api.chosen_language.translate("load_loading_plugin", plugin_name=module.__name__))
                instance = module.Main(self.api)
                self.api.loaded.append(instance.name)
                self.loaded_instances.append(instance)
                time.sleep(0.3)
            except Exception as e:
                self.log.emit(self.api.chosen_language.translate("load_loading_error", error=e))
            self.progress.emit(int(i / total * 100))
        self.done.emit()

class PluginLoaderDialog(QDialog):
    def __init__(self, modules, api):
        super().__init__()

        self.api = api

        self.setWindowTitle("MiniScanner | " + self.api.chosen_language.translate("load_title"))
        self.resize(400, 150)
        self.result_plugins = []

        self.label = QLabel(self.api.chosen_language.translate("load_ready"))
        self.progress = QProgressBar()
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.thread = LoaderThread(modules, api)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.log.connect(self.label.setText)
        self.thread.done.connect(self.loading_done)
        self.thread.start()

    def loading_done(self):
        self.label.setText(self.api.chosen_language.translate("load_loaded"))
        self.result_plugins = self.thread.loaded_instances
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(True)

    def get_result(self):
        return self.result_plugins