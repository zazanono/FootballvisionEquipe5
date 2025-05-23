from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, )

from AnalyseThread import AnalyseThread


# Classe Menu : représente l'écran d'accueil de l'application
# Permet de sélectionner une vidéo et de lancer l’analyse
class Menu(QWidget):
    def __init__(self, stacked_widget, chargement_ecran):
        super().__init__()
        # Référence au gestionnaire d’écrans (QStackedWidget)
        self.stacked_Widget = stacked_widget
        # Référence à l’écran de chargement
        self.chargement_Ecran = chargement_ecran
        # Variables pour suivre le fichier sélectionné
        self.chemin_Fichier = ""
        self.ancien_Chemin_Fichier = ""

        self.fichier_Selectionne = False  # Boolean pour verifier si un fichier a été selectionné
        self.fichier_Deja_Lu = False

        # Style général de l'écran
        self.setStyleSheet("background-color: #222F49; color: white; font-size: 18px;")

        # --- Mise en page verticale ---
        layout = QVBoxLayout()

        # Logo de l'application
        self.image_Label = QLabel()
        self.image_Label.setPixmap(QPixmap("images/logo.png"))  # Charge une image
        self.image_Label.setScaledContents(True)  # Ajuste l’image au QLabel
        self.image_Label.preserve_aspect_ratio = True
        self.image_Label.setFixedSize(204, 172)  # Taille de l’image
        layout.addWidget(self.image_Label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Widget pour afficher un aperçu vidéo (QVideoWidget + QMediaPlayer)
        self.video_Widget = QVideoWidget()
        self.video_Widget.setFixedSize(480, 270)  # Ajuste selon la taille souhaitée
        layout.addWidget(self.video_Widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.media_Player = QMediaPlayer()
        self.media_Player.setVideoOutput(self.video_Widget)
        # Rejoue la vidéo à la fin (boucle infinie)
        self.media_Player.mediaStatusChanged.connect(self.boucleVideo)

        # Label affichant le chemin du fichier sélectionné
        self.label = QLabel("Aucun fichier sélectionné")
        self.label.setStyleSheet("background-color: #354665; color: white; font-size: 18px;")
        self.label.setFixedSize(500, 40)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton "Parcourir..." pour choisir une vidéo sur l’ordinateur
        self.bouton_Parcourir = QPushButton("Parcourir...")
        self.bouton_Parcourir.setFixedSize(150, 40)
        self.bouton_Parcourir.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.bouton_Parcourir.clicked.connect(self.parcourirFichiers)
        layout.addWidget(self.bouton_Parcourir, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton "Lancer" pour démarrer l’analyse de la vidéo sélectionnée
        self.bouton_Lancer = QPushButton("Lancer")
        self.bouton_Lancer.setFixedSize(150, 40)
        self.bouton_Lancer.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;}"
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.bouton_Lancer.clicked.connect(self.lancer)
        layout.addWidget(self.bouton_Lancer, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Application du layout
        self.setLayout(layout)

    def parcourirFichiers(self):
        """ Ouvre une boîte de dialogue pour sélectionner un fichier vidéo """
        self.chemin_Fichier, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "", "Vidéo (*.mp4 *.avi)")
        if self.chemin_Fichier:
            self.fichier_Selectionne = True

            self.label.setText(self.chemin_Fichier)  # Affiche le chemin choisi

            if self.chemin_Fichier:
                self.fichier_Selectionne = True
                self.label.setText(self.chemin_Fichier)

                # Prépare et joue la vidéo sélectionnée
                self.media_Player.setSource(QUrl.fromLocalFile(self.chemin_Fichier))
                self.media_Player.play()

    def lancer(self):
        """ Lance l’analyse de la vidéo choisie en lançant un thread de traitement """
        if self.fichier_Selectionne:  # Vérifie si un fichier a été sélectionné
            self.stacked_Widget.setCurrentIndex(1)  # Passe à l'écran de chargement

            # Vérifie si la vidéo est la même qu'avant (utile pour ne pas réanalyser deux fois)
            if self.ancien_Chemin_Fichier == self.chemin_Fichier:
                self.fichier_Deja_Lu = True

            # Crée un thread d’analyse
            self.thread = AnalyseThread(self.chemin_Fichier, self.fichier_Deja_Lu)
            # Connexion des signaux du thread à l’écran de chargement
            self.thread.analyse_Terminee.connect(self.chargement_Ecran.chargementFini)
            self.thread.erreur.connect(self.chargement_Ecran.erreurChargement)
            self.thread.progression.connect(self.chargement_Ecran.mettreAJourProgression)
            self.thread.start()

            # Mise à jour des états
            self.fichier_Deja_Lu = False
            self.ancien_Chemin_Fichier = self.chemin_Fichier

        else:
            # Aucun fichier sélectionné → affiche un message d'erreur
            self.label.setText("Sélectionnez un fichier vidéo avant de lancer l'application.")

    def boucleVideo(self, status):
        """ Redémarre automatiquement la vidéo quand elle se termine (pour la prévisualisation) """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_Player.setPosition(0)
            self.media_Player.play()
