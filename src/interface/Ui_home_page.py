# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_page.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QCommandLinkButton, QDoubleSpinBox,
    QFrame, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

from src.components.cmd_text_edit import CMDTextEdit
from src.components.file_drag_and_drop_lineedit import FileDragAndDropLineEdit

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(730, 800)
        Form.setToolTipDuration(-1)
        Form.setStyleSheet(u"QComboBox { color: rgb(0, 0, 0);\n"
"	alternate-background-color: rgb(255, 255, 255);\n"
"}\n"
"")
        self.verticalLayout_5 = QVBoxLayout(Form)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_2.addWidget(self.label_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit = FileDragAndDropLineEdit(self.groupBox)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setToolTipDuration(-1)
        self.lineEdit.setDragEnabled(True)

        self.horizontalLayout.addWidget(self.lineEdit)

        self.radioButton_2 = QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setChecked(True)

        self.horizontalLayout.addWidget(self.radioButton_2)

        self.radioButton = QRadioButton(self.groupBox)
        self.radioButton.setObjectName(u"radioButton")

        self.horizontalLayout.addWidget(self.radioButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.verticalLayout_2.addWidget(self.pushButton_2)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.frame.setEnabled(False)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.lineEdit_2 = QLineEdit(self.frame)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.verticalLayout.addWidget(self.lineEdit_2)


        self.verticalLayout_3.addWidget(self.frame)


        self.verticalLayout_5.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.scrollArea = QScrollArea(self.groupBox_2)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Sunken)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 692, 234))
        self.verticalLayout_10 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_5 = QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(u"label_5")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)

        self.verticalLayout_6.addWidget(self.label_5)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.lineEdit_3 = FileDragAndDropLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.horizontalLayout_5.addWidget(self.lineEdit_3)

        self.pushButton_3 = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_5.addWidget(self.pushButton_3)


        self.verticalLayout_6.addLayout(self.horizontalLayout_5)


        self.verticalLayout_10.addLayout(self.verticalLayout_6)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)

        self.horizontalLayout_6.addWidget(self.label_6)

        self.spinBox = QSpinBox(self.scrollAreaWidgetContents)
        self.spinBox.setObjectName(u"spinBox")
        sizePolicy1.setHeightForWidth(self.spinBox.sizePolicy().hasHeightForWidth())
        self.spinBox.setSizePolicy(sizePolicy1)
        self.spinBox.setMaximum(200)
        self.spinBox.setValue(25)

        self.horizontalLayout_6.addWidget(self.spinBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)


        self.horizontalLayout_8.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_7 = QLabel(self.scrollAreaWidgetContents)
        self.label_7.setObjectName(u"label_7")
        sizePolicy1.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy1)

        self.horizontalLayout_7.addWidget(self.label_7)

        self.doubleSpinBox = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        sizePolicy1.setHeightForWidth(self.doubleSpinBox.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox.setSizePolicy(sizePolicy1)
        self.doubleSpinBox.setMaximum(1.000000000000000)
        self.doubleSpinBox.setSingleStep(0.050000000000000)
        self.doubleSpinBox.setValue(0.500000000000000)

        self.horizontalLayout_7.addWidget(self.doubleSpinBox)


        self.horizontalLayout_8.addLayout(self.horizontalLayout_7)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)


        self.verticalLayout_10.addLayout(self.horizontalLayout_8)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_8 = QLabel(self.scrollAreaWidgetContents)
        self.label_8.setObjectName(u"label_8")
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)

        self.verticalLayout_7.addWidget(self.label_8)

        self.comboBox = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout_7.addWidget(self.comboBox)


        self.verticalLayout_10.addLayout(self.verticalLayout_7)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_9 = QLabel(self.scrollAreaWidgetContents)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setEnabled(False)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)

        self.verticalLayout_8.addWidget(self.label_9)

        self.comboBox_2 = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setEnabled(False)

        self.verticalLayout_8.addWidget(self.comboBox_2)


        self.horizontalLayout_9.addLayout(self.verticalLayout_8)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_10 = QLabel(self.scrollAreaWidgetContents)
        self.label_10.setObjectName(u"label_10")
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)

        self.verticalLayout_9.addWidget(self.label_10)

        self.comboBox_3 = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.verticalLayout_9.addWidget(self.comboBox_3)


        self.horizontalLayout_9.addLayout(self.verticalLayout_9)


        self.verticalLayout_10.addLayout(self.horizontalLayout_9)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_4.addWidget(self.scrollArea)


        self.verticalLayout_5.addWidget(self.groupBox_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.progressBar = QProgressBar(Form)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.horizontalLayout_2.addWidget(self.progressBar)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.progressBar_2 = QProgressBar(Form)
        self.progressBar_2.setObjectName(u"progressBar_2")
        self.progressBar_2.setMinimum(1)
        self.progressBar_2.setMaximum(1)
        self.progressBar_2.setValue(0)

        self.horizontalLayout_3.addWidget(self.progressBar_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        font = QFont()
        font.setPointSize(17)
        self.pushButton.setFont(font)

        self.horizontalLayout_4.addWidget(self.pushButton)

        self.commandLinkButton = QCommandLinkButton(Form)
        self.commandLinkButton.setObjectName(u"commandLinkButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.commandLinkButton.sizePolicy().hasHeightForWidth())
        self.commandLinkButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.commandLinkButton)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)

        self.groupBox_3 = QGroupBox(Form)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.widget = CMDTextEdit(self.groupBox_3)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 150))

        self.verticalLayout_11.addWidget(self.widget)


        self.verticalLayout_5.addWidget(self.groupBox_3)

