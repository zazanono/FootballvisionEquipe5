from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar


class Chargement(QWidget):
    def __init__(self, stacked_widget, app_ecran):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.app_ecran = app_ecran  # Référence à l'écran de l'application

        layout = QVBoxLayout()
        layout.setSpacing(30)

        self.label = QLabel("Analyse en cours")
        self.label.setStyleSheet("background-color: #222F49; color: white; font-size: 30px;")

        self.barre_progression = QProgressBar()
        self.barre_progression.setMinimum(0)
        self.barre_progression.setMaximum(100)
        self.barre_progression.setValue(0)
        self.barre_progression.setFormat("%p%")
        self.barre_progression.setFixedWidth(1000)
        self.barre_progression.setStyleSheet("""
                                            QProgressBar {
                                                background-color: #ccc;
                                                border: 2px solid #4F94BA;
                                                border-radius: 15px;
                                                text-align: center;
                                                height: 30px; 
                                                font-size: 18px; 
                                                color: #222F49; 
                                                padding: 2px;
                                            }
                                            QProgressBar::chunk {
                                                background-color: #61BCF0;
                                                border-radius: 13px;
                                                margin: 0px; 
                                            }
                                            """)


        self.bouton_retour = QPushButton("Retour au menu")
        self.bouton_retour.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.bouton_retour.clicked.connect(self.retour_menu)

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.barre_progression, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.bouton_retour, alignment=Qt.AlignmentFlag.AlignCenter)

        self.bouton_retour.setVisible(False)

        self.setLayout(layout)

    def chargement_fini(self):
        print("Analyse terminée, on change d’écran !")
        self.app_ecran.set_video_path("video_foot_ml/output_videos/output_videos.mp4")
        self.stacked_widget.setCurrentIndex(2)  # Change vers l'application

    def erreur_de_chargement(self):
        self.label.setText("Erreur lors du traitement de la vidéo")

        self.bouton_retour.setVisible(True)

    def retour_menu(self):
        self.stacked_widget.setCurrentIndex(0)
        self.label.setText("Traitement en cours")
        self.bouton_retour.setVisible(False)
        self.barre_progression.setValue(0)

    def mettre_a_jour_progression(self, valeur):
        self.barre_progression.setValue(valeur)