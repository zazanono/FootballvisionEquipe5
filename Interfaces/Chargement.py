from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

from video_foot_ml.MainML import *


class Chargement(QWidget):
    def __init__(self, stacked_widget, app_ecran):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.file_path = ""
        self.app_ecran = app_ecran  # Référence à l'écran de l'application

        layout = QVBoxLayout()

        self.label = QLabel("Traitement en cours")
        self.label.setStyleSheet("background-color: #222F49; color: white; font-size: 30px;")

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)
        if self.file_path != "":
            print("analyse")
            #analyseYolo(self.file_path, False, self)


    def set_file_path_pour_analyse(self, file_path):
        self.file_path = file_path


    def chargement_fini(self):
        self.app_ecran.set_video_path('video_foot_ml/output_videos/output_videos.mp4')
        self.stacked_widget.setCurrentIndex(2) # Change vers l'application



