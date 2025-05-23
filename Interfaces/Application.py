import cv2
from PyQt6.QtCore import QTimer, QElapsedTimer, Qt, QSize
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem

from Interfaces.SliderPersonnalise import SliderPersonnalise


class Application(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.chemin_Video = None
        self.max = None
        self.jouer = False

        # Timer pour mettre à jour la vidéo
        self.chrono = QTimer(self)
        self.chrono.timeout.connect(self.update_frame)
        self.temps_Ecoule = QElapsedTimer()

        # Interface
        self.video_Label = QLabel(self)
        self.video_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centre l'affichage vidéo
        self.video_Label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Boutons
        self.boutton_Retour_Menu = QPushButton()
        self.boutton_Retour_Menu.setIcon(QIcon("images/logo.png"))  # Chemin vers icône
        self.boutton_Retour_Menu.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.boutton_Retour_Menu.setStyleSheet(
            "border: none; background: transparent;")  # Cache la bordure et l'arrière-plan
        self.boutton_Retour_Menu.clicked.connect(self.retourMenu)

        self.boutton_Pause = QPushButton()
        self.boutton_Pause.setIcon(QIcon("images/pause.png"))  # Chemin vers icône
        self.boutton_Pause.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.boutton_Pause.setStyleSheet("border: none; background: transparent;")
        self.boutton_Pause.clicked.connect(self.active_Lecture)

        self.boutton_Arret = QPushButton()
        self.boutton_Arret.setIcon(QIcon("images/stop.png"))  # Chemin vers l'icône
        self.boutton_Arret.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.boutton_Arret.setStyleSheet("border: none; background: transparent;")
        self.boutton_Arret.clicked.connect(self.arretVideo)

        self.boutton_Remonter = QPushButton()
        self.boutton_Remonter.setIcon(QIcon("images/fast-backward.png"))  # Chemin vers ton icône
        self.boutton_Remonter.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.boutton_Remonter.setStyleSheet("border: none; background: transparent;")
        self.boutton_Remonter.clicked.connect(self.remonterVideo)

        self.boutton_Avancer = QPushButton()
        self.boutton_Avancer.setIcon(QIcon("images/fast-forward.png"))  # Chemin vers ton icône
        self.boutton_Avancer.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.boutton_Avancer.setStyleSheet("border: none; background: transparent;")
        self.boutton_Avancer.clicked.connect(self.avancerVideo)

        # Barre de progression
        self.barre_Chargement = SliderPersonnalise(Qt.Orientation.Horizontal)
        self.barre_Chargement.setMinimum(0)
        self.barre_Chargement.setMaximum(100)
        self.barre_Chargement.setFixedWidth(1000)

        # Labels temps
        self.temps_Label = QLabel("0:00 / 0:00")
        self.temps_Label.setStyleSheet("color: white;")

        # Layout principal
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

        layoutH1.addWidget(self.boutton_Retour_Menu, alignment=Qt.AlignmentFlag.AlignTop)
        layoutH1.addWidget(self.video_Label)

        layoutH2.addWidget(self.boutton_Remonter, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.boutton_Pause, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.boutton_Avancer, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.boutton_Arret, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def setCheminVideo(self, path):
        """ Définit le chemin de la vidéo et initialise OpenCV """
        self.chemin_Video = path
        if self.max:
            self.max.release()  # Libérer l'ancienne vidéo si besoin
        self.max = cv2.VideoCapture(self.chemin_Video)
        self.jouer = True
        self.chrono.start(42)  # Démarrer le timer (42 ms ≈ 24 FPS)
        self.temps_Ecoule.start()

        # Ajuste le slider selon la durée réelle
        total_frames = self.max.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = self.max.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            total_time = total_frames / fps
            self.temps_Label.setText(f"0:00 / {int(total_time // 60)}:{int(total_time % 60):02d}")
            self.barre_Chargement.setMaximum(100)

    def update_frame(self):
        """ Met à jour l'affichage de la vidéo """
        if self.jouer and self.max:
            ret, frame = self.max.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                hauteur, largeur, _ = frame.shape
                bytes_Par_Lignes = 3 * largeur
                q_Img = QImage(frame.data, largeur, hauteur, bytes_Par_Lignes, QImage.Format.Format_RGB888)

                # Redimensionner l'image pour l'afficher correctement
                pixel_Map = QPixmap.fromImage(q_Img)
                self.video_Label.setPixmap(pixel_Map.scaled(
                    self.video_Label.width(), self.video_Label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                ))

                # Mise à jour slider et temps
                frame_Actuelle = self.max.get(cv2.CAP_PROP_POS_FRAMES)
                total_frames = self.max.get(cv2.CAP_PROP_FRAME_COUNT)
                if total_frames > 0:
                    self.barre_Chargement.setValue(int(frame_Actuelle / total_frames * 100))

                    temps_Actuel = int(self.max.get(cv2.CAP_PROP_POS_MSEC) / 1000)
                    total_time = int(total_frames / self.max.get(cv2.CAP_PROP_FPS))

                    self.temps_Label.setText(
                        f"{temps_Actuel // 60}:{temps_Actuel % 60:02d} / {total_time // 60}:{total_time % 60:02d}"
                    )

            else:
                self.max.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Rejouer la vidéo

    def retourMenu(self):
        self.stacked_widget.setCurrentIndex(0)
        self.arretVideo()
        self.active_Lecture()

    def active_Lecture(self):
        """ Met en pause ou reprend la lecture """
        if self.max:
            self.jouer = not self.jouer
            self.boutton_Pause.setIcon(QIcon("images/pause.png" if self.jouer else "images/play.png"))

    def arretVideo(self):
        """ Arrête la lecture de la vidéo """
        if self.max:
            self.max.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Remet la vidéo au début
            self.jouer = False
            self.boutton_Pause.setIcon(QIcon("images/play.png"))

    def remonterVideo(self):
        """ Reculer de 5 secondes dans la vidéo """
        if self.max:
            position_Actuelle = self.max.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.max.get(cv2.CAP_PROP_FPS)
            frames_A_Remonter = int(fps * 5)  # 5 secondes en frames

            nouvelle_Position = max(0, position_Actuelle - frames_A_Remonter)  # Ne pas dépasser le début de la vidéo
            self.max.set(cv2.CAP_PROP_POS_FRAMES, nouvelle_Position)

            if self.jouer == False: self.jouer = True

    def avancerVideo(self):
        """ Avancer de 5 secondes dans la vidéo """
        if self.max:
            position_Actuelle = self.max.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.max.get(cv2.CAP_PROP_FPS)
            frames_A_Avancer = int(fps * 5)  # 5 secondes en frames

            total_frames = self.max.get(cv2.CAP_PROP_FRAME_COUNT)
            nouvelle_Position = min(total_frames - 1,
                                    position_Actuelle + frames_A_Avancer)  # Ne pas dépasser la fin de la vidéo
            self.max.set(cv2.CAP_PROP_POS_FRAMES, nouvelle_Position)

            if self.jouer == False: self.jouer = True

    def compo_video(self):
        self.rect_widget = QWidget(self)
        self.rect_widget.setGeometry(200, 100, 150, 400)
        self.rect_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 2px solid white;")
        self.rect_widget.show()

        if self.max:
            self.tableau = QTableWidget(4, 3, self)
            self.tableau.setGeometry(70, 100, 450, 280)
            self.tableau.setStyleSheet("background-color: transparent; border: none;")

            for i in range(4):
                for j in range(3):
                    item = QTableWidgetItem(f"Cell {i + 1}, {j + 1}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableau.setItem(i, j, item)
