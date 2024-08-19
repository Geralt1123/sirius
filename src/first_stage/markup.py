import json
import logging
import pickle
import sys
import requests

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage, QIcon, QPen
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, \
    QFileDialog, QComboBox

from config_ui import Config

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),  # Запись логов в файл
                        logging.StreamHandler()  # Вывод логов в консоль
                    ])


class ImageLabel(QLabel):
    def __init__(self, editable=False):
        super().__init__()
        self.setMouseTracking(True)
        self.start_point = None
        self.end_point = None
        self.offset_x = 0  # Смещение по оси X
        self.image = QPixmap()  # Здесь будет храниться изображение
        self.markings = []  # Список для хранения разметок
        self.removed_markings = []  # Список для хранения удаленных разметок
        self.current_class = None  # Текущий выбранный класс
        self.current_color = QColor(255, 0, 0)  # Цвет разметки по умолчанию на красный
        self.fragment_width = 1024  # Ширина фрагмента
        self.fragment_height = 128  # Высота фрагмента
        self.fragment_index = 0  # Индекс текущего фрагмента
        self.image_data = None  # Полное изображение в виде numpy массива
        self.editable = editable  # Флаг для редактируемого слоя

        # # Устанавливаем фиксированный размер для ImageLabel
        # self.setFixedSize(self.fragment_width, self.fragment_height)

    def set_image(self, pixmap):
        self.image = pixmap
        self.offset_x = 0
        self.update()

    def load_image_from_pkl(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                self.image_data = pickle.load(f)

            if isinstance(self.image_data, np.ndarray):
                if self.image_data.dtype == np.float32 or self.image_data.dtype == np.float64:
                    self.image_data = (self.image_data * 255).astype(np.uint8)

                self.setFixedHeight(128)
                self.display_fragment()
                logging.debug("Изображение загружено из файла: %s", file_path)
            else:
                raise ValueError("Данные в файле не являются numpy массивом.")

        except Exception as e:
            logging.error("Ошибка при загрузке изображения: %s", e)

    def display_fragment(self):
        start_x = self.fragment_index * self.fragment_width
        end_x = start_x + self.fragment_width

        if end_x > self.image_data.shape[1]:
            end_x = self.image_data.shape[1]

        fragment = self.image_data[:, start_x:end_x]

        if len(fragment.shape) == 2:
            rgb_image = cv2.cvtColor(fragment, cv2.COLOR_GRAY2RGB)
        else:
            rgb_image = fragment

        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(q_image)
        self.set_image(pixmap)

        # Обновляем отображение разметки для текущего фрагмента
        self.update()

    def shift_image(self, delta_x):
        # Изменяем индекс фрагмента
        new_index = self.fragment_index + (delta_x // self.fragment_width)
        if new_index < 0:
            new_index = 0
        elif new_index * self.fragment_width >= self.image_data.shape[1]:
            new_index = (self.image_data.shape[1] // self.fragment_width) - 1

        if new_index != self.fragment_index:
            self.fragment_index = new_index
            self.display_fragment()  # Отображаем новый фрагмент

    def mousePressEvent(self, event):
        if self.editable and event.button() == Qt.MouseButton.LeftButton and self.current_class is not None:
            real_x = event.pos().x() - self.offset_x
            real_y = event.pos().y()
            self.start_point = (real_x, real_y)
            logging.debug("Начальная точка: %s", self.start_point)

    def mouseMoveEvent(self, event):
        if self.editable and self.start_point is not None:
            real_x = event.pos().x() - self.offset_x
            real_y = event.pos().y()
            self.end_point = (real_x, real_y)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.editable and event.button() == Qt.MouseButton.LeftButton and self.start_point is not None:
            real_x = event.pos().x() - self.offset_x
            real_y = event.pos().y()
            self.end_point = (real_x, real_y)

            if (0 <= real_x < self.image.width()) and (0 <= real_y < self.image.height()):
                self.markings.append({
                    "class": self.current_class,
                    "start": {"x": self.start_point[0], "y": self.start_point[1]},
                    "end": {"x": self.end_point[0], "y": self.end_point[1]},
                    "fragment_id": self.fragment_index
                })
                logging.debug("Добавлена разметка: %s", self.markings[-1])
            else:
                logging.warning("Координаты разметки выходят за пределы изображения: (%d, %d)", real_x, real_y)

            self.start_point = None
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.image.isNull():
            # Масштабируем изображение с учетом рамки
            scaled_image = self.image.scaled(self.width() - 13, self.height() - 20,
                                             Qt.AspectRatioMode.KeepAspectRatioByExpanding)

            # Получаем размеры рамки
            frame_rect = self.rect()

            # Вычисляем центрирование изображения в рамке
            x_offset = (frame_rect.width() - scaled_image.width()) // 2
            y_offset = (frame_rect.height() - scaled_image.height()) // 2

            # Рисуем изображение с учетом смещения
            painter = QPainter(self)
            painter.drawPixmap(x_offset, y_offset, scaled_image)

            # Рисуем разметку и другие элементы, как и раньше
            self.draw_markings(painter)

    def draw_markings(self, painter):
        # Логика рисования разметки
        for marking in self.markings:
            if marking["fragment_id"] == self.fragment_index:
                start_x = marking["start"]["x"]
                start_y = marking["start"]["y"]
                end_x = marking["end"]["x"]
                end_y = marking["end"]["y"]

                # Устанавливаем цвет с альфа-каналом для полупрозрачности
                color = QColor(255, 0, 0)
                color.setAlpha(50)

                painter.setBrush(color)
                painter.drawRect(start_x, start_y, end_x - start_x, end_y - start_y)

                # Рисуем контур
                painter.setPen(QPen(QColor(255, 0, 0), 3))
                painter.drawRect(start_x, start_y, end_x - start_x, end_y - start_y)

        if self.start_point and self.end_point:
            real_start_x, real_start_y = self.start_point
            real_end_x, real_end_y = self.end_point
            current_color = QColor(255, 0, 0, 100)  # Полупрозрачный красный для текущей разметки
            painter.setBrush(current_color)
            painter.drawRect(real_start_x, real_start_y,
                             real_end_x - real_start_x, real_end_y - real_start_y)

            # Рисуем контур с увеличенной толщиной
            painter.setPen(QPen(QColor(255, 0, 0), 3))  # Красный цвет и толщина контура
            painter.drawRect(real_start_x, real_start_y,
                             real_end_x - real_start_x, real_end_y - real_start_y)

    def get_markings_json(self):
        # Добавляем идентификатор фрагмента в разметку
        for marking in self.markings:
            marking["fragment_id"] = self.fragment_index
        return json.dumps(self.markings, ensure_ascii=False, indent=4)

    def remove_last_marking(self):
        if self.markings:
            removed = self.markings.pop()
            self.removed_markings.append(removed)  # Сохраняем удаленную разметку
            logging.debug("Удалена последняя разметка: %s", removed)
            self.update()

    def restore_last_marking(self):
        if self.removed_markings:
            restored = self.removed_markings.pop()
            self.markings.append(restored)  # Восстанавливаем разметку
            logging.debug("Восстановлена последняя разметка: %s", restored)
            self.update()

    def set_current_class(self, class_name):
        self.current_class = class_name
        logging.debug("Выбран класс разметки: %s", class_name)

    def clear_markings(self):
        """Очистить все разметки."""
        self.markings.clear()
        self.removed_markings.clear()
        logging.debug("Все разметки очищены.")
        self.update()

    def load_image_from_array(self, image_array):
        """Загружает изображение из numpy массива."""
        self.image_data = image_array
        self.fragment_index = 0  # Сброс индекса фрагмента
        self.display_fragment()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setStyleSheet(self.get_styles())
        # Список UID
        self.uids = [
            "07ba511d-65ec-4c75-9d7d-5495fcb31948",
            "0aff0357-c88c-43b8-98d5-4be94f3bdd98",
            "1536ed9f-3584-4a8c-8c65-4edd60bd1b3b",
            "2b6b7e2a-8d26-48b6-b0c7-e24d5b6f3138"
        ]
        self.current_index = 0  # Индекс текущего UID
        self.load_initial_image()  # Загружаем первое изображение

    def initUI(self):
        self.setWindowTitle(Config.WINDOW_TITLE)
        self.setGeometry(*Config.WINDOW_GEOMETRY)
        self.setWindowIcon(QIcon(Config.ICON_PATH))
        self.create_layout()

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
            }}

            ImageLabel {{
                border: 5px solid #0078d7;  /* Цвет и толщина рамки */
                border-radius: 8px;  /* Закругление углов рамки */
                padding: 5px;  /* Отступы внутри рамки */
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

            QComboBox {{
                appearance: none;
                border: none;
                border-radius: {Config.DROPDOWN_BORDER_RADIUS}px;
                padding: {Config.DROPDOWN_ITEMLIST_PADDING_VERTICAL}px {Config.DROPDOWN_ITEMLIST_PADDING_HORIZONTAL}px;
                background-color: {Config.COMBOBOX_BACKGROUND_COLOR};
                color: #ffffff;
                padding-right: 30px;
                font-size: {Config.COMBOBOX_FONT_SIZE}px;
            }}

            QComboBox::drop-down {{
                border: none;
                border-radius: {Config.DROPDOWN_BORDER_RADIUS}px;
                width: 30px;
            }}

            QComboBox::down-arrow {{
                image: url("{Config.ARROW_COMBOBOX_ICON}");
            }}

            QComboBox:hover {{
                background-color: {Config.COMBOBOX_HOVER_COLOR};
                border: 1px solid {Config.HOVER_BORDER_COLOR};
            }}

            QComboBox QAbstractItemView {{
                background-color: {Config.DROPDOWN_PRIMARY_BG_COLOR};
                color: #ffffff;
                border-radius: {Config.DROPDOWN_ITEM_BORDER_RADIUS}px;
                border: 1px solid {Config.HOVER_BORDER_COLOR};
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                padding: {Config.DROPDOWN_ITEM_PADDING_VERTICAL}px {Config.DROPDOWN_ITEM_PADDING_HORIZONTAL}px;
                border: none;
                border-radius: {Config.DROPDOWN_ITEM_BORDER_RADIUS}px;
                font-size: {Config.COMBOBOX_FONT_SIZE}px;
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: {Config.DROPDOWN_PRIMARY_ITEM_BG_COLOR_SELECTED_DEFAULT};
                border: none;
                border-radius: {Config.DROPDOWN_ITEM_BORDER_RADIUS}px;
            }}
        """

    def create_layout(self):
        main_layout = QHBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Левая панель
        left_panel = QVBoxLayout()
        main_layout.addLayout(left_panel)

        # Редактируемое изображение
        self.editable_image_label = ImageLabel(editable=True)
        left_panel.addWidget(self.editable_image_label)

        # Кнопки управления изображениями
        self.create_image_control_buttons(left_panel)

        # Правая панель
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel)

        # Выпадающий список для выбора класса
        self.class_combo_box = QComboBox()
        self.class_combo_box.addItems([
            "Дефект 1: Коррозия",
            "Дефект 2: Трещины",
            "Дефект 3: Увеличение толщины",
            "Дефект 4: Изменение цвета",
            "Дефект 5: Утечки"
        ])
        right_panel.addWidget(self.class_combo_box)

        # Кнопки "Сохранить", "Отметить", "Сбросить разметку"
        self.create_action_buttons(right_panel)

    def create_image_control_buttons(self, left_panel):
        button_layout = QHBoxLayout()

        load_button = QPushButton("Загрузить изображение")
        left_button = QPushButton("Стрелка влево")
        right_button = QPushButton("Стрелка вправо")
        remove_button = QPushButton("Удалить последнюю разметку")
        restore_button = QPushButton("Восстановить последнюю разметку")

        button_layout.addWidget(load_button)
        button_layout.addWidget(left_button)
        button_layout.addWidget(right_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(restore_button)

        left_panel.addLayout(button_layout)

        # Подключаем действия кнопок
        load_button.clicked.connect(self.open_image)  # Загрузка изображения
        left_button.clicked.connect(lambda: self.shift_image(-1024))  # Смещение влево
        right_button.clicked.connect(lambda: self.shift_image(1024))  # Смещение вправо
        remove_button.clicked.connect(self.remove_last_marking)
        restore_button.clicked.connect(self.restore_last_marking)

    def create_action_buttons(self, right_panel):
        button_layout = QVBoxLayout()

        mark_button = QPushButton("Отметить")
        save_button = QPushButton("Сохранить")
        reset_button = QPushButton("Сбросить разметку")  # Кнопка для сброса разметки

        button_layout.addWidget(mark_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(reset_button)  # Добавляем кнопку сброса разметки

        right_panel.addLayout(button_layout)

        # Подключаем действия кнопок
        mark_button.clicked.connect(self.mark_image)
        save_button.clicked.connect(self.save_image)
        reset_button.clicked.connect(self.reset_markings)  # Подключаем действие сброса разметки

        # Подключаем действие выбора класса
        self.class_combo_box.currentTextChanged.connect(self.set_class_from_combobox)

    def open_image(self):
        try:
            fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "*.pkl")
            if fileName:
                self.editable_image_label.load_image_from_pkl(fileName)  # Загружаем в оба окна
        except Exception as e:
            logging.error("Ошибка при открытии изображения: %s", e)

    def load_initial_image(self):
        """Загружает первое изображение при инициализации."""
        self.get_image_by_uid(self.uids[self.current_index])

    def get_image_by_uid(self, uid):
        """Отправляет GET-запрос для получения изображения по UID."""
        try:
            response = requests.get(f"http://localhost:8000/sirius/files/get_file?file_id={uid}")
            if response.status_code == 200:
                # Преобразуем ответ в numpy массив с правильным типом данных
                image_array = np.array(response.json(), dtype=np.uint8)  # или np.float32 в зависимости от данных
                self.editable_image_label.load_image_from_array(image_array)
                logging.debug("Загружено изображение с file_id: %s", uid)
            else:
                logging.error("Ошибка при получении изображения: %s", response.text)
        except Exception as e:
            logging.error("Ошибка при отправке запроса на получение изображения: %s", e)

    def shift_image(self, delta_x):
        if delta_x > 0:  # Стрелка вправо
            self.get_next_file()
        else:  # Стрелка влево
            self.get_previous_file()

    def get_next_file(self):
        """Отправляет GET-запрос для получения следующего файла."""
        if self.current_index < len(self.uids) - 1:
            self.current_index += 1
            self.get_image_by_uid(self.uids[self.current_index])
        else:
            logging.warning("Нет следующего файла.")

    def get_previous_file(self):
        """Отправляет GET-запрос для получения предыдущего файла."""
        if self.current_index > 0:
            self.current_index -= 1
            self.get_image_by_uid(self.uids[self.current_index])
        else:
            logging.warning("Нет предыдущего файла.")


    def mark_image(self):
        # Логика для отметки на изображении
        logging.debug("Отметка на изображении")

    def save_image(self):
        # Логика для сохранения разметки
        json_output = self.editable_image_label.get_markings_json()
        logging.debug("Сохранение разметки в формате JSON: %s", json_output)

    def remove_last_marking(self):
        self.editable_image_label.remove_last_marking()

    def restore_last_marking(self):
        self.editable_image_label.restore_last_marking()

    def reset_markings(self):
        """Сбросить всю разметку на редактируемом изображении."""
        self.editable_image_label.clear_markings()  # Очищаем разметку

    def set_class_from_combobox(self, class_name):
        # Устанавливаем текущий класс из выпадающего списка
        self.editable_image_label.set_current_class(class_name)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error("Необработанное исключение: %s", e)