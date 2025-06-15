from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QEventLoop
import sys

class LanguageSelector(QWidget):
    def __init__(self, languages: list[list[str]], default_key: str = ""):
        super().__init__()
        self.setWindowTitle("MiniScanner | Select Language")
        self.setFixedWidth(300)

        self._lang_map = {}
        self.selected_key = None
        self.skip_next_time = False

        layout = QVBoxLayout(self)

        label = QLabel("Please select a language:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.combo = QComboBox()
        layout.addWidget(self.combo)

        default_display = None
        for key, name in languages:
            self._lang_map[name] = key
            self.combo.addItem(name)
            if key == default_key:
                default_display = name

        if default_display:
            index = self.combo.findText(default_display)
            if index >= 0:
                self.combo.setCurrentIndex(index)

        self.checkbox = QCheckBox("Don't ask again")
        layout.addWidget(self.checkbox)

        button = QPushButton("Select")
        button.clicked.connect(self._on_select)
        layout.addWidget(button)

    def _on_select(self):
        name = self.combo.currentText()
        self.selected_key = self._lang_map.get(name)
        self.skip_next_time = self.checkbox.isChecked()
        self.hide()

def select_language(
    language_list: list[list[str]],
    default_key: str = "",
    skip_if_possible: bool = False
) -> tuple[str, bool]:
    if skip_if_possible and default_key:
        return default_key, True

    app = QApplication.instance()
    owns_app = app is None
    if owns_app:
        app = QApplication(sys.argv)

    selector = LanguageSelector(language_list, default_key)
    selector.show()

    loop = QEventLoop()
    selector.destroyed.connect(loop.quit)
    selector.hideEvent = lambda e: loop.quit()
    loop.exec()

    return selector.selected_key, selector.skip_next_time
