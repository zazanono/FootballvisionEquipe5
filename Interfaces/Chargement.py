from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar


class Chargement(QWidget):
    def __init__(self, stacked_widget, ecran_App):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.ecran_App = ecran_App  # Référence à l'écran de l'application

        layout = QVBoxLayout()

        self.label = QLabel("Analyse en cours")
        self.label.setStyleSheet("background-color: #222F49; color: white; font-size: 30px;")

        self.barre_Progression = QProgressBar()
        self.barre_Progression.setMinimum(0)
        self.barre_Progression.setMaximum(100)
        self.barre_Progression.setValue(0)
        self.barre_Progression.setFormat("%p%")
        self.barre_Progression.setFixedWidth(1000)
        self.barre_Progression.setStyleSheet("""
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

        self.bouton_Retour = QPushButton("Retour au menu")
        self.bouton_Retour.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.bouton_Retour.clicked.connect(self.retourMenu)

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.barre_Progression, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.bouton_Retour, alignment=Qt.AlignmentFlag.AlignCenter)

        self.bouton_Retour.setVisible(False)

        self.setLayout(layout)

    def chargementFini(self):
        print("Analyse terminée, on change d’écran !")
        self.ecran_App.setCheminVideo("video_Foot_Ml/output_videos/output_videos.mp4")
        self.barre_Progression.setValue(0)
        self.stacked_widget.setCurrentIndex(2)  # Change vers l'application

    def erreurDeChargement(self):
        self.label.setText("Erreur lors du traitement de la vidéo")

        self.bouton_Retour.setVisible(True)

    def retourMenu(self):
        self.stacked_widget.setCurrentIndex(0)
        self.label.setText("Traitement en cours")
        self.bouton_Retour.setVisible(False)
        self.barre_Progression.setValue(0)

    def mettreAJourProgression(self, valeur):
        self.barre_Progression.setValue(valeur)
