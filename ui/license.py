from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout,
    QPushButton, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt

def show_agreement_dialog(localizator):
    class AgreementDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("MiniScanner | " + localizator.translate("disclaimer_title"))
            self.setMinimumSize(600, 500)

            layout = QVBoxLayout(self)

            agreement_text = localizator.translate("disclaimer")

            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(agreement_text)
            layout.addWidget(text_edit)

            button_layout = QHBoxLayout()
            self.btn_accept = QPushButton(localizator.translate("agree"))
            btn_decline = QPushButton(localizator.translate("disagree"))
            button_layout.addWidget(self.btn_accept)
            button_layout.addWidget(btn_decline)
            layout.addLayout(button_layout)

            btn_decline.clicked.connect(self.reject)
            self.btn_accept.clicked.connect(self.accept)

            scroll_bar = text_edit.verticalScrollBar()
            self.scroll_bar = scroll_bar

            if self.scroll_bar.maximum() == 0:
                self.btn_accept.setEnabled(True)
            else:
                self.btn_accept.setEnabled(False)
                scroll_bar.valueChanged.connect(self.on_scroll)

        def on_scroll(self, value):
            if value == self.scroll_bar.maximum():
                self.btn_accept.setEnabled(True)

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    dialog = AgreementDialog()
    result = dialog.exec()

    return result == QDialog.Accepted

