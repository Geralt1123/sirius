import logging
import os
import string
import pickle
import random
from pathlib import Path

import requests
import bcrypt
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer, QTime, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QTabWidget, QVBoxLayout, QDialog, \
    QProgressBar, QLabel, QLineEdit, QPushButton, QMessageBox
from cryptography.fernet import Fernet

from first_stage import Ui_MainWindow as FirstStageUi
from markup import MainWindow as MarkupWindow
from config_ui import Config
from detect import DetectWindow


class BaseDialog(QDialog):
    def __init__(self, title, width, height):
        super().__init__()
        self.setWindowTitle(title) # Устанавливает заголовок окна
        self.setFixedSize(width, height) # Устанавливает фиксированный размер окна

    def set_styles(self, styles):
        self.setStyleSheet(styles)  # Устанавливает стили для окна


class ActionDialog(BaseDialog):
    action_selected = pyqtSignal(str)

    def __init__(self):
        # Создает элементы интерфейса для выбора действия
        # Подключает кнопки к методам выбора действия
        super().__init__("Дальнейшие действия", 300, 150)  # Заголовок и размер окна
        layout = QVBoxLayout()
        self.label = QLabel("Выберите дальнейшие действия:")
        self.label.setStyleSheet("color: white;")
        self.manual_markup_button = QPushButton("Перейти к ручной разметке")
        self.automatic_markup_button = QPushButton("Перейти к автоматической разметке")

        layout.addWidget(self.label)
        layout.addWidget(self.manual_markup_button)
        layout.addWidget(self.automatic_markup_button)
        self.setLayout(layout)

        self.set_styles(self.get_styles())
        self.manual_markup_button.clicked.connect(lambda: self.select_action("manual"))
        self.automatic_markup_button.clicked.connect(lambda: self.select_action("automatic"))

    def select_action(self, action):  # Излучает сигнал с выбранным действием
        self.action_selected.emit(action)
        self.accept()

    def get_styles(self): # Возвращает стили для диалогового окна
        return """
            QDialog { background-color: #151D2C; border: none; }
            QLabel { color: white; }
            QPushButton {
                background-color: #0078d7; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 12px;
            }
            QPushButton:hover { background-color: #0056a1; }
        """


