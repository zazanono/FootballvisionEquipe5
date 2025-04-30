import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel,)
from analyse_thread import AnalyseThread


class Menu(QWidget):
    def __init__(self, stacked_widget, chargement_ecran):
        super().__init__()
        self.stacked_widget = stacked_widget  # Référence à QStackedWidget
        self.chargement_ecran = chargement_ecran  # Référence à l'écran de l'application
        self.file_path = ""
        self.ancient_file_path = ""

        self.fichier_selectionne = False # Boolean pour verifier si un fichier a été selectionné
        self.fichier_deja_lu = False

        self.setStyleSheet("background-color: #222F49; color: white; font-size: 18px;")

        layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("images/logo.png"))  # Charge une image
        self.image_label.setScaledContents(True)  # Ajuste l’image au QLabel
        self.image_label.preserve_aspect_ratio = True
        self.image_label.setFixedSize(204, 172)  # Taille de l’image
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Label pour l’apercu de la video
        self.video_preview_label = QLabel()
        self.video_preview_label.setFixedSize(480, 270)
        self.video_preview_label.setStyleSheet("border: 2px solid #4F94BA; background-color: black;")
        layout.addWidget(self.video_preview_label, alignment=Qt.AlignmentFlag.AlignHCenter)

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

            if self.ancient_file_path == self.file_path:
                self.fichier_deja_lu = True

            self.label.setText(self.file_path)  # Afficher le chemin sélectionné

            # Lire la première frame de la vidéo
            cap = cv2.VideoCapture(self.file_path)
            ret, frame = cap.read()
            cap.release()

            if ret:
                # Convertir BGR → RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Redimensionner à la taille du QLabel
                frame_resized = cv2.resize(frame, (480, 270), interpolation=cv2.INTER_AREA)

                # Convertir en QImage puis QPixmap
                h, w, ch = frame_resized.shape
                bytes_per_line = ch * w
                q_image = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)

                # Afficher dans le QLabel
                self.video_preview_label.setPixmap(pixmap)


    def lancer(self):
        if self.fichier_selectionne:  # Vérifie si un fichier a été sélectionné
            self.stacked_widget.setCurrentIndex(1)  # Change vers le chargement

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