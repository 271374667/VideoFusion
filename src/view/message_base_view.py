"""
这个模块负责让其他的View继承，实现一些一些常用的信息提示的功能
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QWidget
from qfluentwidgets import MessageBox
from qfluentwidgets.components import (
    InfoBar,
    InfoBarIcon,
    InfoBarPosition,
    PushButton,
    StateToolTip,
)


class MessageBaseView(QWidget):
    """这个类负责让其他的View继承，实现一些一些常用的信息提示的功能"""

    info_button_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setParent(parent)
        self.is_state_tooltip_running = False

    def show_mask_dialog(self, title: str = "Title", content: str = "Content") -> bool:
        """显示一个遮罩式的对话框

        Args:
            title (str): 标题
            content (str): 内容

        Returns:
            bool: 是否点击了确定按钮
        """
        w = MessageBox(title, content, self)
        return bool(w.exec())

    def show_info_infobar(
        self,
        title: str = "Title",
        content: str = "Content",
        duration: int = 5000,
        position: InfoBarPosition = InfoBarPosition.TOP_RIGHT,
        is_closable: bool = True,
        button_text: Optional[str] = None,
    ) -> None:
        """显示一个信息提示框

        Args:
            title (str, optional): 标题. Defaults to 'Title'.
            content (str, optional): 内容. Defaults to 'Content'.
            duration (int, optional): 持续时间. Defaults to 5000.
            position (InfoBarPosition, optional): 位置. Defaults to InfoBarPosition.TOP_RIGHT.
            is_closable (bool, optional): 是否可以被关闭. Defaults to True.
            button_text: (str, optional): 按钮的文本. Defaults to None.
        """
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,  # vertical layout
            isClosable=is_closable,
            position=position,
            duration=duration,
            parent=self,
        )
        if button_text:
            inner_button = PushButton(button_text)
            w.addWidget(inner_button)
            inner_button.clicked.connect(self.info_button_clicked)

        w.show()

    def show_success_infobar(
        self,
        title: str = "Title",
        content: str = "Content",
        duration: int = 4000,
        position: InfoBarPosition = InfoBarPosition.TOP_RIGHT,
        is_closable: bool = True,
    ) -> None:
        """显示一个成功信息提示框

        Args:
            title (str, optional): 标题. Defaults to 'Title'.
            content (str, optional): 内容. Defaults to 'Content'.
            duration (int, optional): 持续时间. Defaults to 2000.
            position (InfoBarPosition, optional): 位置. Defaults to InfoBarPosition.TOP_RIGHT.
            is_closable (bool, optional): 是否可以被关闭. Defaults to True.
        """
        w = InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,  # vertical layout
            isClosable=is_closable,
            position=position,
            duration=duration,
            parent=self,
        )
        w.show()

    def show_warning_infobar(
        self,
        title: str = "Title",
        content: str = "Content",
        duration: int = 5000,
        position: InfoBarPosition = InfoBarPosition.TOP_RIGHT,
        is_closable: bool = False,
    ) -> None:
        """显示一个警告信息提示框

        Args:
            title (str, optional): 标题. Defaults to 'Title'.
            content (str, optional): 内容. Defaults to 'Content'.
            duration (int, optional): 持续时间. Defaults to 3000.
            position (InfoBarPosition, optional): 位置. Defaults to InfoBarPosition.TOP_RIGHT.
            is_closable (bool, optional): 是否可以被关闭. Defaults to False.
        """
        w = InfoBar.warning(
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,  # vertical layout
            isClosable=is_closable,
            position=position,
            duration=duration,
            parent=self,
        )
        w.show()

    def show_error_infobar(
        self,
        title: str = "Title",
        content: str = "Content",
        duration: int = -1,
        position: InfoBarPosition = InfoBarPosition.TOP_RIGHT,
        is_closable: bool = False,
    ) -> None:
        """显示一个错误信息提示框

        Args:
            title (str, optional): 标题. Defaults to 'Title'.
            content (str, optional): 内容. Defaults to 'Content'.
            duration (int, optional): 持续时间. Defaults to -1.
            position (InfoBarPosition, optional): 位置. Defaults to InfoBarPosition.TOP_RIGHT.
            is_closable (bool, optional): 是否可以被关闭. Defaults to False.
        """
        w = InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Orientation.Vertical,  # vertical layout
            isClosable=is_closable,
            position=position,
            duration=duration,
            parent=self,
        )
        w.show()

    def show_state_tooltip(
        self,
        title: str,
        content: str,
    ) -> None:
        """显示一个状态提示框

        Args:
            title (str, optional): 标题. Defaults to 'Title'.
            content (str, optional): 内容. Defaults to 'Content'.
        """
        # 防止多次点击
        if self.is_state_tooltip_running:
            return

        self.state_tooltip = StateToolTip(title, content, self)
        self.state_tooltip.setState(False)
        self.state_tooltip.move(self.state_tooltip.getSuitablePos())
        self.state_tooltip.show()
        self.is_state_tooltip_running = True

    def finish_state_tooltip(self, title: str = None, content: str = None) -> None:
        """结束状态提示框"""
        if not self.is_state_tooltip_running:
            return
        if title:
            self.state_tooltip.setTitle(title)
        if content:
            self.state_tooltip.setContent(content)

        self.state_tooltip.setState(True)
        self.is_state_tooltip_running = False

    def resizeEvent(self, event):
        # 每次窗口大小改变的时候，都要重新计算一下tooltip的位置
        if hasattr(self, "state_tooltip"):
            try:
                self.state_tooltip.move(self.state_tooltip.getSuitablePos())
            except RuntimeError:
                return


if __name__ == "__main__":
    app = QApplication([])
    w = MessageBaseView()
    w.show()
    app.exec()