#if QT_CONFIG(shortcut)
        self.label_3.setBuddy(self.lineEdit)
        self.label_4.setBuddy(self.lineEdit_2)
        self.label_5.setBuddy(self.lineEdit_3)
        self.label_6.setBuddy(self.spinBox)
        self.label_7.setBuddy(self.doubleSpinBox)
        self.label_8.setBuddy(self.comboBox)
        self.label_9.setBuddy(self.comboBox_2)
        self.label_10.setBuddy(self.comboBox_3)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.lineEdit, self.radioButton_2)
        QWidget.setTabOrder(self.radioButton_2, self.radioButton)
        QWidget.setTabOrder(self.radioButton, self.pushButton_2)
        QWidget.setTabOrder(self.pushButton_2, self.lineEdit_2)
        QWidget.setTabOrder(self.lineEdit_2, self.scrollArea)
        QWidget.setTabOrder(self.scrollArea, self.lineEdit_3)
        QWidget.setTabOrder(self.lineEdit_3, self.pushButton_3)
        QWidget.setTabOrder(self.pushButton_3, self.spinBox)
        QWidget.setTabOrder(self.spinBox, self.doubleSpinBox)
        QWidget.setTabOrder(self.doubleSpinBox, self.comboBox)
        QWidget.setTabOrder(self.comboBox, self.comboBox_2)
        QWidget.setTabOrder(self.comboBox_2, self.comboBox_3)
        QWidget.setTabOrder(self.comboBox_3, self.pushButton)
        QWidget.setTabOrder(self.pushButton, self.commandLinkButton)

        self.retranslateUi(Form)
        self.radioButton_2.clicked["bool"].connect(self.frame.setDisabled)
        self.radioButton.clicked["bool"].connect(self.frame.setEnabled)

        self.comboBox.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u89c6\u9891\u5408\u5e76\u5de5\u5177", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u5fc5\u586b", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u4e00\u4e2a\u5305\u542b\u89c6\u9891\u6587\u4ef6\u5939\u6216\u8005\u4e00\u4e2a\u5305\u542b\u89c6\u9891\u8def\u5f84\u7684txt\u6587\u4ef6(\u5141\u8bb8\u62d6\u62fd\u6587\u4ef6\u8fdb\u5165\u4e0b\u65b9\u8f93\u5165\u6846)", None))
