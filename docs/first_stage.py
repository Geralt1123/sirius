from PyQt6 import QtCore, QtWidgets

from src.first_stage.config_ui import Config


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 800)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet(self.get_styles())

        # Создаем основной вертикальный компоновщик
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Создаем горизонтальный компоновщик для кнопок
        button_layout = QtWidgets.QHBoxLayout()

        self.previous_button = QtWidgets.QPushButton(parent=self.centralwidget)
        button_layout.addWidget(self.previous_button)

        self.next_button = QtWidgets.QPushButton(parent=self.centralwidget)
        button_layout.addWidget(self.next_button)

        self.open_button = QtWidgets.QPushButton(parent=self.centralwidget)
        button_layout.addWidget(self.open_button)

        self.save_button = QtWidgets.QPushButton(parent=self.centralwidget)
        button_layout.addWidget(self.save_button)

        self.unstage_parametrs = QtWidgets.QPushButton(parent=self.centralwidget)
        button_layout.addWidget(self.unstage_parametrs)

        main_layout.addLayout(button_layout)

        # Добавляем метку для имени изображения
        self.image_name = QtWidgets.QLabel("Название изображения", parent=self.centralwidget)
        main_layout.addWidget(self.image_name)

        # Создаем метку для текущего изображения
        self.current_image = QtWidgets.QLabel(parent=self.centralwidget)
        main_layout.addWidget(self.current_image)

        # Создаем метку для предыдущего изображения
        self.previous_image = QtWidgets.QLabel(parent=self.centralwidget)
        main_layout.addWidget(self.previous_image)

        # Создаем сетку для групп фильтров
        filter_layout = QtWidgets.QGridLayout()
        self.create_gaussian_group(filter_layout)
        self.create_erosion_group(filter_layout)
        self.create_dilation_group(filter_layout)
        self.create_bilateral_group(filter_layout)

        # Добавляем сетку фильтров в основной компоновщик
        main_layout.addLayout(filter_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1600, 800))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def create_gaussian_group(self, layout):
        groupBox = QtWidgets.QGroupBox("Гауссово размытие", self.centralwidget)
        group_layout = QtWidgets.QGridLayout(groupBox)

        group_layout.addWidget(QtWidgets.QLabel("Размер ядра"), 0, 0)
        self.gaus_core_x = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.gaus_core_x, 0, 1)

        self.gaus_core_y = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.gaus_core_y, 0, 2)

        group_layout.addWidget(QtWidgets.QLabel("Отклонение ядра"), 1, 0)
        self.gaus_sigma_x = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.gaus_sigma_x, 1, 1)

        self.gaus_sigma_y = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.gaus_sigma_y, 1, 2)

        self.add_gaus = QtWidgets.QPushButton("Применить", parent=groupBox)
        group_layout.addWidget(self.add_gaus, 2, 0, 1, 3)

        layout.addWidget(groupBox, 0, 0)  # Добавляем в первую строку, первый столбец

    def create_erosion_group(self, layout):
        groupBox = QtWidgets.QGroupBox("Эрозия", self.centralwidget)
        group_layout = QtWidgets.QGridLayout(groupBox)

        group_layout.addWidget(QtWidgets.QLabel("Структурный элемент"), 0, 0)
        self.eroz_x = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.eroz_x, 0, 1)

        self.eroz_y = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.eroz_y, 0, 2)

        group_layout.addWidget(QtWidgets.QLabel("Итерации"), 1, 0)
        self.eroz_iteration = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.eroz_iteration, 1, 1, 1, 2)

        self.add_eroz = QtWidgets.QPushButton("Применить", parent=groupBox)
        group_layout.addWidget(self.add_eroz, 2, 0, 1, 3)

        layout.addWidget(groupBox, 0, 1)  # Добавляем в первую строку, второй столбец

    def create_dilation_group(self, layout):
        groupBox = QtWidgets.QGroupBox("Дилатация", self.centralwidget)
        group_layout = QtWidgets.QGridLayout(groupBox)

        group_layout.addWidget(QtWidgets.QLabel("Структурный элемент"), 0, 0)
        self.dilatation_x = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.dilatation_x, 0, 1)

        self.dilatation_y = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.dilatation_y, 0, 2)

        group_layout.addWidget(QtWidgets.QLabel("Итерации"), 1, 0)
        self.dilatation_iteration = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.dilatation_iteration, 1, 1, 1, 2)

        self.add_dilatation = QtWidgets.QPushButton("Применить", parent=groupBox)
        group_layout.addWidget(self.add_dilatation, 2, 0, 1, 3)

        layout.addWidget(groupBox, 1, 0)  # Добавляем во вторую строку, первый столбец

    def create_bilateral_group(self, layout):
        groupBox = QtWidgets.QGroupBox("Двусторонний фильтр", self.centralwidget)
        group_layout = QtWidgets.QGridLayout(groupBox)

        group_layout.addWidget(QtWidgets.QLabel("Диаметр пикселя"), 0, 0)
        self.bilat_d = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.bilat_d, 0, 1)

        group_layout.addWidget(QtWidgets.QLabel("Сигма цвета"), 1, 0)
        self.bilat_color = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.bilat_color, 1, 1)

        group_layout.addWidget(QtWidgets.QLabel("Сигма координат"), 2, 0)
        self.bilat_coord = QtWidgets.QLineEdit(parent=groupBox)
        group_layout.addWidget(self.bilat_coord, 2, 1)

        self.add_bilat = QtWidgets.QPushButton("Применить", parent=groupBox)
        group_layout.addWidget(self.add_bilat, 3, 0, 1, 2)

        layout.addWidget(groupBox, 1, 1)  # Добавляем во вторую строку, второй столбец

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.next_button.setText(_translate("MainWindow", ">"))
        self.previous_button.setText(_translate("MainWindow", "<"))
        self.open_button.setText(_translate("MainWindow", "Открыть"))
        self.save_button.setText(_translate("MainWindow", "Сохранить"))
        self.unstage_parametrs.setText(_translate("MainWindow", "Назад"))
        self.image_name.setText(_translate("MainWindow", "Название изображения"))

    def get_styles(self):
        return f"""
            QWidget {{
                background-color: {Config.BACKGROUND_COLOR};
                color: {Config.TEXT_COLOR};
                font-family: Arial;  /* Шрифт по умолчанию */
            }}

            QLabel {{
                font-family: Arial;  /* Шрифт для заголовков */
                font-weight: bold;
                font-size: {Config.LABEL_FONT_SIZE}px;  /* Размер шрифта для заголовков */
                padding: 5px;  /* Отступы для меток */
            }}

            QLabel#current_image, QLabel#previous_image {{
                border: 2px solid {Config.HOVER_BORDER_COLOR};  /* Рамка для меток */
                border-radius: 4px;  /* Закругление углов рамки */
                padding: 5px;  /* Отступы внутри меток */
            }}

            QPushButton {{
                padding: 10px 20px;
                height: 22px;
                background-color: {Config.BUTTON_COLOR};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-family: Arial;  /* Шрифт для кнопок */
                font-weight: bold;
                font-size: {Config.BUTTON_FONT_SIZE}px;  /* Размер шрифта для кнопок */
                transition: background-color 0.3s;
            }}

            QPushButton:hover {{
                background-color: {Config.BUTTON_HOVER_COLOR};
            }}

            QLineEdit {{
                padding: 10px;
                border: 1px solid {Config.HOVER_BORDER_COLOR};
                border-radius: 8px;
                background-color: {Config.INPUT_BACKGROUND_COLOR};
                color: {Config.QLINE_TEXT_COLOR};
                font-family: Arial;  /* Шрифт для текстовых полей */
                font-size: {Config.FONT_SIZE}px;  /* Размер шрифта для текстовых полей */
            }}

            QLineEdit:focus {{
                border: 1px solid {Config.BUTTON_COLOR};  /* Изменение цвета рамки при фокусе */
            }}

            QGroupBox {{
                border: 2px solid {Config.HOVER_BORDER_COLOR};  /* Рамка для групповых полей */
                border-radius: 8px;  /* Закругление углов рамки */
                margin-top: 10px;  /* Отступ сверху для групповых полей */
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;  /* Отступ заголовка группы */
                font-weight: bold;  /* Жирный шрифт для заголовка группы */
                font-size: {Config.GROUPBOX_TITLE_FONT_SIZE}px;  /* Размер шрифта для заголовка группы */
            }}
        """
