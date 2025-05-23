from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QProgressBar


# Classe Chargement : écran d’attente affiché pendant le traitement de la vidéo
class Chargement(QWidget):
    def __init__(self, stacked_widget, app_ecran):
        super().__init__()
        # Référence au gestionnaire de vues (QStackedWidget)
        self.stacked_widget = stacked_widget

        # Référence à l’écran principal de l’application (où sera jouée la vidéo)
        self.ecran_App = app_ecran

        # --- Création du layout vertical principal ---
        layout = QVBoxLayout()

        # Label d’information affiché pendant le chargement
        self.label = QLabel("Analyse en cours")
        self.label.setStyleSheet("background-color: #222F49; color: white; font-size: 30px;")

        # Barre de progression graphique
        self.barre_Progression = QProgressBar()
        self.barre_Progression.setMinimum(0)
        self.barre_Progression.setMaximum(100)
        self.barre_Progression.setValue(0)
        self.barre_Progression.setFormat("%p%")  # Affiche le pourcentage
        self.barre_Progression.setFixedWidth(1000)
        # Style personnalisé de la barre
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

        # Bouton pour revenir au menu en cas d’erreur
        self.bouton_Retour = QPushButton("Retour au menu")
        self.bouton_Retour.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.bouton_Retour.clicked.connect(self.retourMenu)

        # Ajout des widgets au layout
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.barre_Progression, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.bouton_Retour, alignment=Qt.AlignmentFlag.AlignCenter)

        # Le bouton retour est masqué par défaut
        self.bouton_Retour.setVisible(False)

        # Application du layout à ce widget
        self.setLayout(layout)

    def chargementFini(self):
        """ Méthode appelée quand le traitement de la vidéo est terminé """
        print("Analyse terminée, on change d’écran!")

        # Prépare la vidéo dans l'écran principal de l'application
        self.ecran_App.setCheminVideo("VideoFootMl/VideosOutput/VideosOutput.mp4")

        # Réinitialise la barre de progression
        self.barre_Progression.setValue(0)

        # Affiche l'écran principal (index 2 du QStackedWidget)
        self.stacked_widget.setCurrentIndex(2)

    def erreurChargement(self):
        """ Méthode appelée en cas d’erreur de traitement de la vidéo """
        self.label.setText("Erreur lors du traitement de la vidéo")

        # Affiche le bouton pour revenir au menu
        self.bouton_Retour.setVisible(True)

    def retourMenu(self):
        """ Ramène l'utilisateur au menu principal """
        self.stacked_widget.setCurrentIndex(0)
        self.label.setText("Traitement en cours")
        self.bouton_Retour.setVisible(False)
        self.barre_Progression.setValue(0)

    def mettreAJourProgression(self, valeur):
        """ Met à jour la barre de progression avec la valeur donnée (0 à 100) """
        self.barre_Progression.setValue(valeur)
