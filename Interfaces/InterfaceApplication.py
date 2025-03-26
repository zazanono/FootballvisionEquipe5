import cv2
from PyQt6.QtCore import QTimer, QElapsedTimer, Qt, QSize
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem

from CustomSlider import CustomSlider


class Application(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.video_path = None
        self.cap = None
        self.playing = False

        # Timer pour mettre à jour la vidéo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.elapsed_timer = QElapsedTimer()

        # Interface
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centre l'affichage vidéo
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Boutons
        self.buttonRetourMenu = QPushButton()
        self.buttonRetourMenu.setIcon(QIcon("../images/logo.png"))  # Chemin vers icône
        self.buttonRetourMenu.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.buttonRetourMenu.setStyleSheet(
            "border: none; background: transparent;")  # Cache la bordure et l'arrière-plan
        self.buttonRetourMenu.clicked.connect(self.retour_menu)

        self.compo_bouton = QPushButton("Compo")
        self.compo_bouton.setGeometry(200, 100, 150, 400)
        self.compo_bouton.setStyleSheet(
            "QPushButton {background-color: white; color: black; padding: 10px; border-radius: 10px;}")
        self.compo_bouton.clicked.connect(self.compo_video)

        self.pause_button = QPushButton()
        self.pause_button.setIcon(QIcon("../images/pause.png"))  # Chemin vers icône
        self.pause_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.pause_button.setStyleSheet("border: none; background: transparent;")
        self.pause_button.clicked.connect(self.toggle_playback)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("../images/stop.png"))  # Chemin vers ton icône
        self.stop_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.stop_button.setStyleSheet("border: none; background: transparent;")
        self.stop_button.clicked.connect(self.stop_video)

        self.rewind_button = QPushButton()
        self.rewind_button.setIcon(QIcon("../images/fast-backward.png"))  # Chemin vers ton icône
        self.rewind_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.rewind_button.setStyleSheet("border: none; background: transparent;")
        self.rewind_button.clicked.connect(self.rewind_video)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon("../images/fast-forward.png"))  # Chemin vers ton icône
        self.forward_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.forward_button.setStyleSheet("border: none; background: transparent;")
        self.forward_button.clicked.connect(self.forward_video)

        # Barre de progression
        self.slider = CustomSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)  # Par défaut, ajusté lors du chargement de la vidéo


        # Labels temps
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setStyleSheet("color: white;")

        # Layout principal
        layout = QVBoxLayout()

        layoutH1 = QHBoxLayout()
        layoutH2 = QHBoxLayout()

        layout.addLayout(layoutH1)
        layout.addWidget(self.slider)
        layout.addWidget(self.time_label)
        layout.addLayout(layoutH2)

        layoutH1.addWidget(self.buttonRetourMenu, alignment=Qt.AlignmentFlag.AlignTop)
        layoutH1.addWidget(self.video_label)
        layoutH1.addWidget(self.compo_bouton, alignment=Qt.AlignmentFlag.AlignCenter)

        layoutH2.addWidget(self.pause_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.stop_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.rewind_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.forward_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)



    def set_video_path(self, path):
        """ Définit le chemin de la vidéo et initialise OpenCV """
        self.video_path = path
        if self.cap:
            self.cap.release()  # Libérer l'ancienne vidéo si besoin
        self.cap = cv2.VideoCapture(self.video_path)
        self.playing = True
        self.timer.start(30)  # Démarrer le timer (30 ms ≈ 33 FPS)
        self.elapsed_timer.start()

        # Ajuste le slider selon la durée réelle
        total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            total_time = total_frames / fps
            self.time_label.setText(f"0:00 / {int(total_time // 60)}:{int(total_time % 60):02d}")
            self.slider.setMaximum(100)

    def update_frame(self):
        """ Met à jour l'affichage de la vidéo """
        if self.playing and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, _ = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

                # Redimensionner l'image pour l'afficher correctement
                pixmap = QPixmap.fromImage(q_img)
                self.video_label.setPixmap(pixmap.scaled(
                    self.video_label.width(), self.video_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                ))

                # Mise à jour slider et temps
                current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if total_frames > 0:
                    self.slider.setValue(int(current_frame / total_frames * 100))

                    current_time = int(self.cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
                    total_time = int(total_frames / self.cap.get(cv2.CAP_PROP_FPS))

                    self.time_label.setText(
                        f"{current_time // 60}:{current_time % 60:02d} / {total_time // 60}:{total_time % 60:02d}"
                    )

            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Rejouer la vidéo

    def retour_menu(self):
        self.stacked_widget.setCurrentIndex(0)
        self.stop_video()
        self.toggle_playback()

    def toggle_playback(self):
        """ Met en pause ou reprend la lecture """
        if self.cap:
            self.playing = not self.playing
            self.pause_button.setIcon(QIcon("images/pause.png" if self.playing else "images/play.png"))

    def stop_video(self):
        """ Arrête la lecture de la vidéo """
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Remet la vidéo au début
            self.playing = False
            self.pause_button.setIcon(QIcon("../images/play.png"))

    def rewind_video(self):
        """ Reculer de 5 secondes dans la vidéo """
        if self.cap:
            current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frames_to_rewind = int(fps * 5)  # 15 secondes en frames

            new_pos = max(0, current_pos - frames_to_rewind)  # Ne pas dépasser le début de la vidéo
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)

            if self.playing == False: self.playing = True

    def forward_video(self):
        """ Avancer de 5 secondes dans la vidéo """
        if self.cap:
            current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frames_to_advance = int(fps * 5)  # 15 secondes en frames

            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            new_pos = min(total_frames - 1, current_pos + frames_to_advance)  # Ne pas dépasser la fin de la vidéo
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)

            if self.playing == False: self.playing = True

    def compo_video(self):
        self.rect_widget = QWidget(self)
        self.rect_widget.setGeometry(200, 100, 150, 400)
        self.rect_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 2px solid white;")
        self.rect_widget.show()

        if self.cap:
            self.tableau = QTableWidget(4, 3, self)
            self.tableau.setGeometry(70, 100, 450, 280)
            self.tableau.setStyleSheet("background-color: transparent; border: none;")

            for i in range(4):
                for j in range(3):
                    item = QTableWidgetItem(f"Cell {i + 1}, {j + 1}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableau.setItem(i, j, item)

