from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout,
    QPushButton, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt

def show_agreement_dialog():
    class AgreementDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Соглашение об отказе от ответственности")
            self.setMinimumSize(600, 500)

            layout = QVBoxLayout(self)

            agreement_text = (
                "Пожалуйста, внимательно ознакомьтесь с условиями использования.\n\n"
                "Данное программное обеспечение и все его компоненты (включая плагины и инструменты разработки) предоставляются «как есть» без гарантий.\n\n"
                "Автор программы прилагает максимум усилий для обеспечения безопасности и корректной работы основного кода.\n"
                "Однако ответственность за работу и безопасность любых плагинов, в том числе написанных сторонними авторами, "
                "а также за последствия использования таких плагинов, полностью лежит на их создателях и пользователях.\n\n"
                "Вы используете плагины и связанные с ними инструменты на свой страх и риск. Любые сбои, повреждения системы, потеря данных "
                "или другие негативные последствия, вызванные плагинами, не могут быть предъявлены к ответственности автору основной программы.\n\n"
                "Кроме того, автор не несёт ответственности за любые виды ущерба, включая, но не ограничиваясь:\n"
                "- ущербом, причинённым вашей системе или данным;\n"
                "- несоответствием работы программы вашим ожиданиям;\n"
                "- неправильной работой любых компонентов программы, плагинов и инструментов;\n"
                "- потерей данных, сбоем оборудования и иными последствиями использования.\n\n"
                "Перед использованием настоятельно рекомендуется создавать резервные копии важных данных.\n\n"
                "Продолжая использовать это программное обеспечение, вы принимаете все риски и полностью освобождаете автора "
                "от ответственности за любые последствия.\n\n"
                "Спасибо за понимание и аккуратное использование!"
            )

            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(agreement_text)
            layout.addWidget(text_edit)

            button_layout = QHBoxLayout()
            self.btn_accept = QPushButton("Согласен")
            btn_decline = QPushButton("Отказаться")
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


if __name__ == "__main__":
    # Тесты
    accepted = show_agreement_dialog()
    if accepted:
        print("Пользователь согласился с условиями.")
    else:
        print("Пользователь отказался или закрыл окно.")
