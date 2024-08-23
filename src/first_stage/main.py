import logging
from pathlib import Path
import pickle
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QTabWidget, QWidget, QVBoxLayout
import requests
#from src.first_stage.first_stage import Ui_MainWindow as FirstStageUi
from docs.first_stage import Ui_MainWindow as FirstStageUi
from markup import MainWindow as MarkupWindow  # Импортируем класс из markup.py


class FirstStage(QMainWindow, FirstStageUi):
    file_list = []
    current_image_id = None
    current_index = None
    previous_file_list = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.open_button.clicked.connect(self.open_image)
        self.next_button.clicked.connect(self.get_next_image)
        self.previous_button.clicked.connect(self.get_previous_image)
        self.add_gaus.clicked.connect(self.add_gaus_func)
        self.add_eroz.clicked.connect(self.add_eroz_func)
        self.add_dilatation.clicked.connect(self.add_dilatation_func)
        self.add_bilat.clicked.connect(self.add_bilat_func)
        self.unstage_parametrs.clicked.connect(self.unstage_parametrs_func)
        self.save_button.clicked.connect(self.save_button_func)

    def open_image(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "*.pkl")
        if fileName:
            with open(Path(fileName), 'rb') as f:
                data = pickle.load(f)

        response = requests.post("http://localhost:8000/sirius/files/save_file", json=data.tolist())

        self.file_list = response.json()
        self.current_image_id = self.file_list[0]
        self.current_index = 0

        self.open_api_image()  # image form set image

    def get_next_image(self):
        if self.current_index is None:
            return None

        if self.current_index >= len(self.file_list) - 1:
            return None

        self.current_index += 1
        self.current_image_id = self.file_list[self.current_index]

        self.open_api_image()  # image form set image

    def get_previous_image(self):
        if self.current_index is None:
            return None

        if self.current_index == 0:
            return None

        self.current_index -= 1
        self.current_image_id = self.file_list[self.current_index]

        self.open_api_image()  # image form set image

    def open_api_image(self):
        """ Подтягивает необходимы для фото в форме данные"""
        if not self.current_image_id:
            return 0
        self.image_name.setText(self.current_image_id)

        image_array = requests.get("http://localhost:8000/sirius/files/get_file",
                                         params={"file_id": self.current_image_id})
        arr = np.array(image_array.json())
        img = ImageQt(Image.fromarray(arr.astype(np.uint8)))
        self.current_image.setPixmap(QPixmap.fromImage(img))

        if self.previous_file_list:
            image_array = requests.get("http://localhost:8000/sirius/files/get_file",
                                       params={"file_id": self.previous_file_list[self.current_index]})
            arr = np.array(image_array.json())
            img = ImageQt(Image.fromarray(arr.astype(np.uint8)))
            self.previous_image.setPixmap(QPixmap.fromImage(img))
        else:
            self.previous_image.clear()

    def add_gaus_func(self):
        """Применяет метод гауса"""
        meta = {"gaus_core_x": self.gaus_core_x.text(),
                "gaus_core_y": self.gaus_core_y.text(),
                "gaus_sigma_x": self.gaus_sigma_x.text(),
                "gaus_sigma_y": self.gaus_sigma_y.text()
                }

        self.previous_file_list = self.file_list

        self.file_list = requests.get(
            "http://localhost:8000/sirius/files/add_method",
            params={
                "files_id": self.file_list,
                "method": "gaus",
            },
            json=meta
        ).json()

        self.current_image_id = self.file_list[self.current_index]
        self.open_api_image()  # image form set image

    def add_eroz_func(self):
        """Применяет метод эрозии"""

        meta = {
            "eroz_x": self.eroz_x.text(),
            "eroz_y": self.eroz_y.text(),
            "eroz_iteration": self.eroz_iteration.text(),
        }

        self.previous_file_list = self.file_list

        self.file_list = requests.get(
            "http://localhost:8000/sirius/files/add_method",
            params={
                "files_id": self.file_list,
                "method": "erode",
            },
            json=meta
        ).json()

        self.current_image_id = self.file_list[self.current_index]
        self.open_api_image()  # image form set image

    def add_dilatation_func(self):
        """Применяет метод Дилатации"""

        meta = {
            "dilatation_x": self.dilatation_x.text(),
            "dilatation_y": self.dilatation_y.text(),
            "dilatation_iteration": self.dilatation_iteration.text(),
        }

        self.previous_file_list = self.file_list

        self.file_list = requests.get(
            "http://localhost:8000/sirius/files/add_method",
            params={
                "files_id": self.file_list,
                "method": "dilatation",
            },
            json=meta
        ).json()

        self.current_image_id = self.file_list[self.current_index]
        self.open_api_image()  # image form set image

    def add_bilat_func(self):
        """Применяет двусторонний фильтр"""

        meta = {
            "bilat_d": self.bilat_d.text(),
            "bilat_color": self.bilat_color.text(),
            "bilat_coord": self.bilat_coord.text(),
        }

        self.previous_file_list = self.file_list

        self.file_list = requests.get(
            "http://localhost:8000/sirius/files/add_method",
            params={
                "files_id": self.file_list,
                "method": "bilat",
            },
            json=meta
        ).json()

        self.current_image_id = self.file_list[self.current_index]
        self.open_api_image()  # image form set image

    def unstage_parametrs_func(self):
        if self.previous_file_list:
            self.file_list = self.previous_file_list
            self.current_image_id = self.file_list[self.current_index]
            self.previous_file_list = requests.get(
                "http://localhost:8000/sirius/files/previous_file_list",
                params={
                    "files_id": self.previous_file_list,
                }
            ).json()

        self.open_api_image()  # image form set image

    def save_button_func(self):
        if self.current_image_id:
            requests.get(
                "http://localhost:8000/sirius/files/save_files",
                params={
                    "files_id": self.file_list,
                }
            )
            self.current_image.clear()
            self.previous_image.clear()
            self.image_name.clear()
            self.file_list = []
            self.current_image_id = None
            self.current_index = None
            self.previous_file_list = []




