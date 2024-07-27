from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QHBoxLayout, QSizePolicy, QSpacerItem, QVBoxLayout
from qfluentwidgets.components import PrimaryPushButton, PushButton, StrongBodyLabel, TextEdit, TitleLabel
from qframelesswindow import FramelessDialog


class MessageDialog(FramelessDialog):
    ok_signal = Signal()
    cancel_signal = Signal()

    def __init__(self):
        super().__init__()
        self.ok_btn = PrimaryPushButton()
        self.ok_btn.setText("确认")
        self.cancel_btn = PushButton()
        self.cancel_btn.setText("取消")

        self.title_label = TitleLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setText("标题")

        self.explain_label = StrongBodyLabel()
        self.explain_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.explain_label.setText("说明")

        self.body_text_edit = TextEdit()
        self.body_text_edit.setReadOnly(True)

        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.v_spacer = QSpacerItem(0, 21, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.button_layout.addWidget(self.ok_btn)
        self.button_layout.addWidget(self.cancel_btn)
        self.main_layout.addItem(self.v_spacer)
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.explain_label)
        self.main_layout.addWidget(self.body_text_edit)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

        self.ok_btn.clicked.connect(self.ok_signal.emit)
        self.cancel_btn.clicked.connect(self.cancel_signal.emit)

        self.setStyleSheet("background-color: #f9f9f9")

    def set_title(self, title: str):
        self.title_label.setText(title)

    def set_explain(self, explain: str):
        self.explain_label.setText(explain)

    def set_body(self, body: str):
        self.body_text_edit.setMarkdown(body)


if __name__ == '__main__':
    app = QApplication([])
    dialog = MessageDialog()
    dialog.show()
    app.exec()