#if QT_CONFIG(tooltip)
        self.lineEdit.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>\u63a8\u8350\u4f7f\u7528\u5bfc\u5165txt\u7684\u65b9\u5f0f\u8fdb\u884c\u5408\u5e76\uff0c\u80fd\u4fdd\u8bc1\u987a\u5e8f\u4e0d\u4f1a\u51fa\u73b0\u9519\u4e71</p><p>\u901a\u8fc7\u70b9\u51fb\u4e0b\u9762\u7684\u3010\u6587\u4ef6\u6392\u5e8f\u5de5\u5177\u3011\u5bf9\u89c6\u9891\u8fdb\u884c\u6392\u5e8f\uff0c\u7136\u540e\u751f\u6210txt\u6392\u5e8f\u6587\u4ef6</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\u8f93\u5165\u6587\u4ef6\u7684\u8def\u5f84", None))
        self.radioButton_2.setText(QCoreApplication.translate("Form", u"\u9009\u62e9txt\u6587\u4ef6", None))
        self.radioButton.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6587\u4ef6\u5939", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u89c6\u9891\u6587\u4ef6\u5939/txt\u6587\u4ef6", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"<html><head/><body><p>\u8bbe\u7f6e\u641c\u7d22\u89c6\u9891\u7684\u65b9\u5f0f(\u9075\u5faafnmatch\u683c\u5f0f)</p><p>\u8be5\u9009\u9879\u4ec5\u5728\u4f7f\u7528\u6587\u4ef6\u5939\u5408\u5e76\u89c6\u9891\u7684\u65f6\u5019\u624d\u4f1a\u751f\u6548</p></body></html>", None))
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("Form", u"*.mp4", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"\u66f4\u591a\u8bbe\u7f6e", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u8f93\u51fa\u6587\u4ef6\u8def\u5f84(\u5141\u8bb8\u62d6\u62fd\u6587\u4ef6\u8fdb\u5165\u4e0b\u65b9\u8f93\u5165\u6846)", None))
        self.lineEdit_3.setText(QCoreApplication.translate("Form", u"output.mp4", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u8def\u5f84", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u8f93\u51fa\u89c6\u9891\u5e27\u7387", None))
#if QT_CONFIG(tooltip)
        self.spinBox.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>\u8f93\u51fa\u7684\u89c6\u9891\u5c06\u4f1a\u88ab<span style=\" font-weight:700;\">\u5e73\u6ed1\u62bd\u5e27</span>\u6216\u8005<span style=\" font-weight:700;\">\u5e73\u6ed1\u8865\u5e27</span>\u5230\u8fd9\u4e2a\u5e27\u6570</p><p>\u76f8\u6bd4\u4f20\u7edfOpenCv\u7684\u62bd\u5e27\u548c\u8865\u5e27\uff0c\u8be5\u8f6f\u4ef6\u91c7\u7528\u7279\u6b8a\u7684\u5e73\u6ed1\u62bd\u5e27\u548c\u8865\u5e27\u4ece\u5168\u5c40\u8fdb\u884c\u8865\u5e27\u6216\u8005\u62bd\u5e27\uff0c\u80fd<span style=\" font-weight:700;\">\u6700\u5927\u7a0b\u5ea6\u7684\u4fdd\u8bc1\u89c6\u9891\u6d41\u7545\u548c\u8fde\u8d2f</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("Form", u"\u89c6\u9891\u53bb\u9ed1\u8fb9\u91c7\u6837\u7387", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"\u8f93\u51fa\u89c6\u9891\u65b9\u5411", None))
        self.comboBox.setPlaceholderText("")
        self.label_9.setText(QCoreApplication.translate("Form", u"\u6a2a\u5c4f\u89c6\u9891\u65cb\u8f6c\u65b9\u5411", None))
        self.comboBox_2.setPlaceholderText("")
        self.label_10.setText(QCoreApplication.translate("Form", u"\u7ad6\u76f4\u89c6\u9891\u65cb\u8f6c\u65b9\u5411", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u83b7\u53d6\u4fe1\u606f", None))
        self.progressBar.setFormat(QCoreApplication.translate("Form", u"(%v/%m) %p%", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u8be6\u7ec6\u8fdb\u5ea6", None))
        self.progressBar_2.setFormat(QCoreApplication.translate("Form", u"(%v/%m) %p%", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u5f00\u59cb\u5408\u5e76", None))
        self.commandLinkButton.setText(QCoreApplication.translate("Form", u"\u8fdb\u5165\u6587\u4ef6\u6392\u5e8f\u5de5\u5177", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"\u8f93\u51fa", None))
    # retranslateUi

