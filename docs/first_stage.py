# Form implementation generated from reading ui file '.\first_stage.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1519, 794)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.current_image = QtWidgets.QLabel(parent=self.centralwidget)
        self.current_image.setGeometry(QtCore.QRect(10, 10, 1035, 331))
        self.current_image.setMouseTracking(False)
        self.current_image.setObjectName("current_image")
        self.next_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.next_button.setGeometry(QtCore.QRect(980, 360, 51, 51))
        self.next_button.setObjectName("next_button")
        self.previous_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.previous_button.setGeometry(QtCore.QRect(10, 360, 51, 51))
        self.previous_button.setObjectName("previous_button")
        self.previous_image = QtWidgets.QLabel(parent=self.centralwidget)
        self.previous_image.setGeometry(QtCore.QRect(10, 430, 1035, 331))
        self.previous_image.setObjectName("previous_image")
        self.open_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.open_button.setGeometry(QtCore.QRect(80, 360, 151, 51))
        self.open_button.setObjectName("open_button")
        self.save_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.save_button.setGeometry(QtCore.QRect(800, 360, 151, 51))
        self.save_button.setObjectName("save_button")
        self.unstage_parametrs = QtWidgets.QPushButton(parent=self.centralwidget)
        self.unstage_parametrs.setGeometry(QtCore.QRect(1260, 710, 151, 51))
        self.unstage_parametrs.setObjectName("unstage_parametrs")
        self.image_name = QtWidgets.QLabel(parent=self.centralwidget)
        self.image_name.setGeometry(QtCore.QRect(240, 380, 341, 16))
        self.image_name.setObjectName("image_name")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(1040, 10, 471, 81))
        self.groupBox.setObjectName("groupBox")
        self.gaus_core_x = QtWidgets.QTextEdit(parent=self.groupBox)
        self.gaus_core_x.setGeometry(QtCore.QRect(10, 40, 31, 31))
        self.gaus_core_x.setObjectName("gaus_core_x")
        self.label = QtWidgets.QLabel(parent=self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 20, 71, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(50, 50, 16, 16))
        self.label_2.setObjectName("label_2")
        self.gaus_core_y = QtWidgets.QTextEdit(parent=self.groupBox)
        self.gaus_core_y.setGeometry(QtCore.QRect(70, 40, 31, 31))
        self.gaus_core_y.setObjectName("gaus_core_y")
        self.label_3 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(160, 20, 101, 16))
        self.label_3.setObjectName("label_3")
        self.gaus_sigma_x = QtWidgets.QTextEdit(parent=self.groupBox)
        self.gaus_sigma_x.setGeometry(QtCore.QRect(170, 40, 31, 31))
        self.gaus_sigma_x.setObjectName("gaus_sigma_x")
        self.label_4 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(140, 50, 16, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(220, 50, 16, 16))
        self.label_5.setObjectName("label_5")
        self.gaus_sigma_y = QtWidgets.QTextEdit(parent=self.groupBox)
        self.gaus_sigma_y.setGeometry(QtCore.QRect(250, 40, 31, 31))
        self.gaus_sigma_y.setObjectName("gaus_sigma_y")
        self.add_gaus = QtWidgets.QPushButton(parent=self.groupBox)
        self.add_gaus.setGeometry(QtCore.QRect(310, 20, 151, 51))
        self.add_gaus.setObjectName("add_gaus")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(1040, 110, 471, 81))
        self.groupBox_2.setObjectName("groupBox_2")
        self.label_11 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_11.setGeometry(QtCore.QRect(160, 20, 61, 16))
        self.label_11.setObjectName("label_11")
        self.eroz_iteration = QtWidgets.QTextEdit(parent=self.groupBox_2)
        self.eroz_iteration.setGeometry(QtCore.QRect(170, 40, 31, 31))
        self.eroz_iteration.setObjectName("eroz_iteration")
        self.add_eroz = QtWidgets.QPushButton(parent=self.groupBox_2)
        self.add_eroz.setGeometry(QtCore.QRect(310, 20, 151, 51))
        self.add_eroz.setObjectName("add_eroz")
        self.label_12 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_12.setGeometry(QtCore.QRect(10, 20, 131, 16))
        self.label_12.setObjectName("label_12")
        self.eroz_x = QtWidgets.QTextEdit(parent=self.groupBox_2)
        self.eroz_x.setGeometry(QtCore.QRect(10, 40, 31, 31))
        self.eroz_x.setObjectName("eroz_x")
        self.label_13 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_13.setGeometry(QtCore.QRect(50, 50, 16, 16))
        self.label_13.setObjectName("label_13")
        self.eroz_y = QtWidgets.QTextEdit(parent=self.groupBox_2)
        self.eroz_y.setGeometry(QtCore.QRect(70, 40, 31, 31))
        self.eroz_y.setObjectName("eroz_y")
        self.groupBox_3 = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(1040, 210, 471, 81))
        self.groupBox_3.setObjectName("groupBox_3")
        self.add_dilatation = QtWidgets.QPushButton(parent=self.groupBox_3)
        self.add_dilatation.setGeometry(QtCore.QRect(310, 20, 151, 51))
        self.add_dilatation.setObjectName("add_dilatation")
        self.label_14 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_14.setGeometry(QtCore.QRect(10, 20, 131, 16))
        self.label_14.setObjectName("label_14")
        self.dilatation_x = QtWidgets.QTextEdit(parent=self.groupBox_3)
        self.dilatation_x.setGeometry(QtCore.QRect(10, 40, 31, 31))
        self.dilatation_x.setObjectName("dilatation_x")
        self.label_15 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_15.setGeometry(QtCore.QRect(50, 50, 16, 16))
        self.label_15.setObjectName("label_15")
        self.dilatation_y = QtWidgets.QTextEdit(parent=self.groupBox_3)
        self.dilatation_y.setGeometry(QtCore.QRect(70, 40, 31, 31))
        self.dilatation_y.setObjectName("dilatation_y")
        self.label_16 = QtWidgets.QLabel(parent=self.groupBox_3)
        self.label_16.setGeometry(QtCore.QRect(160, 20, 61, 16))
        self.label_16.setObjectName("label_16")
        self.dilatation_iteration = QtWidgets.QTextEdit(parent=self.groupBox_3)
        self.dilatation_iteration.setGeometry(QtCore.QRect(170, 40, 31, 31))
        self.dilatation_iteration.setObjectName("dilatation_iteration")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1519, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.next_button.setText(_translate("MainWindow", ">"))
        self.previous_button.setText(_translate("MainWindow", "<"))
        self.open_button.setText(_translate("MainWindow", "Открыть"))
        self.save_button.setText(_translate("MainWindow", "Сохранить"))
        self.unstage_parametrs.setText(_translate("MainWindow", "Назад"))
        self.image_name.setText(_translate("MainWindow", "Название изображения"))
        self.groupBox.setTitle(_translate("MainWindow", "Гауссово размытие"))
        self.label.setText(_translate("MainWindow", "Размер ядра"))
        self.label_2.setText(_translate("MainWindow", "X"))
        self.label_3.setText(_translate("MainWindow", "Отклонение ядра"))
        self.label_4.setText(_translate("MainWindow", "X="))
        self.label_5.setText(_translate("MainWindow", "Y="))
        self.add_gaus.setText(_translate("MainWindow", "Применить"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Эрозия"))
        self.label_11.setText(_translate("MainWindow", "Итерации"))
        self.add_eroz.setText(_translate("MainWindow", "Применить"))
        self.label_12.setText(_translate("MainWindow", "Структурный элемент"))
        self.label_13.setText(_translate("MainWindow", "X"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Дилатация"))
        self.add_dilatation.setText(_translate("MainWindow", "Применить"))
        self.label_14.setText(_translate("MainWindow", "Структурный элемент"))
        self.label_15.setText(_translate("MainWindow", "X"))
        self.label_16.setText(_translate("MainWindow", "Итерации"))
