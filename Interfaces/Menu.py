import cv2
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, )
from AnalyseThread import AnalyseThread


class Menu(QWidget):
    def __init__(self, stacked_widget, chargement_Ecran):
        super().__init__()
        self.stacked_widget = stacked_widget  # Référence à QStackedWidget
        self.chargement_Ecran = chargement_Ecran  # Référence à l'écran de l'application
        self.chemin_Fichier = ""
        self.ancien_Chemin = ""

        self.fichier_Selectionne = False  # Boolean pour verifier si un fichier a été selectionné
        self.fichier_Deja_Lu = False

        self.setStyleSheet("background-color: #222F49; color: white; font-size: 18px;")

        layout = QVBoxLayout()

        self.image_Label = QLabel()
        self.image_Label.setPixmap(QPixmap("images/logo.png"))  # Charge une image
        self.image_Label.setScaledContents(True)  # Ajuste l’image au QLabel
        self.image_Label.preserve_aspect_ratio = True
        self.image_Label.setFixedSize(204, 172)  # Taille de l’image
        layout.addWidget(self.image_Label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Apercu de la video choisie
        self.video_Widget = QVideoWidget()
        self.video_Widget.setFixedSize(480, 270)  # Ajuste selon la taille souhaitée
        layout.addWidget(self.video_Widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.media_Player = QMediaPlayer()
        self.media_Player.setVideoOutput(self.video_Widget)

        # Rejoue la vidéo à la fin (boucle infinie)
        self.media_Player.mediaStatusChanged.connect(self.verifierBoucleVideo)

        # Label pour afficher le chemin du fichier sélectionné
        self.label = QLabel("Aucun fichier sélectionné")
        self.label.setStyleSheet("background-color: #354665; color: white; font-size: 18px;")
        self.label.setFixedSize(500, 40)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton pour ouvrir le sélecteur de fichier
        self.boutton_Parcourir = QPushButton("Parcourir...")
        self.boutton_Parcourir.setFixedSize(150, 40)
        self.boutton_Parcourir.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.boutton_Parcourir.clicked.connect(self.parcourirFichiers)
        layout.addWidget(self.boutton_Parcourir, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton pour lancer l'application
        self.boutton_Lancer = QPushButton("Lancer")
        self.boutton_Lancer.setFixedSize(150, 40)
        self.boutton_Lancer.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;}"
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.boutton_Lancer.clicked.connect(self.lancer)
        layout.addWidget(self.boutton_Lancer, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)

    def parcourirFichiers(self):
        self.chemin_Fichier, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "", "Vidéo (*.mp4 *.avi)")
        if self.chemin_Fichier:
            self.fichier_Selectionne = True

            self.label.setText(self.chemin_Fichier)  # Afficher le chemin sélectionné

            if self.chemin_Fichier:
                self.fichier_Selectionne = True
                self.label.setText(self.chemin_Fichier)

                # Charger et jouer la vidéo en boucle
                self.media_Player.setSource(QUrl.fromLocalFile(self.chemin_Fichier))
                self.media_Player.play()

    def lancer(self):
        if self.fichier_Selectionne:  # Vérifie si un fichier a été sélectionné
            self.stacked_widget.setCurrentIndex(1)  # Change vers le chargement

            if self.ancien_Chemin == self.chemin_Fichier:
                self.fichier_Deja_Lu = True

            self.thread = AnalyseThread(self.chemin_Fichier, self.fichier_Deja_Lu)
            self.thread.analyse_Terminee.connect(self.chargement_Ecran.chargementFini)
            self.thread.erreur.connect(self.chargement_Ecran.erreurDeChargement)
            self.thread.progression.connect(self.chargement_Ecran.mettreAJourProgression)
            self.thread.start()

            self.fichier_Deja_Lu = False
            self.ancien_Chemin = self.chemin_Fichier

        else:
            self.label.setText("Sélection"
                               "ez un fichier vidéo avant de lancer l'application.")

    def verifierBoucleVideo(self, statut):
        if statut == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_Player.setPosition(0)
            self.media_Player.play()
