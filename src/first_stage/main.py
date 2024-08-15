from pathlib import Path
import pickle

import numpy as np
from PIL import Image

from PIL.ImageQt import ImageQt, QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog

from src.first_stage.first_stage import Ui_MainWindow
import requests


class FirstStage(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.open_button.clicked.connect(self.open_image)

    def open_image(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "*.pkl", )
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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = FirstStage()
    window.show()
    sys.exit(app.exec())
