from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout


class Chargement(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()

        self.label = QLabel("...")
        self.label.setStyleSheet("background-color: #222F49; color: white; font-size: 30px;")

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)

    #def cr7(self):


