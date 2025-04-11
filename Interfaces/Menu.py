from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel,)
from video_foot_ml.MainML import *

class Menu(QWidget):
    def __init__(self, stacked_widget, chargement_ecran):
        super().__init__()
        self.stacked_widget = stacked_widget  # Référence à QStackedWidget
        self.chargement_ecran = chargement_ecran  # Référence à l'écran de l'application

        self.fichier_selectionne = False # Boolean pour verifier si un fichier a été selectionné
        self.file_path = ""

        self.setStyleSheet("background-color: #222F49; color: white; font-size: 18px;")

        layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("images/logo.png"))  # Charge une image
        self.image_label.setScaledContents(True)  # Ajuste l’image au QLabel
        self.image_label.preserve_aspect_ratio = True
        self.image_label.setFixedSize(204, 172)  # Taille de l’image
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignHCenter)

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
            self.label.setText(self.file_path)  # Afficher le chemin sélectionné
            self.fichier_selectionne = True
            #self.chargement_ecran.set_video_path(file_path)  # Envoyer le chemin à l'application
            # self.app_ecran.set_video_path('video_foot_ml/output_videos/output_videos.mp4')  # Envoyer le chemin à l'application

    def lancer(self):
        if self.fichier_selectionne:  # Vérifie si un fichier a été sélectionné
            self.chargement_ecran.set_file_path_pour_analyse(self.file_path)
            self.stacked_widget.setCurrentIndex(1)  # Change vers le chargement
            #analyseYolo(self.file_path, False, self.chargement_ecran)
        else:
            self.label.setText("Sélectionnez un fichier vidéo avant de lancer l'application.")