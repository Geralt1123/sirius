from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DetectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Интерфейс для распознавания")
        layout.addWidget(label)
        self.setLayout(layout)
