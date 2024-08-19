from PyQt6 import QtCore, QtWidgets
from config_ui import Config

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1422, 200)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Устанавливаем стили для центрального виджета
        self.centralwidget.setStyleSheet(self.get_styles())

        # Основной горизонтальный компоновщик
        main_layout = QtWidgets.QHBoxLayout(self.centralwidget)

        # Левая панель
        left_panel = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left_panel)

        # Текущее изображение
        self.current_image = QtWidgets.QLabel(parent=self.centralwidget)
        self.current_image.setObjectName("current_image")
        left_panel.addWidget(self.current_image)

        # Предыдущее изображение
        self.previous_image = QtWidgets.QLabel(parent=self.centralwidget)
        self.previous_image.setObjectName("previous_image")
        left_panel.addWidget(self.previous_image)

        # Кнопки управления изображениями
        self.create_image_control_buttons(left_panel)

        # Правая панель
        right_panel = QtWidgets.QVBoxLayout()
        main_layout.addLayout(right_panel)

        # Название изображения
        self.image_name = QtWidgets.QLabel(parent=self.centralwidget)
        self.image_name.setObjectName("image_name")
        right_panel.addWidget(self.image_name)

        # Кнопки "Сохранить", "Применить", "Назад"
        self.create_action_buttons(right_panel)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1422, 22))
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
        self.add_parametrs.setText(_translate("MainWindow", "Применить"))
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
                font-size: {Config.LABEL_FONT_SIZE}px;  /* Размер шрифта для названий полей ввода */
                border: 2px solid #0078d7;  /* Цвет и толщина рамки */
                border-radius: 8px;  /* Закругление углов рамки */
                padding: 10px;  /* Увеличенные отступы внутри QLabel */
                background-color: {Config.BACKGROUND_COLOR};  /* Цвет фона QLabel */
                color: {Config.TEXT_COLOR};  /* Цвет текста */
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
        """

    def create_image_control_buttons(self, layout):
        button_layout = QtWidgets.QHBoxLayout()

        self.previous_button = QtWidgets.QPushButton("Назад", parent=self.centralwidget)
        self.next_button = QtWidgets.QPushButton("Вперед", parent=self.centralwidget)
        self.open_button = QtWidgets.QPushButton("Открыть", parent=self.centralwidget)
        self.save_button = QtWidgets.QPushButton("Сохранить", parent=self.centralwidget)

        button_layout.addWidget(self.previous_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def create_action_buttons(self, layout):
        button_layout = QtWidgets.QVBoxLayout()

        self.add_parametrs = QtWidgets.QPushButton("Применить", parent=self.centralwidget)
        self.unstage_parametrs = QtWidgets.QPushButton("Назад", parent=self.centralwidget)

        button_layout.addWidget(self.add_parametrs)
        button_layout.addWidget(self.unstage_parametrs)

        layout.addLayout(button_layout)