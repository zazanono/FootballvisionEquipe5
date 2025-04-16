from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout


class Chargement(QWidget):
    def __init__(self, stacked_widget, app_ecran):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.app_ecran = app_ecran  # Référence à l'écran de l'application

        layout = QVBoxLayout()

        self.label = QLabel("Traitement en cours")
        self.label.setStyleSheet("background-color: #222F49; color: white; font-size: 30px;")

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)


    def chargement_fini(self):
        self.stacked_widget.setCurrentIndex(2) # Change vers l'application
        self.app_ecran.set_video_path("output_videos/output_videos.mp4")