class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Устанавливаем стиль для вкладок
        self.tab_widget.setStyleSheet(self.get_tab_styles())

        # Устанавливаем стиль для главного окна и центрального виджета
        self.setStyleSheet(self.get_main_window_styles())

        self.first_stage = FirstStage()
        self.markup_window = MarkupWindow()

        self.tab_widget.addTab(self.first_stage, "Первый этап")
        self.tab_widget.addTab(self.markup_window, "Разметка")

        self.tab_widget.currentChanged.connect(self.adjust_window_size)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)  # Подключаем обработчик

        self.setWindowTitle("Image Annotation Tool")
        self.resize(1600, 800)

    def load_uids(self):
        """Загружает список UID из API."""
        try:
            response = requests.get("http://localhost:8000/sirius/files/get_file_list")
            if response.status_code == 200:
                self.markup_window.uids = response.json()  # Обновляем список UID в разметке
                self.markup_window.update_uid_combobox()  # Обновляем выпадающий список UID
                if self.markup_window.uids:
                    self.markup_window.current_index = 0  # Сбрасываем индекс только если список не пустой
                    self.markup_window.get_image_by_uid(self.markup_window.uids[self.markup_window.current_index])
                else:
                    self.markup_window.editable_image_label.clear_markings()  # Очищаем разметку, если UID пустой
                    logging.info("Список UID пуст, изображение не загружено.")
            else:
                logging.error("Ошибка при получении списка UID: %s", response.text)
        except Exception as e:
            logging.error("Ошибка при отправке запроса на получение списка UID: %s", e)

    def on_tab_changed(self, index):
        """Обработчик изменения вкладки."""
        try:
            if index == 1:  # Если выбрана вкладка "Разметка"
                self.load_uids()  # Получаем список UID
        except Exception as e:
            logging.error("Ошибка при переключении на вкладку 'Разметка': %s", e)

    def get_tab_styles(self):
        return """
            QTabWidget {
                background-color: #151D2C;  /* Цвет фона для всего QTabWidget */
                border: none;
            }
            
            QTabBar {
                background-color: #0078d7;  /* Цвет фона для QTabBar */
                padding: 5px;  /* Отступы вокруг вкладок */
                border: none;  /* Убираем границу */
            }
            
            QTabBar::tab {
                background: #0078d7;  /* Цвет фона для вкладок */
                color: white;  /* Цвет текста на вкладках */
                padding: 5px;  /* Отступы внутри вкладок */
                border: none;  /* Граница вкладок */
            }

            QTabBar::tab:selected {
                background: #0056a1;  /* Цвет фона для выбранной вкладки */
                color: white;  /* Цвет текста для выбранной вкладки */
                border: none;
            }
            
            QTabBar::tab:!selected { 
                margin-right: 1px; 
            }

            QTabBar::tab:hover {
                background: #0056a1;  /* Цвет фона при наведении на вкладку */
                border: none;
            }
        """

    def get_main_window_styles(self):
        return """
            QMainWindow {
                background-color: #151D2C;  /* Цвет фона для главного окна */
                background: #151D2C;  /* Цвет фона для вкладок */
                border: none;
            }

            QWidget {
                background-color: #151D2C;  /* Цвет фона для центрального виджета */
                background: #151D2C;  /* Цвет фона для вкладок */
                border: none;
            }
        """

    def adjust_window_size(self, index):
        """Изменяет размер главного окна в зависимости от текущей вкладки."""
        current_widget = self.tab_widget.widget(index)
        if current_widget:
            size = current_widget.sizeHint()
            self.resize(size.width(), size.height())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())