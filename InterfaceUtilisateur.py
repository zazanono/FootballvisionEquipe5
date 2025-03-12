import sys
import cv2
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtGui import QImage, QPixmap, QIcon, QPainter, QColor
from PyQt6.QtCore import QTimer, QRect


class VideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()
        #self.showMaximized()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        self.playing = True

        # Interface
        self.video_label = QLabel(self)
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.toggle_playback)
        self.setWindowTitle("Video soccer tracker")
        self.setWindowIcon(QIcon("71bgARSO2EL.jpg"))

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)


        layout1 = QHBoxLayout()
        button1 = QPushButton("Statistiques", self)
        layout1.addWidget(button1)


        layout.addWidget(self.pause_button)

        self.setLayout(layout)

        # Timer pour mise à jour des frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 ms = ~33 FPS

    def set_media(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawRect(QRect(100, 100, 50, 50))
        painter.end()

    def update_frame(self):
        if self.playing:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(q_img))
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Rejouer la vidéo

    def toggle_playback(self):
        self.playing = not self.playing
        self.pause_button.setText("Play" if not self.playing else "Pause")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer("08fd33_4.mp4")  # Remplace par ton fichier vidéo
    player.show()
    sys.exit(app.exec())
