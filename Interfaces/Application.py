import cv2
from PyQt6.QtCore import QTimer, QElapsedTimer, Qt, QSize
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem

from Interfaces.BarrePersonnalisee import BarrePersonalisee


# Classe principale de l'interface graphique permettant de lire une vidéo et de la contrôler
class Application(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        # Widget pour permettre de revenir au menu principal
        self.stacked_widget = stacked_widget

        # Variables de lecture vidéo
        self.chemin_Video = None
        self.cap = None
        self.jouer = False

        # Chronomètre pour mettre à jour la vidéo
        self.chrono = QTimer(self)
        self.chrono.timeout.connect(self.updateFrame)
        self.temps_Ecoule = QElapsedTimer()

        # Interface
        # Zone d'affichage vidéo
        self.video_Label = QLabel(self)
        self.video_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centre l'affichage vidéo
        self.video_Label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # --- Création des boutons de contrôle vidéo ---

        # Bouton pour retourner au menu
        self.bouton_Retour_Menu = QPushButton()
        self.bouton_Retour_Menu.setIcon(QIcon("images/logo.png"))  # Chemin vers icône
        self.bouton_Retour_Menu.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.bouton_Retour_Menu.setStyleSheet(
            "border: none; background: transparent;")  # Cache la bordure et l'arrière-plan
        self.bouton_Retour_Menu.clicked.connect(self.retourMenu)

        # Bouton lecture/pause
        self.bouton_Pause = QPushButton()
        self.bouton_Pause.setIcon(QIcon("images/pause.png"))  # Chemin vers l'icône
        self.bouton_Pause.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.bouton_Pause.setStyleSheet("border: none; background: transparent;")
        self.bouton_Pause.clicked.connect(self.recommencerLecture)

        # Bouton arrêt (remet au début)
        self.bouton_Arret = QPushButton()
        self.bouton_Arret.setIcon(QIcon("images/stop.png"))  # Chemin vers l'icône
        self.bouton_Arret.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.bouton_Arret.setStyleSheet("border: none; background: transparent;")
        self.bouton_Arret.clicked.connect(self.arreterVideo)

        # Bouton pour reculer de 5 secondes
        self.bouton_Remonter = QPushButton()
        self.bouton_Remonter.setIcon(QIcon("images/fast-backward.png"))  # Chemin vers l'icône
        self.bouton_Remonter.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.bouton_Remonter.setStyleSheet("border: none; background: transparent;")
        self.bouton_Remonter.clicked.connect(self.remonterVideo)

        # Bouton pour avancer de 5 secondes
        self.bouton_Avancer = QPushButton()
        self.bouton_Avancer.setIcon(QIcon("images/fast-forward.png"))  # Chemin vers l'icône
        self.bouton_Avancer.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.bouton_Avancer.setStyleSheet("border: none; background: transparent;")
        self.bouton_Avancer.clicked.connect(self.avancerVideo)

        # --- Barre de progression personnalisée ---
        self.barre_Chargement = BarrePersonalisee(Qt.Orientation.Horizontal)
        self.barre_Chargement.setMinimum(0)
        self.barre_Chargement.setMaximum(100)  # Par défaut, ajusté lors du chargement de la vidéo
        self.barre_Chargement.setFixedWidth(1000)

        # Label pour afficher le temps écoulé / total
        self.temps_Label = QLabel("0:00 / 0:00")
        self.temps_Label.setStyleSheet("color: white;")

        # --- Organisation des layouts (disposition graphique) ---
        layout = QVBoxLayout()

        layoutH1 = QHBoxLayout()
        layoutH2 = QHBoxLayout()
        layoutH2.setContentsMargins(500, 0, 500, 0)
        layoutH3 = QHBoxLayout()
        layoutH3.setContentsMargins(200, 0, 200, 0)

        layout.addLayout(layoutH1)
        layout.addLayout(layoutH3)
        layout.addLayout(layoutH2)

        layoutH3.addWidget(self.temps_Label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layoutH3.addWidget(self.barre_Chargement, alignment=Qt.AlignmentFlag.AlignHCenter)

        layoutH1.addWidget(self.bouton_Retour_Menu, alignment=Qt.AlignmentFlag.AlignTop)
        layoutH1.addWidget(self.video_Label)

        layoutH2.addWidget(self.bouton_Remonter, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.bouton_Pause, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.bouton_Avancer, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.bouton_Arret, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    # -------- MÉTHODES --------

    def setCheminVideo(self, path):
        """ Charge la vidéo à partir du chemin spécifié et initialise les paramètres de lecture """
        self.chemin_Video = path
        if self.cap:
            self.cap.release()  # Libérer l'ancienne vidéo si besoin
        self.cap = cv2.VideoCapture(self.chemin_Video)
        self.jouer = True
        self.chrono.start(42)  # Démarrer le chrono (42 ms ≈ 24 FPS)
        self.temps_Ecoule.start()

        # Mise à jour de la durée dans l'interface
        total_Frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            total_time = total_Frames / fps
            self.temps_Label.setText(f"0:00 / {int(total_time // 60)}:{int(total_time % 60):02d}")
            self.barre_Chargement.setMaximum(100)

    def updateFrame(self):
        """ Lit et affiche une nouvelle frame de la vidéo """
        if self.jouer and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                hauteur, largeur, _ = frame.shape
                bytes_Par_ligne = 3 * largeur
                q_Img = QImage(frame.data, largeur, hauteur, bytes_Par_ligne, QImage.Format.Format_RGB888)

                # Affichage de la frame dans le QLabel
                pixmap = QPixmap.fromImage(q_Img)
                self.video_Label.setPixmap(pixmap.scaled(
                    self.video_Label.width(), self.video_Label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                ))

                # Mise à jour du slider et du temps
                frame_Actuelle = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                total_Frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if total_Frames > 0:
                    self.barre_Chargement.setValue(int(frame_Actuelle / total_Frames * 100))

                    temps_Actuel = int(self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
                    temps_Total = int(total_Frames / self.cap.get(cv2.CAP_PROP_FPS))

                    self.temps_Label.setText(
                        f"{temps_Actuel // 60}:{temps_Actuel % 60:02d} / {temps_Total // 60}:{temps_Total % 60:02d}"
                    )

            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Redémarre la vidéo à la fin

    def retourMenu(self):
        """ Retourne au menu principal """
        self.stacked_widget.setCurrentIndex(0)
        self.arreterVideo()
        self.recommencerLecture()

    def recommencerLecture(self):
        """ Met la lecture en pause ou la reprend """
        if self.cap:
            self.jouer = not self.jouer
            self.bouton_Pause.setIcon(QIcon("images/pause.png" if self.jouer else "images/play.png"))

    def arreterVideo(self):
        """ Arrête la lecture et remet la vidéo au début """
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Remet la vidéo au début
            self.jouer = False
            self.bouton_Pause.setIcon(QIcon("images/play.png"))

    def remonterVideo(self):
        """ Reculer de 5 secondes dans la vidéo """
        if self.cap:
            position_Actuelle = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frames_A_Remonter = int(fps * 5)  # 5 secondes en frames

            nouvelle_Position = max(0, position_Actuelle - frames_A_Remonter)  # Ne pas dépasser le début de la vidéo
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, nouvelle_Position)

            if self.jouer == False: self.jouer = True

    def avancerVideo(self):
        """ Avancer de 5 secondes dans la vidéo """
        if self.cap:
            position_Actuelle = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frames_A_Avancer = int(fps * 5)  # 5 secondes en frames

            total_Frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            nouvelle_Position = min(total_Frames - 1,
                                    position_Actuelle + frames_A_Avancer)  # Ne pas dépasser la fin de la vidéo
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, nouvelle_Position)

            if self.jouer == False: self.jouer = True

    def compoVideo(self):
        """ Crée une zone rectangulaire et un tableau pour afficher des informations (ex. statistiques) """
        self.rect_widget = QWidget(self)
        self.rect_widget.setGeometry(200, 100, 150, 400)
        self.rect_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 2px solid white;")
        self.rect_widget.show()

        if self.cap:
            self.tableau = QTableWidget(4, 3, self)
            self.tableau.setGeometry(70, 100, 450, 280)
            self.tableau.setStyleSheet("background-color: transparent; border: none;")

            # Remplissage de chaque cellule du tableau
            for i in range(4):
                for j in range(3):
                    item = QTableWidgetItem(f"Cell {i + 1}, {j + 1}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableau.setItem(i, j, item)
