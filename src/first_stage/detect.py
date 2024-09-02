from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QFrame, QFileDialog, QHBoxLayout
from PyQt6.QtGui import QPixmap
import requests
from PIL import Image
from PIL.ImageQt import ImageQt
import numpy as np

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

        # Область для отображения изображения
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet("border: 5px solid #0078d7; border-radius: 1px;")
        self.image_label = QLabel()
        self.image_frame_layout = QVBoxLayout(self.image_frame)
        self.image_frame_layout.addWidget(self.image_label)
        layout.addWidget(self.image_frame)

        self.setLayout(layout)

        # Подключаем кнопки к функциям
        self.recognize_button.clicked.connect(self.recognize_image)
        self.save_button.clicked.connect(self.save_image)

        # Применяем стили
        self.setStyleSheet(self.get_styles())

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
            }

            QComboBox QAbstractItemView::item {
                padding: 5px;  /* Отступы внутри элементов выпадающего списка */
            }

            QComboBox QAbstractItemView::item:selected {
                background-color: #0056a1;  /* Цвет фона для выбранного элемента */
            }
        """

    def load_image_list(self, image_list):
        """Загружает список изображений в выпадающий список."""
        self.image_selector.clear()
        self.image_selector.addItems(image_list)

    def recognize_image(self):
        """Обрабатывает распознавание изображения."""
        selected_image_id = self.image_selector.currentText()
        if selected_image_id:
            # Здесь вы можете добавить код для отправки запроса на сервер для распознавания
            response = requests.get(f"http://localhost:8000/sirius/files/get_file", params={"file_id": selected_image_id})
            if response.status_code == 200:
                arr = np.array(response.json())
                img = ImageQt(Image.fromarray(arr.astype(np.uint8)))
                self.image_label.setPixmap(QPixmap.fromImage(img))
            else:
                print("Ошибка при получении изображения:", response.text)

    def save_image(self):
        """Сохраняет текущее изображение."""
        if self.image_label.pixmap() is not None:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)
            if file_name:
                # Получаем текущее изображение и сохраняем его
                current_pixmap = self.image_label.pixmap()
                current_pixmap.save(file_name)
        else:
            print("Нет изображения для сохранения.")