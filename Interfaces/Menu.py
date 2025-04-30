import cv2
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, )
from analyse_thread import AnalyseThread


class Menu(QWidget):
    def __init__(self, stacked_widget, chargement_ecran):
        super().__init__()
        self.stacked_widget = stacked_widget  # Référence à QStackedWidget
        self.chargement_ecran = chargement_ecran  # Référence à l'écran de l'application
        self.file_path = ""
        self.ancient_file_path = ""

        self.fichier_selectionne = False  # Boolean pour verifier si un fichier a été selectionné
        self.fichier_deja_lu = False

        self.setStyleSheet("background-color: #222F49; color: white; font-size: 18px;")

        layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("images/logo.png"))  # Charge une image
        self.image_label.setScaledContents(True)  # Ajuste l’image au QLabel
        self.image_label.preserve_aspect_ratio = True
        self.image_label.setFixedSize(204, 172)  # Taille de l’image
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Apercu de la video choisie
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(480, 270)  # Ajuste selon la taille souhaitée
        layout.addWidget(self.video_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        # Rejoue la vidéo à la fin (boucle infinie)
        self.media_player.mediaStatusChanged.connect(self.check_loop_video)

        # Label pour afficher le chemin du fichier sélectionné
        self.label = QLabel("Aucun fichier sélectionné")
        self.label.setStyleSheet("background-color: #354665; color: white; font-size: 18px;")
        self.label.setFixedSize(500, 40)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton pour ouvrir le sélecteur de fichier
        self.buttonParcourir = QPushButton("Parcourir...")
        self.buttonParcourir.setFixedSize(150, 40)
        self.buttonParcourir.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.buttonParcourir.clicked.connect(self.parcourir_fichiers)
        layout.addWidget(self.buttonParcourir, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton pour lancer l'application
        self.buttonLancer = QPushButton("Lancer")
        self.buttonLancer.setFixedSize(150, 40)
        self.buttonLancer.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;}"
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.buttonLancer.clicked.connect(self.lancer)
        layout.addWidget(self.buttonLancer, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)

    def parcourir_fichiers(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "", "Vidéo (*.mp4 *.avi)")
        if self.file_path:
            self.fichier_selectionne = True

            self.label.setText(self.file_path)  # Afficher le chemin sélectionné

            if self.file_path:
                self.fichier_selectionne = True
                self.label.setText(self.file_path)

                # Charger et jouer la vidéo en boucle
                self.media_player.setSource(QUrl.fromLocalFile(self.file_path))
                self.media_player.play()

    def lancer(self):
        if self.fichier_selectionne:  # Vérifie si un fichier a été sélectionné
            self.stacked_widget.setCurrentIndex(1)  # Change vers le chargement

            if self.ancient_file_path == self.file_path:
                self.fichier_deja_lu = True

            self.thread = AnalyseThread(self.file_path, self.fichier_deja_lu)
            self.thread.analyse_terminee.connect(self.chargement_ecran.chargement_fini)
            self.thread.erreur.connect(self.chargement_ecran.erreur_de_chargement)
            self.thread.progression.connect(self.chargement_ecran.mettre_a_jour_progression)
            self.thread.start()

            self.fichier_deja_lu = False
            self.ancient_file_path = self.file_path

        else:
            self.label.setText("Sélection"
                               "ez un fichier vidéo avant de lancer l'application.")

    def check_loop_video(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
