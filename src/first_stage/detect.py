import logging
import cv2
import numpy as np
import requests
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QFrame, QFileDialog, QHBoxLayout, \
    QSpacerItem, QSizePolicy, QMessageBox, QTextEdit


class ImageLoader(QThread):
    image_loaded = pyqtSignal(np.ndarray, int)  # Сигнал для передачи загруженного изображения и индекса

    def __init__(self, file_id, endpoint):
        super().__init__()
        self.file_id = file_id
        self.endpoint = endpoint

    def run(self):
        try:
            # Отправка запроса на сервер для получения изображения
            response = requests.post(self.endpoint, params={"file_id": self.file_id})
            response.raise_for_status()  # Проверка на ошибки HTTP

            # Предполагаем, что сервер возвращает массив в формате JSON
            arr = np.array(response.json())

            # Проверка, является ли полученный массив NumPy
            if isinstance(arr, list):
                arr = np.array(arr)  # Преобразование списка в массив NumPy

            # Проверка на цветное изображение
            if arr.ndim == 3 and arr.shape[2] in [3, 4]:  # 3 канала (RGB) или 4 канала (RGBA)
                if arr.dtype == np.float32 or arr.dtype == np.float64:
                    arr = (arr * 255).astype(np.uint8)  # Преобразование в uint8
                elif arr.dtype != np.uint8:
                    arr = arr.astype(np.uint8)  # Преобразование в uint8, если это не float

                # Преобразование в RGB, если это необходимо
                if arr.shape[2] == 4:  # RGBA
                    arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)

                # Отправляем сигнал с загруженным изображением
                self.image_loaded.emit(arr, 1)  # Индекс 1 для первого изображения
            else:
                raise ValueError("Полученный массив не является цветным изображением.")

        except requests.exceptions.RequestException as e:
            logging.error("Ошибка при запросе к серверу: %s", e)
        except ValueError as e:
            logging.error("Ошибка при обработке данных: %s", e)
        except Exception as e:
            logging.error("Неизвестная ошибка: %s", e)


class DetectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Выпадающий список для выбора изображений
        self.image_selector = QComboBox()
        self.image_selector.setPlaceholderText("Выберите изображение")
        layout.addWidget(self.image_selector)

        # Создаем горизонтальный layout для кнопок
        button_layout = QHBoxLayout()

        # Кнопка для распознавания
        self.recognize_button = QPushButton("Распознать")
        button_layout.addWidget(self.recognize_button)

        # Кнопка для сохранения изображения
        self.save_button = QPushButton("Сохранить результат")
        button_layout.addWidget(self.save_button)

        # Добавляем кнопки в основной layout
        layout.addLayout(button_layout)

        # Создаем горизонтальный layout для размещения текстовых полей и области изображений
        main_layout = QHBoxLayout()

        # Создаем текстовые поля
        self.output_log_left = QTextEdit()
        self.output_log_left.setReadOnly(True)
        self.output_log_left.setPlaceholderText("Результаты распознаваниия")
        self.output_log_left.setStyleSheet(self.get_styles())  # Применяем стили

        self.output_log_right = QTextEdit()
        self.output_log_right.setReadOnly(True)
        self.output_log_right.setPlaceholderText("Результаты распознаваниия")
        self.output_log_right.setStyleSheet(self.get_styles())  # Применяем стили

        # Добавляем текстовые поля в левый и правый layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.output_log_left)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.output_log_right)

        # Область для отображения изображений
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet("border: 5px solid #0078d7; border-radius: 1px;")
        self.image_frame.setMinimumSize(QSize(1024, 128))  # Устанавливаем минимальные размеры рамки
        self.image_frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Устанавливаем фиксированный размер

        # Создаем метки для изображений
        self.image_label_1 = QLabel()
        self.image_label_1.setMinimumSize(QSize(1024, 128))  # Устанавливаем минимальные размеры для метки
        self.image_label_1.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем изображение

        self.image_label_2 = QLabel()
        self.image_label_2.setMinimumSize(QSize(1024, 128))  # Устанавливаем минимальные размеры для метки
        self.image_label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем изображение

        # Создаем вертикальный layout для изображений
        self.image_frame_layout = QVBoxLayout(self.image_frame)
        self.image_frame_layout.addWidget(self.image_label_1)
        self.image_frame_layout.addWidget(self.image_label_2)
        self.image_frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Центрируем содержимое рамки

        # Добавляем текстовые поля и область изображений в общий layout
        main_layout.addLayout(left_layout)  # Левый layout
        main_layout.addWidget(self.image_frame)  # Область изображений
        main_layout.addLayout(right_layout)  # Правый layout

        layout.addLayout(main_layout)  # Добавляем общий layout в основной layout

        self.setLayout(layout)

        # Подключаем кнопки к функциям
        self.recognize_button.clicked.connect(self.recognize_image)
        self.save_button.clicked.connect(self.save_image)

        # Применяем стили
        self.setStyleSheet(self.get_styles())

        # Загрузка данных в текстовые поля
        self.load_text_data()

    def get_styles(self):
        return """
            QWidget {
                background-color: #151D2C;  /* Цвет фона для окна распознавания */
                color: white;  /* Цвет текста */
                font-family: Arial;  /* Шрифт по умолчанию */
            }

            QLabel {
                font-family: Arial;  /* Шрифт для заголовков */
                font-weight: bold;
                font-size: 14px;  /* Размер шрифта для названий полей ввода */
            }

            QPushButton {
                padding: 10px 20px;
                height: 30px;
                background-color: #0078d7;  /* Цвет фона для кнопки */
                color: #ffffff;  /* Цвет текста на кнопке */
                border: none;
                border-radius: 8px;  /* Закругление углов */
                cursor: pointer;
                font-family: Arial;  /* Шрифт для кнопок */
                font-weight: bold;
                font-size: 14px;  /* Размер шрифта для кнопок */
                transition: background-color 0.3s;
            }

            QPushButton:hover {
                background-color: #0056a1;  /* Цвет фона при наведении на кнопку */
            }

            QComboBox {
                background-color: #0078d7;  /* Цвет фона для выпадающего списка */
                color: white;  /* Цвет текста в выпадающем списке */
                border: 1px solid #0056a1;  /* Цвет границы */
                border-radius: 5px;  /* Закругление углов */
                padding: 5px;  /* Отступы внутри выпадающего списка */
                font-size: 14px;  /* Размер шрифта для выпадающего списка */
            }

            QComboBox::drop-down {
                border: none;  /* Убираем границу для стрелки */
                width: 30px;  /* Ширина стрелки */
            }

            QComboBox::down-arrow {
                image: url("path_to_arrow_icon.png");  /* Путь к иконке стрелки */
            }

            QComboBox QAbstractItemView {
                background-color: #151D2C;  /* Цвет фона для выпадающего списка */
                color: white;  /* Цвет текста в выпадающем списке */
                border: 1px solid #0056a1;  /* Цвет границы */
                outline: none;
            }

            QComboBox QAbstractItemView::item {
                padding: 5px;  /* Отступы внутри элементов выпадающего списка */
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #0056a1;  /* Цвет фона для выбранного элемента */
            }

            QTextEdit {
                background-color: #151D2C;  /* Цвет фона для текстового поля */
                color: white;  /* Цвет текста в текстовом поле */
                border: 1px solid #0056a1;  /* Цвет границы */
                border-radius: 5px;  /* Закругление углов */
                padding: 5px;  /* Отступы внутри текстового поля */
                font-size: 14px;  /* Размер шрифта для текстового поля */
            }
        """

    def load_text_data(self):
        """Загружает текстовые данные из эндпоинта."""
        try:
            response = requests.get("http://localhost:8000/sirius/files/text")
            response.raise_for_status()  # Проверка на ошибки HTTP
            text_data = response.json()  # Предполагаем, что сервер возвращает данные в формате JSON

            # Заполнение текстовых полей
            self.output_log_left.setPlainText(text_data.get("left", ""))
            self.output_log_right.setPlainText(text_data.get("right", ""))
        except requests.exceptions.RequestException as e:
            logging.error("Ошибка при запросе к серверу: %s", e)
        except Exception as e:
            logging.error("Неизвестная ошибка: %s", e)

    def load_image_list(self, image_list):
        """Загружает список изображений в выпадающий список."""
        self.image_selector.clear()
        self.image_selector.addItems(image_list)

    def recognize_image(self):
        """Обрабатывает распознавание изображения."""
        selected_image_id = self.image_selector.currentText()
        if selected_image_id:
            # Создаем потоки для загрузки изображений
            self.load_image_1 = ImageLoader(selected_image_id, "http://localhost:8000/sirius/files/predict_file")
            self.load_image_2 = ImageLoader(selected_image_id, "http://localhost:8000/sirius/files/predict_file")

            # Подключаем сигнал к слоту для обработки загруженного изображения
            self.load_image_1.image_loaded.connect(self.display_image)
            self.load_image_2.image_loaded.connect(self.display_image)

            # # Заполнение текстовых полей
            # self.output_log_left.setPlainText(text_data.get("left", ""))
            # self.output_log_right.setPlainText(text_data.get("right", ""))

            # Запускаем потоки
            self.load_image_1.start()
            self.load_image_2.start()

    def display_image(self, arr):
        """Отображает изображение в соответствующем QLabel."""
        # Получаем размеры изображения
        height, width, channel = arr.shape
        bytes_per_line = 3 * width

        # Создание QImage из массива
        q_image = QImage(arr.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        # Создание QPixmap из QImage
        pixmap = QPixmap.fromImage(q_image)

        # Устанавливаем фиксированные размеры для отображения
        pixmap = pixmap.scaled(1024, 128, Qt.AspectRatioMode.KeepAspectRatio)  # Масштабируем изображение

        self.image_label_1.setPixmap(pixmap)  # Устанавливаем первое изображение
        self.image_label_2.setPixmap(pixmap)  # Устанавливаем второе изображение

    def show_error_message(self, message):
        """Отображает модальное окно с сообщением об ошибке."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle("Ошибка")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Применяем стили
        msg_box.setStyleSheet(self.get_styles())

        msg_box.exec()

    def save_image(self):
        """Сохраняет текущее изображение в формате PNG с соответствующими именами."""
        selected_image_id = self.image_selector.currentText()

        if selected_image_id:
            # Сохраняем первое изображение (Конструктивные элементы)
            initial_file_name_1 = f"{selected_image_id}_Конструктивные_элементы.png"
            file_name_1, _ = QFileDialog.getSaveFileName(self,
                                                         f"Сохранить изображение {selected_image_id} - Конструктивные элементы",
                                                         initial_file_name_1,
                                                         "Images (*.png);;All Files (*)")

            if file_name_1:
                try:
                    # Получаем текущее изображение и сохраняем его
                    current_pixmap_1 = self.image_label_1.pixmap()
                    if current_pixmap_1 is not None:
                        current_pixmap_1.save(file_name_1)
                    else:
                        self.show_error_message("Нет изображения для сохранения в 'Конструктивные элементы'.")
                except Exception as e:
                    self.show_error_message(f"Ошибка при сохранении изображения 'Конструктивные элементы': {str(e)}")

            # Сохраняем второе изображение (Дефекты)
            initial_file_name_2 = f"{selected_image_id}_Дефекты.png"
            file_name_2, _ = QFileDialog.getSaveFileName(self,
                                                         f"Сохранить изображение {selected_image_id} - Дефекты",
                                                         initial_file_name_2,
                                                         "Images (*.png);;All Files (*)")

            if file_name_2:
                try:
                    # Получаем текущее изображение и сохраняем его
                    current_pixmap_2 = self.image_label_2.pixmap()
                    if current_pixmap_2 is not None:
                        current_pixmap_2.save(file_name_2)
                    else:
                        self.show_error_message("Нет изображения для сохранения в 'Дефекты'.")
                except Exception as e:
                    self.show_error_message(f"Ошибка при сохранении изображения 'Дефекты': {str(e)}")
        else:
            self.show_error_message("Нет изображения для сохранения.")