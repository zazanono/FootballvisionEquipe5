import sys
import cv2
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QStackedWidget, QFileDialog, QLabel, QHBoxLayout
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
        self.buttonParcourir.setStyleSheet("QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
                                           "QPushButton:hover {background-color: #3F7797;}"
                                           "QPushButton:pressed {background-color: #61BCF0;}")
        self.buttonParcourir.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.buttonParcourir, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Bouton pour lancer l'application
        self.buttonLancer = QPushButton("Lancer")
        self.buttonLancer.setFixedSize(150, 40)
        self.buttonLancer.setStyleSheet("QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;}"
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

        self.pause_button = QPushButton("Play", self)
        self.pause_button.setStyleSheet("QPushButton {background-color: #4F94BA; color: white; padding: 10px; border-radius: 10px;} "
                                        "QPushButton:hover {background-color: #3F7797;}"
                                        "QPushButton:pressed {background-color: #61BCF0;}")
        self.pause_button.clicked.connect(self.toggle_playback)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.pause_button, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def toggle_playback(self):
        """ Met en pause ou reprend la lecture """
        if self.cap:
            self.playing = not self.playing
            self.pause_button.setText("Pause" if self.playing else "Play")

    def closeEvent(self, event):
        """ Libère les ressources OpenCV à la fermeture """
        if self.cap:
            self.cap.release()
        event.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basketvision")
        self.showMaximized()
        self.setStyleSheet("background-color: #222F49")  # Changer la couleur

        self.stacked_widget = QStackedWidget()
        self.setWindowIcon(QIcon("logo.png"))
        self.app_screen = Application(self.stacked_widget)  # Crée l'écran de l'application
        self.menu = Menu(self.stacked_widget, self.app_screen)  # Passe une référence à l'application

        self.stacked_widget.addWidget(self.menu)       # Index 0 : Menu
        self.stacked_widget.addWidget(self.app_screen)  # Index 1 : Application

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
