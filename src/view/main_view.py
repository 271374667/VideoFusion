from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentWindow, NavigationItemPosition, TextEdit

from src.components.cmd_text_edit import CMDTextEdit
from src.core.about import about_txt
from src.view.concate_view import ConcateView
from src.view.settings_view import SettingView


class MainView(FluentWindow):
    def __init__(self, concate_view: ConcateView, setting_view: SettingView):
        super().__init__()

        # create sub interface
        self.concate_interface = concate_view
        self.cmd_interface = CMDTextEdit()
        self.about_interface = TextEdit()
        self.about_interface.setHtml(about_txt)
        self.about_interface.setObjectName("about")
        self.setting_interface = setting_view

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.concate_interface, FIF.HOME, '主页')
        self.addSubInterface(self.cmd_interface, FIF.COMMAND_PROMPT, '日志')

        self.addSubInterface(self.about_interface, FIF.CHAT, '关于', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.setting_interface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(1100, 750)
        # 设置窗口的最大尺寸
        self.setMaximumSize(1100, 750)
        # 设置窗口的最小尺寸
        self.setMinimumSize(1100, 750)
        self.setWindowIcon(QIcon(':/images/images/logo.ico'))
        self.setWindowTitle('VideoFusion')

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


if __name__ == '__main__':
    app = QApplication([])
    w = MainView(ConcateView(), SettingView())
    w.show()
    app.exec()
