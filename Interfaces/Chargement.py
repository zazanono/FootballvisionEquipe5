from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton


class Chargement(QWidget):
    def __init__(self, stacked_widget, app_ecran):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.app_ecran = app_ecran  # Référence à l'écran de l'application

        layout = QVBoxLayout()

        self.label = QLabel("Traitement en cours")
        self.label.setStyleSheet("background-color: #222F49; color: white; font-size: 30px;")

        self.bouton_retour = QPushButton("Retour au menu")
        self.bouton_retour.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.bouton_retour.clicked.connect(self.retour_menu)

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self.bouton_retour, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.bouton_retour.setVisible(False)

        self.setLayout(layout)

    def chargement_fini(self):
        print("Analyse terminée, on change d’écran !")
        self.app_ecran.set_video_path("video_foot_ml/output_videos/output_videos.mp4")
        # self.app_ecran.set_video_path("output_videos/output_videos.mp4")
        self.stacked_widget.setCurrentIndex(2)  # Change vers l'application

    def erreur_de_chargement(self):
        self.label.setText("Erreur lors du traitement de la vidéo")

        self.bouton_retour.setVisible(True)

    def retour_menu(self):
        self.stacked_widget(0)
        self.label.setText("Traitement en cours")
        self.bouton_retour.setVisible(False)