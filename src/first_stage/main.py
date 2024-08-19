from pathlib import Path
import pickle
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt, QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QTabWidget, QWidget, QVBoxLayout
import requests
from src.first_stage.first_stage import Ui_MainWindow as FirstStageUi
from markup import MainWindow as MarkupWindow  # Импортируем класс из markup.py


class FirstStage(QMainWindow, FirstStageUi):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.open_button.clicked.connect(self.open_image)

    def open_image(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "*.pkl")
        if fileName:
            with open(Path(fileName), 'rb') as f:
                data = pickle.load(f)

            response = requests.post("http://localhost:8000/sirius/files/save_file", json=data.tolist())
            first_image_id = response.json()

            self.image_name.setText(first_image_id)
            first_image_array = requests.get("http://localhost:8000/sirius/files/get_file", params={"file_id": first_image_id})
            arr = np.array(first_image_array.json())
            img = ImageQt(Image.fromarray(arr.astype(np.uint8)))

            self.current_image.setPixmap(QPixmap.fromImage(img))


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

        self.setWindowTitle("Image Annotation Tool")
        self.resize(1422, 200)

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