class AuthDialog(BaseDialog):
    def __init__(self):
        super().__init__("Авторизация", 300, 300)  # Заголовок и размер окна
        self.layout = QVBoxLayout() # Создает вертикальный layout
        self.setup_ui() # Настраивает элементы интерфейса
        self.set_styles(self.get_styles())
        self.attempts = 0
        self.locked_until = None
        self.ip_attempts = {}
        self.max_attempts_per_ip = 5
        self.block_time = 30
        self.captcha_input = None  # Инициализация переменной для капчи
        self.load_state() # Загружает состояние (например, попытки входа)

    def setup_ui(self):
        # Создает и добавляет элементы интерфейса для ввода логина и пароля
        # Подключает кнопки к методам проверки учетных данных
        self.label_username = QLabel("Логин:")
        self.username_input = QLineEdit()
        self.label_password = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.cancel_button = QPushButton("Отмена")

        self.layout.addWidget(self.label_username)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.cancel_button)

        self.setLayout(self.layout)
        self.login_button.clicked.connect(self.check_credentials)
        self.cancel_button.clicked.connect(self.reject)

        self.stored_username = "admin"
        self.stored_password_hash = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt())

    def get_styles(self):
        return """
            QDialog { background-color: #151D2C; border: none; }
            QLabel { color: white; }
            QLineEdit {
                background-color: #0078d7; color: white; border: 1px solid #0056a1; border-radius: 5px; padding: 5px; font-size: 12px;
            }
            QPushButton {
                background-color: #0078d7; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 12px;
            }
            QPushButton:hover { background-color: #0056a1; }
        """

    def get_external_ip(self): # Получает внешний IP-адрес пользователя
        try:
            return requests.get('https://api.ipify.org').text
        except requests.RequestException:
            return "0.0.0.0"

    def check_credentials(self):
        # Проверяет учетные данные пользователя
        # Если учетные данные верны, закрывает диалог
        # Если нет, обрабатывает неудачную попытку вход
        external_ip = self.get_external_ip()
        if self.is_ip_locked(external_ip):
            QMessageBox.warning(self, "Ошибка", "Вход заблокирован с этого IP. Попробуйте позже.")
            return

        username = self.username_input.text()
        password = self.password_input.text()

        # Проверяем, отображается ли капча
        if self.captcha_input is not None and self.captcha_input.text() != self.captcha_text:
            QMessageBox.warning(self, "Ошибка", "Неверная капча. Попробуйте снова.")
            return

        if self.validate_credentials(username, password):
            self.accept()
            self.reset_ip_attempts(external_ip)
        else:
            self.handle_failed_attempt(external_ip)

    def is_ip_locked(self, external_ip): # Проверяет, заблокирован ли IP-адрес
        return (external_ip in self.ip_attempts and
                self.ip_attempts[external_ip]['locked_until'] and
                QTime.currentTime() < self.ip_attempts[external_ip]['locked_until'])

    def reset_ip_attempts(self, external_ip): # Сбрасывает количество попыток входа для данного IP
        if external_ip in self.ip_attempts:
            self.ip_attempts[external_ip]['attempts'] = 0

    def handle_failed_attempt(self, external_ip): # Обрабатывает неудачную попытку входа
        # Увеличивает счетчик попыток и блокирует IP при необходимости
        if external_ip not in self.ip_attempts:
            self.ip_attempts[external_ip] = {'attempts': 0, 'locked_until': None}

        self.ip_attempts[external_ip]['attempts'] += 1

        if self.ip_attempts[external_ip]['attempts'] >= self.max_attempts_per_ip:
            self.ip_attempts[external_ip]['locked_until'] = QTime.currentTime().addSecs(self.block_time)
            QMessageBox.warning(self, "Ошибка", "Слишком много неправильных попыток. Попробуйте позже.")
            self.save_state()
            return

        if self.ip_attempts[external_ip]['attempts'] == 3:
            self.show_captcha()

        QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль. Попробуйте снова.")
        self.save_state()

    def validate_credentials(self, username, password): # Проверяет, соответствуют ли введенные учетные данные сохраненным
        return username == self.stored_username and bcrypt.checkpw(password.encode('utf-8'), self.stored_password_hash)

    def show_captcha(self): # Генерирует и отображает капчу после нескольких неудачных попыток входа
        self.captcha_text = self.generate_captcha()

        if self.captcha_input is None:  # Проверяем, существует ли уже поле для капчи
            self.captcha_input = QLineEdit(self)
            self.captcha_input.setPlaceholderText("Введите капчу: " + self.captcha_text)
            self.layout.addWidget(self.captcha_input)  # Добавляем поле для капчи в layout
            self.captcha_input.setFocus()  # Устанавливаем фокус на поле для капчи
        else:
            # Если капча уже была показана, просто обновляем текст
            self.captcha_input.setPlaceholderText("Введите капчу: " + self.captcha_text)
            self.captcha_input.clear()  # Очищаем предыдущее значение
            self.captcha_input.setFocus()  # Устанавливаем фокус на поле для капчи

    def generate_captcha(self): # Генерирует случайную строку для капчи
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(6))

    def save_state(self): # Сохраняет состояние (например, попытки входа) в файл
        key = os.environ.get('SECRET_KEY')
        if key is None:
            QMessageBox.critical(self, "Ошибка", "Не установлен SECRET_KEY.")
            return
        try:
            data = {'ip_attempts': self.ip_attempts}
            key = key.encode()
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(pickle.dumps(data))

            with open('auth_state.pkl', 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить состояние: {str(e)}")

    def load_state(self): # Загружает состояние из файла
        key = os.environ.get('SECRET_KEY')
        if key is None:
            QMessageBox.critical(self, "Ошибка", "Не установлен SECRET_KEY.")
            return
        try:
            with open('auth_state.pkl', 'rb') as f:
                encrypted_data = f.read()
                key = key.encode()
                fernet = Fernet(key)
                data = pickle.loads(fernet.decrypt(encrypted_data))
                self.ip_attempts = data.get('ip_attempts', {})
        except FileNotFoundError:
            self.ip_attempts = {}
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить состояние: {str(e)}")


class LoadingScreen(BaseDialog):
    def __init__(self):
        super().__init__("Загрузка", 300, 100) # Заголовок и размер окна
        # Создает элементы интерфейса для отображения процесса загрузки
        layout = QVBoxLayout()
        self.label = QLabel("Загрузка, пожалуйста подождите...")
        self.label.setStyleSheet("color: white;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.set_styles(self.get_styles())

    def get_styles(self):
        return """
            QDialog { background-color: #151D2C; border: none; }
            QProgressBar {
                background-color: #0078d7; border: 2px solid #0056a1; border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #0056a1; border-radius: 5px;
            }
        """

    def show_loading(self): # Показывает экран загрузки
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_loading(self): # Скрывает экран загрузки
        self.hide()


class FirstStage(QMainWindow, FirstStageUi):
    def __init__(self):
        super().__init__()
        self.setupUi(self) # Настраивает интерфейс
        self.file_list = []
        self.current_image_id = None
        self.current_index = None
        self.previous_file_list = []
        self.loading_screen = LoadingScreen() # Создает экран загрузки

        self.setup_connections() # Настраивает соединения между элементами интерфейса и методами

    def setup_connections(self):  # Подключает кнопки к соответствующим методам
        self.open_button.clicked.connect(self.open_image)
        self.next_button.clicked.connect(self.get_next_image)
        self.previous_button.clicked.connect(self.get_previous_image)
        self.add_gaus.clicked.connect(self.add_gaus_func)
        self.add_eroz.clicked.connect(self.add_eroz_func)
        self.add_dilatation.clicked.connect(self.add_dilatation_func)
        self.add_bilat.clicked.connect(self.add_bilat_func)
        self.unstage_parametrs.clicked.connect(self.unstage_parametrs_func)
        self.save_button.clicked.connect(self.save_button_func)

    def open_image(self): # Открывает диалог для выбора изображения и загружает его
        self.loading_screen.show_loading()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "*.pkl")
        if fileName:
            with open(Path(fileName), 'rb') as f:
                data = pickle.load(f)

            response = requests.post("http://localhost:8000/sirius/files/save_file", json=data.tolist())
            self.file_list = response.json()
            self.current_image_id = self.file_list[0]
            self.current_index = 0
            self.open_api_image()
        self.loading_screen.hide_loading()

    def get_next_image(self): # Переходит к следующему изображени
        self.change_image(1)

    def get_previous_image(self): # Переходит к предыдущему изображению
        self.change_image(-1)

    def change_image(self, direction): # Изменяет текущее изображение в зависимости от направления
        self.loading_screen.show_loading()
        if self.current_index is None:
            return

        new_index = self.current_index + direction
        if 0 <= new_index < len(self.file_list):
            self.current_index = new_index
            self.current_image_id = self.file_list[self.current_index]
            self.open_api_image()
        self.loading_screen.hide_loading()

    def open_api_image(self): # Загружает изображение из API и отображает его
        self.loading_screen.show_loading()
        if not self.current_image_id:
            return
        self.image_name.setText(self.current_image_id)

        image_array = requests.get("http://localhost:8000/sirius/files/get_file",
                                   params={"file_id": self.current_image_id})
        arr = np.array(image_array.json())
        img = ImageQt(Image.fromarray(arr.astype(np.uint8)))
        self.current_image.setPixmap(QPixmap.fromImage(img))

        if self.previous_file_list:
            self.load_previous_image()
        else:
            self.previous_image.clear()
        self.loading_screen.hide_loading()

    def load_previous_image(self): # Загружает и отображает предыдущее изображение
        image_array = requests.get("http://localhost:8000/sirius/files/get_file",
                                   params={"file_id": self.previous_file_list[self.current_index]})
        arr = np.array(image_array.json())
        img = ImageQt(Image.fromarray(arr.astype(np.uint8)))
        self.previous_image.setPixmap(QPixmap.fromImage(img))

    def add_gaus_func(self): # Применяет метод Гаусса к изображению
        self.apply_method("gaus", {
            "gaus_core_x": self.gaus_core_x.text(),
            "gaus_core_y": self.gaus_core_y.text(),
            "gaus_sigma_x": self.gaus_sigma_x.text(),
            "gaus_sigma_y": self.gaus_sigma_y.text()
        })

    def add_eroz_func(self): # Применяет метод эрозии к изображению
        self.apply_method("erode", {
            "eroz_x": self.eroz_x.text(),
            "eroz_y": self.eroz_y.text(),
            "eroz_iteration": self.eroz_iteration.text()
        })

    def add_dilatation_func(self): # Применяет метод дилатации к изображению
        self.apply_method("dilatation", {
            "dilatation_x": self.dilatation_x.text(),
            "dilatation_y": self.dilatation_y.text(),
            "dilatation_iteration": self.dilatation_iteration.text()
        })

    def add_bilat_func(self): # Применяет метод билинейной фильтрации к изображению
        self.apply_method("bilat", {
            "bilat_d": self.bilat_d.text(),
            "bilat_color": self.bilat_color.text(),
            "bilat_coord": self.bilat_coord.text()
        })

    def apply_method(self, method, meta): # Применяет указанный метод к изображению с заданными параметрами
        self.previous_file_list = self.file_list
        self.loading_screen.show_loading()
        self.file_list = requests.get(
            "http://localhost:8000/sirius/files/add_method",
            params={"files_id": self.file_list, "method": method},
            json=meta
        ).json()

        self.current_image_id = self.file_list[self.current_index]
        self.open_api_image()
        self.loading_screen.hide_loading()

    def unstage_parametrs_func(self):  # Восстанавливает параметры предыдущего состояния
        self.loading_screen.show_loading()
        if self.previous_file_list:
            self.file_list = self.previous_file_list
            self.current_image_id = self.file_list[self.current_index]
            self.previous_file_list = requests.get(
                "http://localhost:8000/sirius/files/previous_file_list",
                params={"files_id": self.previous_file_list}
            ).json()

        self.open_api_image()
        self.loading_screen.hide_loading()

    def save_button_func(self): # Сохраняет текущее состояние изображения
        self.loading_screen.show_loading()
        if self.current_image_id:
            response = requests.get(
                "http://localhost:8000/sirius/files/save_files",
                params={"files_id": self.file_list}
            )
            if response.status_code == 200:
                self.clear_current_image()
                QTimer.singleShot(1500, self.show_action_dialog)
        self.loading_screen.hide_loading()

    def clear_current_image(self): # Очищает текущее изображение и сбрасывает состояние
        self.current_image.clear()
        self.previous_image.clear()
        self.image_name.clear()
        self.file_list = []
        self.current_image_id = None
        self.current_index = None
        self.previous_file_list = []

    def show_action_dialog(self): # Показывает диалог для выбора дальнейших действи
        action_dialog = ActionDialog()
        action_dialog.action_selected.connect(self.handle_action_selection)
        action_dialog.exec()

    def handle_action_selection(self, action): # Обрабатывает выбор действия из диалога
        main_app = self.get_main_app()
        if action == "manual":
            main_app.tab_widget.setCurrentIndex(1)
        elif action == "automatic":
            main_app.tab_widget.setCurrentIndex(2)

    def get_main_app(self): # Получает основной экземпляр приложения
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, MainApp):
                return widget
        return None


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tab_widget = QTabWidget() # Создает виджет вкладок
        self.setCentralWidget(self.tab_widget) # Устанавливает виджет вкладок как центральный
        self.set_styles()
        self.first_stage = FirstStage() # Создает экземпляр первого этапа
        self.markup_window = MarkupWindow() # Создает экземпляр окна разметки
        self.detect_window = DetectWindow() # Создает экземпляр окна распознавания

        # Добавляет вкладки в виджет

        self.tab_widget.addTab(self.first_stage, "Преобразование")
        self.tab_widget.addTab(self.markup_window, "Разметка")
        self.tab_widget.addTab(self.detect_window, "Распознавание")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.setWindowTitle("Image Annotation Tool")
        self.resize(1600, 800)
        self.setMinimumSize(1500, 300)
        self.loading_screen = LoadingScreen()

    def set_styles(self): # Устанавливает стили для вкладок и основного окна
        self.tab_widget.setStyleSheet(self.get_tab_styles())
        self.setStyleSheet(self.get_main_window_styles())

    def load_uids(self): # Загружает список UID изображений для разметки
        try:
            response = requests.get("http://localhost:8000/sirius/files/get_file_list")
            if response.status_code == 200:
                self.markup_window.uids = response.json()
                self.markup_window.update_uid_combobox()
                if self.markup_window.uids:
                    self.markup_window.current_index = 0
                    self.markup_window.get_image_by_uid(self.markup_window.uids[self.markup_window.current_index])
                else:
                    self.markup_window.editable_image_label.clear_markings()
                    logging.info("Список UID пуст, изображение не загружено.")
            else:
                logging.error("Ошибка при получении списка UID: %s", response.text)
        except Exception as e:
            logging.error("Ошибка при отправке запроса на получение списка UID: %s", e)
        finally:
            self.loading_screen.hide_loading()

    def on_tab_changed(self, index): # Обрабатывает изменение активной вкладки
        try:
            if index == 0:
                self.resize(1600, 800)
            elif index == 1:
                self.resize(Config.WINDOW_GEOMETRY[2], Config.WINDOW_GEOMETRY[3])
                self.loading_screen.show_loading()
                QTimer.singleShot(100, self.load_uids)
            elif index == 2:
                self.loading_screen.show_loading()
                self.resize(1600, 450)
                QTimer.singleShot(100, self.load_images_for_detection)
        except Exception as e:
            logging.error("Ошибка при переключении на вкладку: %s", e)

    def load_images_for_detection(self): # Загружает изображения для распознавания
        try:
            response = requests.get("http://localhost:8000/sirius/files/get_file_list")
            if response.status_code == 200:
                image_list = response.json()
                self.detect_window.load_image_list(image_list)
            else:
                logging.error("Ошибка при получении списка изображений: %s", response.text)
        except Exception as e:
            logging.error("Ошибка при отправке запроса на получение списка изображений: %s", e)
        finally:
            self.loading_screen.hide_loading()

    def get_tab_styles(self): # Возвращает стили для вкладок
        return """
            QTabWidget { background-color: #151D2C; border: none; }
            QTabBar { background-color: #0078d7; padding: 5px; border: none; }
            QTabBar::tab {
                background: #0078d7; color: white; padding: 5px; border: none;
            }
            QTabBar::tab:selected { background: #0056a1; color: white; }
            QTabBar::tab:!selected { margin-right: 1px; }
            QTabBar::tab:hover { background: #0056a1; }
        """

    def get_main_window_styles(self): # Возвращает стили для основного окна
        return """
            QMainWindow { background-color: #151D2C; border: none; }
            QWidget { background-color: #151D2C; border: none; }
        """


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)  # Создает экземпляр приложения

    auth_dialog = AuthDialog()  # Создает диалог авторизации
    if auth_dialog.exec() == QDialog.DialogCode.Accepted:  # Если авторизация успешна
        main_window = MainApp()  # Создает основной экземпляр приложения
        main_window.show()  # Показывает основное окно
        sys.exit(app.exec())  # Запускает главный цикл приложения
    else:
        sys.exit()  # Выходит из приложения