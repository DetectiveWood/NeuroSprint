# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ГлавнаяaAtcZR.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1750, 1044)
        MainWindow.setStyleSheet(u"background-color:white;\n"
"color:black;")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setLineWidth(3)
        self.stackedWidget.setMidLineWidth(3)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout = QGridLayout(self.page)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 19, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.progressBar = QProgressBar(self.page)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(0, 2))
        self.progressBar.setMaximumSize(QSize(16777215, 4))
        self.progressBar.setStyleSheet(u"*::chunk {\n"
"                background-color: #005cb3;   \n"
"                border-radius: 5px;                                     \n"
"            }")
        self.progressBar.setValue(100)
        self.progressBar.setTextVisible(False)

        self.verticalLayout.addWidget(self.progressBar)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_2)

        self.label_3 = QLabel(self.page)
        self.label_3.setObjectName(u"label_3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setStyleSheet(u"color:#333333;\n"
"font-size: 32px;\n"
"font-weight:800;")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_3)

        self.label_4 = QLabel(self.page)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"color:#333333;\n"
"font-size: 16px;")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_4.addWidget(self.label_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.widget = QWidget(self.page)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"border: 2px solid #cee7ff;\n"
"border-radius:15px;")
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(20, -1, 20, -1)
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(40, -1, -1, -1)
        self.label_6 = QLabel(self.widget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.label_6.setStyleSheet(u"*{color:#333333;\n"
"font-size: 15px;\n"
"border-color: transparent;}\n"
"*::hover{\n"
"background-color:#cee7ff;\n"
"}")

        self.verticalLayout_5.addWidget(self.label_6)

        self.label_7 = QLabel(self.widget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"*{\n"
"color:#333333;\n"
"font-size: 15px;\n"
"border-color: transparent;\n"
"}\n"
"\n"
"*::hover{\n"
"background-color:#cee7ff;\n"
"}")

        self.verticalLayout_5.addWidget(self.label_7)

        self.label_8 = QLabel(self.widget)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setStyleSheet(u"*{\n"
"color:#333333;\n"
"font-size: 15px;\n"
"border-color: transparent;\n"
"}\n"
"\n"
"*::hover{\n"
"background-color:#cee7ff;\n"
"}")

        self.verticalLayout_5.addWidget(self.label_8)

        self.label_5 = QLabel(self.widget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"*{\n"
"color:#333333;\n"
"font-size: 15px;\n"
"border-color: transparent;\n"
"}\n"
"\n"
"*::hover{\n"
"background-color:#cee7ff;\n"
"}")

        self.verticalLayout_5.addWidget(self.label_5)


        self.verticalLayout_3.addLayout(self.verticalLayout_5)


        self.verticalLayout.addWidget(self.widget)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButton_2 = QPushButton(self.page)
        self.pushButton_2.setObjectName(u"pushButton_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy1)
        self.pushButton_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_2.setStyleSheet(u"color:white;\n"
"font-size: 18px;\n"
"font-weight: bold;	\n"
"background-color:#005cb3;\n"
"border:1px solid transparent;\n"
"border-radius:25px;")

        self.verticalLayout_2.addWidget(self.pushButton_2)

        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setObjectName(u"pushButton_4")
        sizePolicy1.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy1)
        self.pushButton_4.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_4.setStyleSheet(u"color:#005cb3;\n"
"background-color:#ffffff;\n"
"border:2px solid #005cb3;\n"
"font-size: 18px;\n"
"font-weight: bold;	")

        self.verticalLayout_2.addWidget(self.pushButton_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_4 = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.label_9 = QLabel(self.page)
        self.label_9.setObjectName(u"label_9")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy2)
        self.label_9.setStyleSheet(u"color:#666666;\n"
"font-size: 13px;")
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.label_9)

        self.horizontalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)

        self.pushButton_9 = QPushButton(self.page)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_9.setStyleSheet(u"color:#005cb3;\n"
"text-decoration: underline #005cb3;\n"
"font-size: 13px;\n"
"border:none;")

        self.horizontalLayout_3.addWidget(self.pushButton_9)

        self.horizontalSpacer_3 = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)
        self.label.setStyleSheet(u"color:#999999;\n"
"font-size: 11px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)


        self.verticalLayout.addLayout(self.verticalLayout_2)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.horizontalLayout_4 = QHBoxLayout(self.page_2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_11 = QLabel(self.page_2)
        self.label_11.setObjectName(u"label_11")
        sizePolicy2.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy2)
        self.label_11.setStyleSheet(u"color:#005cb3;\n"
"font-size: 32px;\n"
"font-weight:800;")

        self.verticalLayout_6.addWidget(self.label_11)

        self.verticalSpacer_4 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)

        self.line_3 = QFrame(self.page_2)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setStyleSheet(u"background-color:blue;")
        self.line_3.setLineWidth(3)
        self.line_3.setMidLineWidth(3)
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_6.addWidget(self.line_3)

        self.verticalSpacer_3 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)

        self.horizontalWidget = QWidget(self.page_2)
        self.horizontalWidget.setObjectName(u"horizontalWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy3)
        self.horizontalLayout_5 = QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_13 = QLabel(self.horizontalWidget)
        self.label_13.setObjectName(u"label_13")
        sizePolicy2.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy2)
        self.label_13.setStyleSheet(u"font-size: 16px;\n"
"font-weight: 600;")

        self.verticalLayout_8.addWidget(self.label_13)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_14 = QLabel(self.horizontalWidget)
        self.label_14.setObjectName(u"label_14")
        sizePolicy2.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy2)
        self.label_14.setStyleSheet(u"color:#666666;\n"
"font-size: 13px;")

        self.horizontalLayout_6.addWidget(self.label_14)

        self.label_15 = QLabel(self.horizontalWidget)
        self.label_15.setObjectName(u"label_15")
        sizePolicy2.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy2)
        self.label_15.setStyleSheet(u"color:#666666;\n"
"font-size: 13px;")

        self.horizontalLayout_6.addWidget(self.label_15)


        self.verticalLayout_8.addLayout(self.horizontalLayout_6)


        self.horizontalLayout_5.addLayout(self.verticalLayout_8)


        self.verticalLayout_6.addWidget(self.horizontalWidget)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_19 = QVBoxLayout()
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.pushButton_6 = QPushButton(self.page_2)
        self.pushButton_6.setObjectName(u"pushButton_6")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButton_6.sizePolicy().hasHeightForWidth())
        self.pushButton_6.setSizePolicy(sizePolicy4)
        self.pushButton_6.setMinimumSize(QSize(0, 50))
        self.pushButton_6.setStyleSheet(u"text-align: left;\n"
"                padding: 0 20px;\n"
"                border-radius: 10px;\n"
"                font-size: 15px;\n"
"                font-weight: 500;")

        self.verticalLayout_19.addWidget(self.pushButton_6)

        self.pushButton_3 = QPushButton(self.page_2)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy4.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy4)
        self.pushButton_3.setMinimumSize(QSize(0, 50))
        self.pushButton_3.setStyleSheet(u"text-align: left;\n"
"                padding: 0 20px;\n"
"                border-radius: 10px;\n"
"                font-size: 15px;\n"
"                font-weight: 500;")

        self.verticalLayout_19.addWidget(self.pushButton_3)

        self.pushButton_7 = QPushButton(self.page_2)
        self.pushButton_7.setObjectName(u"pushButton_7")
        sizePolicy4.setHeightForWidth(self.pushButton_7.sizePolicy().hasHeightForWidth())
        self.pushButton_7.setSizePolicy(sizePolicy4)
        self.pushButton_7.setMinimumSize(QSize(0, 50))
        self.pushButton_7.setStyleSheet(u"text-align: left;\n"
"                padding: 0 20px;\n"
"                border-radius: 10px;\n"
"                font-size: 15px;\n"
"                font-weight: 500;")

        self.verticalLayout_19.addWidget(self.pushButton_7)


        self.verticalLayout_16.addLayout(self.verticalLayout_19)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_16.addItem(self.verticalSpacer_2)


        self.verticalLayout_6.addLayout(self.verticalLayout_16)

        self.pushButton = QPushButton(self.page_2)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy4.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy4)
        self.pushButton.setMinimumSize(QSize(0, 50))
        self.pushButton.setStyleSheet(u"text-align: left;\n"
"                padding: 0 20px;\n"
"                border-radius: 10px;\n"
"                font-size: 15px;\n"
"                font-weight: 500;")

        self.verticalLayout_6.addWidget(self.pushButton)


        self.horizontalLayout_4.addLayout(self.verticalLayout_6)

        self.line = QFrame(self.page_2)
        self.line.setObjectName(u"line")
        self.line.setStyleSheet(u"background-color:blue;")
        self.line.setLineWidth(3)
        self.line.setMidLineWidth(3)
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_4.addWidget(self.line)

        self.verticalWidget_2 = QWidget(self.page_2)
        self.verticalWidget_2.setObjectName(u"verticalWidget_2")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.verticalWidget_2.sizePolicy().hasHeightForWidth())
        self.verticalWidget_2.setSizePolicy(sizePolicy5)
        self.verticalLayout_7 = QVBoxLayout(self.verticalWidget_2)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_16 = QLabel(self.verticalWidget_2)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setStyleSheet(u"font-size: 24px;\n"
"font-weight: 600;\n"
"color:#2c3e50;")

        self.horizontalLayout_7.addWidget(self.label_16)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_6)

        self.label_17 = QLabel(self.verticalWidget_2)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_7.addWidget(self.label_17)


        self.verticalLayout_7.addLayout(self.horizontalLayout_7)

        self.pushButton_8 = QPushButton(self.verticalWidget_2)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setMinimumSize(QSize(0, 90))
        self.pushButton_8.setStyleSheet(u"background-color: #005cb3;\n"
"color: white;\n"
"border: none;\n"
"border-radius: 20px;\n"
"font-size: 24px;\n"
"font-weight: bold;\n"
"letter-spacing: 2px;\n"
"margin: 10px 0;\n"
"text-align:left;")

        self.verticalLayout_7.addWidget(self.pushButton_8)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_5)


        self.horizontalLayout_4.addWidget(self.verticalWidget_2)

        self.stackedWidget.addWidget(self.page_2)

        self.horizontalLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1750, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.progressBar.setFormat("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Image", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"REACTION TEST", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0432\u0435\u0440\u044c \u0441\u0432\u043e\u044e \u0441\u043a\u043e\u0440\u043e\u0441\u0442\u044c", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u2713 \u0422\u043e\u0447\u043d\u043e\u0435 \u0438\u0437\u043c\u0435\u0440\u0435\u043d\u0438\u0435 \u0440\u0435\u0430\u043a\u0446\u0438\u0438", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u2713 \u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u0438 \u043f\u0440\u043e\u0433\u0440\u0435\u0441\u0441", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u2713 \u0421\u043e\u0440\u0435\u0432\u043d\u0443\u0439\u0441\u044f \u0441 \u0434\u0440\u0443\u0437\u044c\u044f\u043c\u0438", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u2713 \u0420\u0430\u0437\u043d\u044b\u0435 \u0440\u0435\u0436\u0438\u043c\u044b \u0438\u0433\u0440\u044b", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0430\u043a\u043a\u0430\u0443\u043d\u0442", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0436\u0435 \u0435\u0441\u0442\u044c \u0430\u043a\u043a\u0430\u0443\u043d\u0442? \u0412\u043e\u0439\u0442\u0438", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"\u0425\u043e\u0442\u0438\u0442\u0435 \u043f\u043e\u043f\u0440\u043e\u0431\u043e\u0432\u0430\u0442\u044c \u0431\u0435\u0437 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u0438?", None))
        self.pushButton_9.setText(QCoreApplication.translate("MainWindow", u"\u0413\u043e\u0441\u0442\u0435\u0432\u043e\u0439 \u0432\u0445\u043e\u0434", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0435\u0440\u0441\u0438\u044f 1.0.0", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"REACTION TEST", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"HHorus", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0440\u043e\u0432\u0435\u043d\u044c 1", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"1250 \u043e\u0447\u043a\u043e\u0432", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0441\u043a\u0430 \u043b\u0438\u0434\u0435\u0440\u043e\u0432", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0439\u0442\u0438", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0440\u043e \u041f\u043e\u0436\u0430\u043b\u043e\u0432\u0430\u0442\u044c", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"28 \u0444\u0435\u0432\u0440\u0430\u043b\u044f 2026", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"  \u041d\u0410\u0427\u0410\u0422\u042c \u0422\u0415\u0421\u0422", None))
    # retranslateUi

