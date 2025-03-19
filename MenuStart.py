import sys
import cv2
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QStackedWidget, QFileDialog, QLabel, QHBoxLayout, QSizePolicy,
    QTableWidget, QTableWidgetItem
)


class Menu(QWidget):
    def __init__(self, stacked_widget, app_screen):
        super().__init__()
        self.stacked_widget = stacked_widget  # Référence à QStackedWidget
        self.app_screen = app_screen  # Référence à l'écran de l'application

        self.setStyleSheet("background-color: #222F49; color: white; font-size: 18px;")

        layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("logo.png"))  # Charge une image
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
        self.buttonParcourir.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.buttonParcourir, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton pour lancer l'application
        self.buttonLancer = QPushButton("Lancer")
        self.buttonLancer.setFixedSize(150, 40)
        self.buttonLancer.setStyleSheet(
            "QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;}"
            "QPushButton:hover {background-color: #3F7797;}"
            "QPushButton:pressed {background-color: #61BCF0;}")
        self.buttonLancer.clicked.connect(self.go_to_app)
        layout.addWidget(self.buttonLancer, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "", "Vidéo (*.mp4 *.avi)")
        if file_path:
            self.label.setText(file_path)  # Afficher le chemin sélectionné
            self.app_screen.set_video_path(file_path)  # Envoyer le chemin à l'application

    def go_to_app(self):
        if self.app_screen.video_path:  # Vérifie si un fichier a été sélectionné
            self.stacked_widget.setCurrentIndex(1)  # Change vers l'application
        else:
            self.label.setText("Sélectionnez un fichier vidéo avant de lancer l'application !")


class Application(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.video_path = None
        self.cap = None
        self.playing = False

        # Interface
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centre l'affichage vidéo
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #Boutons
        self.buttonRetourMenu = QPushButton()
        self.buttonRetourMenu.setIcon(QIcon("logo.png"))  # Chemin vers icône
        self.buttonRetourMenu.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.buttonRetourMenu.setStyleSheet("border: none; background: transparent;")  # Cache la bordure et l'arrière-plan
        self.buttonRetourMenu.clicked.connect(self.retour_menu)

        self.compo_bouton = QPushButton("Compo")
        self.compo_bouton.setGeometry(200, 100, 150, 400)
        self.compo_bouton.setStyleSheet(
            "QPushButton {background-color: white; color: black; padding: 10px; border-radius: 10px;}")
        self.compo_bouton.clicked.connect(self.compo_video)

        self.pause_button = QPushButton()
        self.pause_button.setIcon(QIcon("pause.png"))  # Chemin vers icône
        self.pause_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.pause_button.setStyleSheet("border: none; background: transparent;")
        self.pause_button.clicked.connect(self.toggle_playback)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("stop.png"))  # Chemin vers ton icône
        self.stop_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.stop_button.setStyleSheet("border: none; background: transparent;")
        self.stop_button.clicked.connect(self.stop_video)

        self.rewind_button = QPushButton()
        self.rewind_button.setIcon(QIcon("fast-backward.png"))  # Chemin vers ton icône
        self.rewind_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.rewind_button.setStyleSheet("border: none; background: transparent;")
        self.rewind_button.clicked.connect(self.rewind_video)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon("fast-forward.png"))  # Chemin vers ton icône
        self.forward_button.setIconSize(QSize(64, 64))  # Taille de l'icône
        self.forward_button.setStyleSheet("border: none; background: transparent;")
        self.forward_button.clicked.connect(self.forward_video)

        # Layout principal
        layout = QVBoxLayout()

        layoutH1 = QHBoxLayout()
        layoutH2 = QHBoxLayout()

        layout.addLayout(layoutH1)
        layout.addLayout(layoutH2)

        layoutH1.addWidget(self.buttonRetourMenu, alignment=Qt.AlignmentFlag.AlignTop)
        layoutH1.addWidget(self.video_label)
        layoutH1.addWidget(self.compo_bouton, alignment=Qt.AlignmentFlag.AlignCenter)

        layoutH2.addWidget(self.pause_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.stop_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.rewind_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layoutH2.addWidget(self.forward_button, alignment=Qt.AlignmentFlag.AlignCenter)


        self.setLayout(layout)

        # Timer pour mettre à jour la vidéo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def set_video_path(self, path):
        """ Définit le chemin de la vidéo et initialise OpenCV """
        self.video_path = path
        if self.cap:
            self.cap.release()  # Libérer l'ancienne vidéo si besoin
        self.cap = cv2.VideoCapture(self.video_path)
        self.playing = True
        self.timer.start(30)  # Démarrer le timer (30 ms ≈ 33 FPS)

    def update_frame(self):
        """ Met à jour l'affichage de la vidéo """
        if self.playing and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir pour PyQt6
                height, width, _ = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

                # Redimensionner l'image pour l'afficher correctement
                pixmap = QPixmap.fromImage(q_img)
                self.video_label.setPixmap(pixmap.scaled(
                    self.video_label.width(), self.video_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                ))
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
            self.pause_button.setIcon(QIcon("pause.png" if self.playing else "play.png"))


    def stop_video(self):
        """ Arrête la lecture de la vidéo """
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Remet la vidéo au début
            self.playing = False
            self.pause_button.setIcon(QIcon("play.png"))

    def rewind_video(self):
        """ Reculer de 15 secondes dans la vidéo """
        if self.cap:
            current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frames_to_rewind = int(fps * 5)  # 15 secondes en frames

            new_pos = max(0, current_pos - frames_to_rewind)  # Ne pas dépasser le début de la vidéo
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)


    def forward_video(self):
        """ Avancer de 15 secondes dans la vidéo """
        if self.cap:
            current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frames_to_advance = int(fps * 5)  # 15 secondes en frames

            total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            new_pos = min(total_frames - 1, current_pos + frames_to_advance)  # Ne pas dépasser la fin de la vidéo
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)

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

    def closeEvent(self, event):
        """ Libère les ressources OpenCV à la fermeture """
        if self.cap:
            self.cap.release()
        event.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision FC")
        self.showMaximized()
        self.setStyleSheet("background-color: #222F49")  # Changer la couleur

        self.stacked_widget = QStackedWidget()
        self.setWindowIcon(QIcon("logo.png"))
        self.app_screen = Application(self.stacked_widget)  # Crée l'écran de l'application
        self.menu = Menu(self.stacked_widget, self.app_screen)  # Passe une référence à l'application

        self.stacked_widget.addWidget(self.menu)  # Index 0 : Menu
        self.stacked_widget.addWidget(self.app_screen)  # Index 1 : Application

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())